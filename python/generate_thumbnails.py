#!/usr/bin/env python

import image_processing
import argparse
import photodb
import sys, os

def create_thumbnails(db):
    for gallery in db.galleries():
        num_images = len(gallery['photos'])
        for i, photo in enumerate(gallery['photos']):
            sys.stdout.write('\r%s: %3.0f%%' % (gallery['title'], float(i) / num_images * 100))
            sys.stdout.flush()
#        ThumbnailCreator.start().proxy().create_thumbnail(
            create_thumbnail(
                os.path.join(gallery['root_dir'], gallery['gallery_dir'], photo['path']),
                os.path.join(gallery['thumbnails_dir'], 'small', photo['path']),
                277, 200)
        print '\r%s: 100%%' % gallery['title']

#class ThumbnailCreator(pykka.ThreadingActor):
def create_thumbnail(image_path, target_image, width, height):
    try:
        image_processing.create_thumbnail(
            image_path, target_image, width, height, mkdir=True)
    except Exception as e:
        print e
#    finally:
#        self.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('db_file')
    args = parser.parse_args()

    db = photodb.PhotoDB(args.db_file)    
    create_thumbnails(db)
