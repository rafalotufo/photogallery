import os
import argparse
import photodb
import pykka
import image_processing

def import_gallery_from_disk(db, root_dir, gallery_dir, root_thumbnails_dir):
    path, gallery_folder = os.path.split(gallery_dir)
    title = gallery_folder
    gallery_dir = gallery_dir.replace(root_dir, '')
    def split_names(path):
        head, tail = os.path.split(path)
        if head and tail:
            return split_names(head) + [tail]
        else:
            return [tail]

    tags = split_names(path)
    thumbnails_dir = os.path.join(root_thumbnails_dir, gallery_dir)
    gallery = db.add_gallery(
        os.path.abspath(root_dir),
        gallery_dir,
        thumbnails_dir,
        title,
        tags)
    print 'Created gallery %s' % gallery['title']

def create_thumbnails(db):
    for gallery in db.galleries():
        for photo in gallery['photos']:
#        ThumbnailCreator.start().proxy().create_thumbnail(
            create_thumbnail(
                os.path.join(gallery['root_dir'], gallery['images_dir'], photo['path']),
                os.path.join(gallery['thumbnails_dir'], photo['path']),
                277, 200)

#class ThumbnailCreator(pykka.ThreadingActor):
def create_thumbnail(image_path, target_image, width, height):
    print image_path, target_image
    try:
        image_processing.create_thumbnail(
            image_path, target_image, width, height, mkdir=True)
    except Exception as e:
        print e
#    finally:
#        self.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('gallery_list')
    parser.add_argument('root_dir')
    parser.add_argument('db_file')
    parser.add_argument('root_thumbnails_dir')
    args = parser.parse_args()

    gallery_list = map(lambda f: f.strip(), open(args.gallery_list).readlines())
    db = photodb.PhotoDB(args.db_file)    
    for gallery_dir in gallery_list:
       import_gallery_from_disk(db, args.root_dir, gallery_dir, args.root_thumbnails_dir)
    # create_thumbnails(db)
