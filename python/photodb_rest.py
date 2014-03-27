import web
import json
import photodb
import os
import sys

urls = (
    '/galleries', 'galleries',
    '/photos', 'photos',
    '/images/(.*)', 'images',
    '/thumbnails/(.*)', 'thumbnails',
)

class galleries:
    def GET(self):
        return json.dumps(web.db.list_galleries())

class photos:
    def GET(self):
        def media_ext(path):
            return os.path.splitext(path)[1].lower().strip('.')
        def media_type(path):
            ext = media_ext(path)
            if ext in ['jpg', 'jpeg', 'gif', 'png']:
                return 'image'
            if ext in ['mov', 'mp4', 'ogg']:
                return 'video'

        gallery_id = web.input()['gallery-id']
        web.header('Content-Type', 'application/json')
        gallery = web.db.load_gallery(gallery_id)
        if gallery:
            photos = list({
                'name': 'sasf', 
                'path': os.path.join('/', gallery_id, photo['path']),
                'type': media_type(photo['path']),
                'ext': media_ext(photo['path']),
                'index': i
            } for i,photo in enumerate(gallery[0]['photos']))
            return json.dumps(photos)

class images:
    def GET(self,name):
        ext = name.split(".")[-1].lower() # Gather extension

        cType = {
            "png":"images/png",
            "jpg":"images/jpeg",
            "gif":"images/gif",
            "ico":"images/x-icon"            
        }

        path = web.db.image_path(name)
        if True or name in os.listdir('images'):  # Security
            # web.header("Content-Type", cType[ext]) # Set the Header
            return open(path,"rb").read() # Notice 'rb' for reading images
        else:
            raise web.notfound()

class thumbnails:
    def GET(self,name):
        ext = name.split(".")[-1].lower() # Gather extension

        cType = {
            "png":"images/png",
            "jpg":"images/jpeg",
            "gif":"images/gif",
            "ico":"images/x-icon"            
        }

        path = web.db.thumbnail_image_path(name)
        # if True or name in os.listdir('images'):  # Security
        try:
            # web.header("Content-Type", cType[ext]) # Set the Header
            return open(path,"rb").read() # Notice 'rb' for reading images
        except:
            raise web.seeother('/static/img/loading.gif')


if __name__ == "__main__":
    dbpath = sys.argv[2]
    web.app = web.application(urls, globals())
    web.db = photodb.PhotoDB(dbpath)
    print web.db.list_galleries()
    web.app.run()
