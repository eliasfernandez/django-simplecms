from django import template
from os import  mkdir, path
from django.conf import settings
from PIL import Image

register = template.Library()


SCALE_WIDTH = 'w'
SCALE_HEIGHT = 'h'
@register.filter(name="thumbnail")
def do_thumbnail(image, arg="100x100"):

    original_image_path = image.path
    if not original_image_path:  
        return ''  
        
    size = arg
    
    if (size.lower().endswith('h')):
        mode = 'h'
    else:
        mode = 'w'
    
        
    size = arg.split("x")
    
    # defining the size  
    max_size = int(size[0])
    
    # defining the filename and the miniature filename  
    basename, format = original_image_path.rsplit('.', 1)  
    basename, name = basename.rsplit(path.sep, 1)  

    miniature = name + '_' + str(max_size) + mode + '.' + format
    thumbnail_path = settings.MEDIA_ROOT+path.join(basename, settings.THUMBNAILS_PATH) 
    
    if not path.exists(thumbnail_path):  
        mkdir(thumbnail_path)  
    
    miniature_filename =path.join(thumbnail_path, miniature)  
    miniature_url = '/'.join((settings.MEDIA_URL[:-1], miniature_filename[ (len(settings.MEDIA_ROOT)) :] ))
    #import ipdb; ipdb.set_trace()
    
    # if the image wasn't already resized, resize it  
    if not path.exists(miniature_filename) or path.getmtime(settings.MEDIA_ROOT+original_image_path) > path.getmtime(miniature_filename):
        image = Image.open(settings.MEDIA_ROOT+original_image_path)  
        image_x, image_y = image.size  
        
        if mode == 'h':
            image_y, image_x = scale(max_size, (image_y, image_x))
        else:
            image_x, image_y = scale(max_size, (image_x, image_y))
            
        
        image = image.resize((image_x, image_y), Image.ANTIALIAS)
              
        image.save(miniature_filename, image.format)  

    return miniature_url    

register.filter('thumbnail', do_thumbnail)

def scale(max_x, pair):
        x, y = pair
        new_y = (float(max_x) / x) * y
        return (int(max_x), int(new_y))