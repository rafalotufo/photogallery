from PIL import Image, ImageOps
import os

def create_thumbnail(source_image, target_image, width, height, mkdir=False):
    size = width, height

    if mkdir:
        try:
            os.makedirs(os.path.dirname(target_image))
        except:
            pass
    # target_image = os.path.splitext(infile)[0] + ".thumbnail"
    if source_image != target_image:
        try:
            im = Image.open(source_image)
            thumb = ImageOps.fit(im, size, Image.ANTIALIAS)
            thumb.save(target_image, "JPEG")
        except IOError as e:
            print e
            print "cannot create copy for '%s'" % source_image

def resize_image(source_image, target_image, width, height, mkdir=False):
    if source_image != target_image:
        if mkdir:
            try:
                os.makedirs(os.path.dirname(target_image))
            except:
                pass
        try:
            img = Image.open(source_image)
            wpercent = (width/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((width,hsize), Image.ANTIALIAS)
            img.save(target_image)
        except IOError as e:
            print e
            print "cannot create copy for '%s'" % source_image