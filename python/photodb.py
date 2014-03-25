#!/usr/bin/env python

import os
import argparse
from tinydb import TinyDB, where
import uuid
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware, ConcurrencyMiddleware

class PhotoDB:
    def __init__(self, db_file_path):
        # self.cachingMiddleware = CachingMiddleware(JSONStorage)
        # self.concurrentMiddleware = ConcurrencyMiddleware(self.cachingMiddleware)
        self.concurrentMiddleware = ConcurrencyMiddleware(JSONStorage)
        self.db = TinyDB(db_file_path, storage=self.concurrentMiddleware)
        self.gallery_cache = {}

    def image_path(self, image_id):
        gallery_id, filename = os.path.split(image_id)
        gallery_id = gallery_id.strip('/')
        galleries = self.load_gallery(gallery_id)
        if galleries:
            gallery = galleries[0]
            return os.path.join(gallery['images_dir'], filename)
        else:
            return 'file-not-found'

    def thumbnail_image_path(self, image_id):
        gallery_id, filename = os.path.split(image_id)
        gallery_id = gallery_id.strip('/')
        galleries = self.load_gallery(gallery_id)
        if galleries:
            gallery = galleries[0]
            return os.path.join(gallery['thumbnails_dir'], filename)
        else:
            return 'file-not-found'

    def add_gallery(self, root_dir, gallery_dir, thumbnails_dir=None, title=None, tags=None):
        '''Creates an entry in db with the contents of all image files in gallery_dir'''
        ## check if gallery already exists
        existing_gallery = self.db.table('gallery').search(where('root_dir') == gallery_dir)
        if existing_gallery:
            raise Exception('gallery already exists')

        if title is None: title = gallery_dir
        if tags is None: tags = []
        if thumbnails_dir is None: thumbnails_dir = os.path.join(gallery_dir, '.thumbnails')
        gallery = {
            'title': title,
            'root_dir': root_dir,
            'images_dir': gallery_dir,
            'thumbnails_dir': thumbnails_dir,
            'photos': [],
            'tags': tags,
            'uuid': uuid.uuid1().hex
        }
        for filename in os.listdir(gallery_dir):
            ext = os.path.splitext(filename)[1]
            if ext.lower() in ['.jpg', '.jpeg', '.gif', '.png']:
                gallery['photos'].append({
                    'path': filename.replace(gallery_dir, '')
                })
        self.db.table('gallery').insert(gallery)
        self.gallery_cache[gallery['uuid']] = gallery
        return gallery

# def update_gallery(db, gallery_id, title=None, tags=None):
#     db.table('gallery').remove(where('uuid') == gallery_id)
#     add_gallery(db, gallery_dir, title, tags)

    def load_gallery(self, gallery_id):
        return self.gallery_cache.setdefault(
            gallery_id,
            self.db.table('gallery').search(where('uuid') == gallery_id))

    def list_galleries(self):
        return [{
            'galleryId': gallery['uuid'],
            'name': gallery['title'],        
        } for gallery in self.db.table('gallery').all()]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dbfile')
    parser.add_argument('gallery_dir')
    args = parser.parse_args()

    photodb = PhotoDB(args.dbfile)
    photodb.add_gallery(args.gallery_dir)