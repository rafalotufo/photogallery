import web
import json
import photodb
import os
import sys
import image_processing

urls = (
    '/galleries', 'galleries',
    '/galleries/(.*)/photos/(.*)', 'images',
    '/galleries/(.*)/thumbnails/(.*)', 'thumbnails',
    '/galleries/(.*)', 'galleries'
)

def media_ext(path):
    return os.path.splitext(path)[1].lower().strip('.')
def media_type(path):
    ext = media_ext(path)
    if ext in ['jpg', 'jpeg', 'gif', 'png']:
        return 'image'
    if ext in ['mov', 'mp4', 'ogg']:
        return 'video'

class galleries:
    def GET(self, gallery_id=None):
        if gallery_id is None:
            return json.dumps(web.db.list_galleries())
        else:
            # gallery_id = web.input()['gallery-id']
            web.header('Content-Type', 'application/json')
            gallery = web.db.load_gallery(gallery_id)
            if gallery:
                photos = list({
                    'name': photo['path'], 
                    'gallery_id': gallery_id,
                    'path': photo['path'],
                    'type': media_type(photo['path']),
                    'ext': media_ext(photo['path']),
                    'index': i,
                    'favorite': photo.get('favorite', False)
                } for i,photo in enumerate(gallery['photos']))
                return json.dumps(photos)

class images:
    def POST(self, gallery_id, name):
        data = json.loads(web.data())
        web.db.update_image_metadata(gallery_id, name, data)

    def GET(self, gallery_id, name):
        ext = name.split(".")[-1].lower() # Gather extension

        cType = {
            "png":"images/png",
            "jpg":"images/jpeg",
            "gif":"images/gif",
            "ico":"images/x-icon"            
        }

        path = web.db.image_path(gallery_id, name)
        # web.header("Content-Type", cType[ext]) # Set the Header
        f = None
        try:
            f = open(path['src'], 'rb') # Notice 'rb' for reading images
        except IOError:
            image_processing.resize_image(
                path['original'], path['src'], 1024, 780, mkdir=True)
            f = open(path['src'], 'rb') # Notice 'rb' for reading images
        finally:
            if f:
                return f.read()
            else:
                raise web.notfound()

class thumbnails:
    def GET(self, gallery_id, name):
        print 'here'
        ext = name.split(".")[-1].lower() # Gather extension

        cType = {
            "png":"images/png",
            "jpg":"images/jpeg",
            "gif":"images/gif",
            "ico":"images/x-icon"            
        }

        path = web.db.thumbnail_image_path(gallery_id, name)
        print path
        # if True or name in os.listdir('images'):  # Security
        try:
            # web.header("Content-Type", cType[ext]) # Set the Header
            return open(path, 'rb').read() # Notice 'rb' for reading images
        except:
            raise web.notfound()


if __name__ == "__main__":
    dbpath = sys.argv[2]
    web.app = web.application(urls, globals())
    web.db = photodb.PhotoDB(dbpath)
    print web.db.list_galleries()
    web.app.run()
