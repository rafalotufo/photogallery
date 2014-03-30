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

    def image_path(self, gallery_id, filename):
        galleries = self.load_gallery(gallery_id)
        if galleries:
            gallery = galleries
            return {
                'src': os.path.join(
                    gallery['root_dir'], gallery['thumbnails_dir'], 'large', filename),
                'original': os.path.join(gallery['root_dir'], gallery['gallery_dir'], filename)
            }
        else:
            return 'file-not-found'

    def thumbnail_image_path(self, gallery_id, filename):
        galleries = self.load_gallery(gallery_id)
        if galleries:
            gallery = galleries
            return os.path.join(gallery['thumbnails_dir'], 'small', filename)
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
            'gallery_dir': gallery_dir,
            'thumbnails_dir': thumbnails_dir,
            'photos': [],
            'tags': tags,
            'uuid': uuid.uuid1().hex
        }
        for filename in os.listdir(os.path.join(root_dir, gallery_dir)):
            ext = os.path.splitext(filename)[1]
            if ext.lower() in ['.jpg', '.jpeg', '.gif', '.png', '.mov', 'mp4']:
                path = filename.replace(gallery_dir, '')
                gallery['photos'].append({
                    'path': path
                })
        self.db.table('gallery').insert(gallery)
        self.gallery_cache[gallery['uuid']] = gallery
        return gallery

# def update_gallery(db, gallery_id, title=None, tags=None):
#     db.table('gallery').remove(where('uuid') == gallery_id)
#     add_gallery(db, gallery_dir, title, tags)

    def update_image_metadata(self, gallery_id, name, data):
        gallery = self.load_gallery(gallery_id)
        for i,item in enumerate(gallery['photos']):
            if item['path'] == name:
                break
        image = gallery['photos'][i]
        for name, val in data.iteritems():
            image[name] = val
        gallery['photos'][i] = image
        self.db.table('gallery').remove(where('uuid') == gallery_id)
        self.db.table('gallery').insert(gallery)
        self.gallery_cache[gallery['uuid']] = gallery

    def load_gallery(self, gallery_id):
        if gallery_id not in self.gallery_cache:
            galleries = self.db.table('gallery').search(where('uuid') == gallery_id)
            if galleries:
                self.gallery_cache[gallery_id] = galleries[0]
            else:
                return None
        return self.gallery_cache[gallery_id]

    def list_galleries(self):
        def is_image(filename): 
            ext = os.path.splitext(filename)[1]
            return ext.lower() in ['.jpg', '.jpeg', '.gif', '.png']
        def first_image(gallery):
            return next(x for x in gallery['photos'] if is_image(x['path']))
        return [{
            'gallery_id': gallery['uuid'],
            'name': gallery['title'],
            'thumbnail': first_image(gallery)['path'],
            'tags': gallery['tags']
        } for gallery in self.db.table('gallery').all()]

    def galleries(self):
        return self.db.table('gallery').all()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dbfile')
    parser.add_argument('gallery_dir')
    args = parser.parse_args()

    photodb = PhotoDB(args.dbfile)
    photodb.add_gallery(args.gallery_dir)
