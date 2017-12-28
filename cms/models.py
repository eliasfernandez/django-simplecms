# coding=utf-8
from mptt.models import MPTTModel, TreeForeignKey
from os import path, mkdir
from PIL import Image as PilImage
from django.db import models
from django.db.models.signals import pre_save
from django.conf import settings
from django.contrib.contenttypes.models import ContentType 
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _
from django.forms import CharField, EmailField, FileField, ChoiceField, Textarea, BooleanField
from cms.forms import CmsForm
from tinymce.models import HTMLField
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField
from easy_thumbnails.files import get_thumbnailer

default_options = {'size': (10000, 10000), 'crop': True}

class NonDeletedManager(models.Manager):
    "returns non deleted items"
    def get_query_set(self):
        return super(NonDeletedManager, self).get_query_set().filter(deleted=False)

class VisibleManager(models.Manager):
    "returns non deleted items"
    def get_query_set(self):
        return super(VisibleManager, self).get_query_set().filter(deleted=False, hidden=False)

class DeletedManager(models.Manager):
    def get_query_set(self):
        return super(DeletedManager, self).get_query_set().filter(deleted=True)


def get_pages_for_group(user_groups): 
    """
        Returns the pages associated with user_groups or None if is not defined.
    """
    if user_groups.exists():
        groups = user_groups.all()
    else:
        groups =[]
    
    return Page.objects.exclude(visible_for__in=Group.objects.exclude(pk__in = groups)).exclude(hidden=True)


def get_page_for_group(user_groups, slug): 
    """
        Returns a page associated with user_groups given a slug.
    """
    try:
        page = get_pages_for_group(user_groups).get( slug = slug)
    except Page.DoesNotExist:
        page = None

    return page
        



class Page(MPTTModel):
    
    """
        Page entity from which every content is hanging.
    """

    deleted = models.BooleanField(default=False, verbose_name=_(u"Remove"))
    hidden = models.BooleanField(default=False, verbose_name=_(u"Hide"))
    objects = NonDeletedManager()
    visible = VisibleManager()
    deleted_objects = DeletedManager()
    visible_for = models.ManyToManyField(Group, blank=True)

    name = models.CharField(max_length=255,  verbose_name=_("Name") )
    slug = models.SlugField( unique = True)
    subtitle =  models.CharField(max_length=255,  verbose_name=_("Subtitle"),null=True, blank=True )
    description =  models.CharField(max_length=255,  verbose_name=_("Description"),null=True, blank=True )
    image = FilerImageField(related_name ="image_page",blank=True,  null=True,help_text="Sube una imagen en jpg, gif y png, (800x600 max)")
    parent = TreeForeignKey('self', null=True, blank=True, verbose_name=_("Parent"), related_name=_("Children") )
    new_tab = models.BooleanField(verbose_name=_(u"Abrir en una nueva pestaña"), default=False)
    
#   meta
    meta_keywords =  models.CharField(max_length=255,  blank=True )
    meta_description =  models.CharField(max_length=255,  blank=True)
    meta_title =  models.CharField(max_length=255,  blank=True)
    
#    behaviour
    redirect_url = models.CharField(max_length=255,  blank=True) 
    

    def get_absolute_url(self):
        if(self.redirect_url != None and self.redirect_url != ''):
            return self.get_redirect_url()
        
        home_slug= settings.HOME_SLUG
        urlpieces = [self.slug,]
        c = self.parent
        
        while( c != None and c.slug != home_slug):
            urlpieces.append(c.slug)
            c = c.parent
            
                
        
        if len(urlpieces)>1:
            urlpieces.reverse()

        return '/%s/' % "/".join(urlpieces)
    
    def get_redirect_url(self):
        try:
            redirect_page = Page.objects.get(slug = self.redirect_url)
            return redirect_page.get_absolute_url()
        except Page.DoesNotExist:
            return self.redirect_url        
        
        
    
    def __unicode__(self):
        
        return self.name or u"-- Sin título --"

    def move_up(self):
        """
        move this item before previous item
        """

        prev_sibling = self.get_previous_sibling()
        if prev_sibling!=None: 
            self.move_to(prev_sibling,'left')
            self.save()
        
    def move_down(self):
        """
        move this item after next item
        """

        next_sibling = self.get_next_sibling()
        if next_sibling!=None: 
            self.move_to(next_sibling,'right')
            self.save()
        
        
    class Meta:
        verbose_name = u"página"
        verbose_name_plural = u"páginas"
        ordering=['tree_id','lft', 'level'   ]
        
    class MPTTMeta:
        parent_attr = 'parent'
        



class ContentModel(models.Model):
    deleted = models.BooleanField(default=False,  verbose_name=_(u"Remove") )
    hidden = models.BooleanField(default=False, verbose_name=_(u"Hide") )
    name =  models.CharField(max_length=100, null = True, blank = True)
    date_time_add = models.DateTimeField(auto_now_add = True, null = True, blank = True)
    date_time_update = models.DateTimeField(auto_now = True, null = True, blank = True)
    objects = NonDeletedManager()
    visible = VisibleManager()
    deleted_objects = DeletedManager()
    add_url = None
    admin_url = None

    def __delete__(self):
        self.deleted = True
        self.save()
    
    def __unicode__(self):
        return self.name or u'-Sin título-'
    
    class Meta:
        abstract=True
    
    def get_page(self):
       
        pagerelations = PageRelation.objects.filter(object_id=self.id, content_type=ContentType.objects.get_for_model(self))

        if len(pagerelations)>0:
            pr=pagerelations[0]
            return pr.page

        return None


    def get_absolute_url(self):

        page = self.get_page()
        if page:
            return page.get_absolute_url()

	return None

       
        


class Form(ContentModel):
    """
        Form content type
        field types:
        input, textarea, email, file, select,checkbox
        

    """
    content = models.TextField( help_text=_(u"Every line is a field ( Label|name=field_type|default text ) "),   verbose_name=_("Content") )
    to = models.TextField(  verbose_name=_("to"))
    
            
    class Meta:
        verbose_name = "formulario"
        verbose_name_plural = "formularios"
        
    @staticmethod
    def cms_prepare(content, request):
        lines = content.content.splitlines()
        formlist=[]
        form = CmsForm() # Create the form
        
        i = 0
        for line in lines:
            fields = line.split("|")
            
            if len(fields)>1:
                #@todo: detectar tipos de campo de formulario 
                w_type = fields[1].split("=")[1].replace(" ","").lower()
                name = fields[1].split("=")[0].replace(" ","")
                label = fields[0]
                if w_type=="input":
                    formlist.append([name, CharField(label=label)])   
                elif w_type=="textarea":
                    formlist.append([name, CharField(label=label, widget=Textarea)])                 
                elif w_type=="email":
                    formlist.append([name, EmailField(label=label)])  
                
                elif w_type=="file":
                    formlist.append([name, FileField(label=label)])   
            
                elif w_type=="select":
                    options = list()
                    i = 0;
                    for option in fields[2].split(';'):
                        options.insert(i, (option, option))
                        i = i +1
                    formlist.append([name, ChoiceField(label=label, choices=options)])
                elif w_type=="checkbox":
                    formlist.append([name, BooleanField(label='', help_text=label, required = False)])
                elif w_type=="*checkbox":
                    formlist.append([name, BooleanField(label='', help_text=label, required = True)])
                else:
                    formlist.append([name, CharField(label=label)])
                    
                if request.POST.has_key(name):
                    formlist[i][1].initial = request.POST[name] 
                i = i + 1

                    
        
        form.setFields(formlist)

        request.isvalidform = False
        if request.method == 'POST': # If the form has been submitted...

            form.setData(request.POST) # Set the form data
            form.validate(request.POST) # validate the from

            if form.is_valid(): # All validation rules pass 
               form.send(content.to.split(","))
               content.content = "Gracias"
               request.isvalidform = True
               return content # Redirect after POST

             
        content.form = form
        return content    

class List(ContentModel):
    """
       Html List, once per line
    """
    content = models.TextField( help_text="Cada linea es una viñeta",  verbose_name=_("Content"))
    is_ordered = models.BooleanField(default = False,  verbose_name=_("ordered list"))
    class Meta:
        verbose_name = "lista"
        verbose_name_plural = "listas"
        
    @staticmethod
    def cms_prepare(content, request):
        lines = content.content.split("\n")
        content.content =lines 
        return content

class Table(ContentModel):
    """
        Table content type
        cell 1 |  cell 2 |  cell 3
        cell 4 |  cell 5 |  cell 6

    """
    content = models.TextField( help_text=_(u"Every line is a row (cell 1| cell 2 | cell 3)"),  verbose_name=_(u"Table content"))
    has_header = models.BooleanField(default = False,verbose_name=_(u"has header"))
    
    class Meta:
        verbose_name = "table"
        verbose_name_plural = "tables"
    
    @staticmethod
    def cms_prepare(content, request):
        lines = content.content.split("\n")
        arr =[] 
        for line in lines:
            cells = line.split("|")
            if len(cells)>1:
                arr.append(cells) 
                
        content.content =arr 
        return content
    

class Filelist(ContentModel):
    """ 
        File list content
    """
    content = models.TextField( help_text=" Descripción del listado de archivos",verbose_name=_("Content"))

    class Meta:
        verbose_name = "File list"
        verbose_name_plural = "file lists"
        
    @staticmethod
    def cms_prepare(content, request):
        content.content= File.objects.filter(file_list=content.id)
        
        return content
 
    
class File(ContentModel):
    """
        File content type
    """
    
    #file_link = models.FileField( max_length=200, upload_to="uploads/", help_text="archivos pdf, doc, xls, etc...")
    file_link = FilerFileField(related_name ="file_content", blank=True,  null=True,help_text="Upload one file doc, xls, pdf, etc...")
    content = models.TextField( help_text=_(u" File Content"),verbose_name=_("Content"),  null=True, blank=True)
    file_list = models.ForeignKey(Filelist,  null=True, blank=True)
    order =models.PositiveSmallIntegerField("Position")


    def get_absolute_url(self):
        """ 
        Return the url for the file, 
        the url for the list of files or the
        generic url for the content model (the first available) 
        
        """

        file_url = settings.MEDIA_URL + str(self.file_link.url)
        filelist_url = self.file_list.get_absolute_url() if self.file_list else ""
        contentmodel_url = super(File, self).get_absolute_url()

        # otherwise return the url for its list of files or its content model url
        return (file_url or filelist_url or contentmodel_url or "")


    class Meta:
        verbose_name = "file"
        ordering = ['order']


class Image(ContentModel):
    """ 
        Image content type 
    """
    
    image = FilerImageField(related_name ="image_content", blank=True,  null=True,help_text="Upload a image file jpg, gif y png, (800x600 max)")
    caption = models.CharField(max_length=255,  null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    width = models.PositiveSmallIntegerField( blank=True,  null=True)
    height = models.PositiveSmallIntegerField( blank=True,  null=True)
    alt = models.CharField(max_length=100,  null=True, blank=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    
    @staticmethod
    def cms_prepare(content, request):
        img = content.image
        size =  [content.width,content.height]
        thumb = Image.thumbnail(img.url, size)
        content.image.thumb = thumb.url.split(settings.PROJECT_DIR)[1]
        content.width  = thumb.width
        content.height = thumb.height
        
        return content
    
    @staticmethod
    def thumbnail(image, size, crop = False): 
        
        thumbnailer = get_thumbnailer(path.join(settings.PROJECT_DIR, image[1:]))
        thumbnail = thumbnailer.get_thumbnail({ 'size':size, 'crop':crop });

        return thumbnail


    @staticmethod
    def scale(max_x, pair):
        x, y = pair
        new_y = (float(max_x) / x) * y
        return (int(max_x), int(new_y))
    class Meta:
        verbose_name = "image"
        verbose_name_plural = "images"


MAX_IMAGE_SIZE  = [10000,10000]
class Gallery(ContentModel):
    """
        Gallery content type
    """
    columns = models.PositiveSmallIntegerField(default= 0,verbose_name=_("Columns"))
    max_width = models.PositiveSmallIntegerField(blank=True,  null=True,verbose_name=_("max width"))
    max_height = models.PositiveSmallIntegerField( blank=True,  null=True,verbose_name=_("max height"))
    is_slider  = models.BooleanField(default = False,verbose_name=_("is slider"))
    lightbox  = models.BooleanField(default = False,verbose_name=_("lightbox"))
    crop  = models.BooleanField(default = False,verbose_name=_("Crop"))
    content = models.TextField()

    
    @staticmethod
    def cms_prepare(content, request):
        
        content.content= ImageFile.objects.filter(gallery=content.id)
        size = MAX_IMAGE_SIZE
        content.col_bootstrap = int(12 / content.columns)

        if content.max_width!=None and content.max_height !=None  :
            size =  [content.max_width,content.max_height]
         
        elif(content.max_width != None):
            size[0] = content.max_width

        elif(content.max_height!= None):
            size[1] = content.max_height
 
        
        for i in  range(len(content.content)) :  
            img = content.content[i].image
            thumb = Image.thumbnail(img.url, size, content.crop)
            content.content[i].thumbnail = thumb.url.split(settings.PROJECT_DIR)[1]
            content.content[i].width = thumb.width
            content.content[i].height =thumb.height
          
        return content

    
    class Meta:
        verbose_name = "Gallery"
  
class ImageFile(models.Model): 
    """
        Image content
    """
    image = FilerImageField(related_name ="image_imagefile",help_text="Upload and image file jpg, gif y png, (800x600 max)")
    #image = ImageField( max_length=200, upload_to="images/", help_text="Sube una imagen en jpg, gif y png, (800x600 max)")
    caption = models.CharField(max_length=255, null=True, blank=True,verbose_name=_("Caption"))
    alt = models.CharField(max_length=100,null=True, blank=True,verbose_name=_("alt")) 
    gallery = models.ForeignKey( Gallery,null=True, blank=True,verbose_name=_("gallery"))
    link = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "image file"
        verbose_name_plural = "image files"
    
    def get_absolute_url(self):
        if self.gallery:
            return self.gallery.get_absolute_url()
        else:
            return ""

class Text(ContentModel):
    """ 
        Rich text content
    """
    content = HTMLField(null=True, blank=True)
    class Meta:
        verbose_name = "texto"
        verbose_name_plural = "textos"

    
class Html(ContentModel):
    """
        Plain Html content
    """
    
    content = models.TextField()
    class Meta:
        verbose_name = _(u"html code")
        verbose_name_plural = _(u"html codes" )



class TextImage(ContentModel):
    """
        Text and image content
    """
    text_ptr_id = models.PositiveSmallIntegerField(default= 0,verbose_name=_("ptr_id"))
    image = FilerImageField(related_name ="textimage_content",null=True, blank=True,  help_text=_(u" Upload an image file jpg, gif y png, (800x600 max)"), default = None)
    content = HTMLField()
    class Meta:
        verbose_name = _(u"image and text")
        verbose_name_plural = _(u"image and text contents")

    @staticmethod
    def cms_prepare(content, request):

        # content.imageurl = get_thumbnailer(content.image.url).get_thumbnail(options).url
        content.content = {"text":content.content,"image":content.image.url}
        return content

    

    

pagerelation_limits = {
                            'model__in':('image','text','html','gallery','file','filelist','list','table','form','textimage'),
                            'app_label':'cms'
                        }




class PageRelation(models.Model):
    """
        Page and content relationship
    """
    page = models.ForeignKey(Page)
    content_type = models.ForeignKey(ContentType, limit_choices_to=pagerelation_limits)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    sorting = models.PositiveSmallIntegerField(default= 0)
    def __unicode__(self):
        pr_model  = self.content_type.model_class()
        pr_object = pr_model.objects.get(id=self.object_id)
        return pr_object.name

    

    class Meta:
        ordering = ['sorting']
        
    def save(self, *args, **kwargs):                 
      
        if self.id != None :
            pr = PageRelation.objects.get(id = self.id)
            if pr.content_type != self.content_type:
                pr_model  = pr.content_type.model_class()
                pr_object = pr_model.objects.get(id=self.object_id)
                pr_object.delete()

            
        
        super(PageRelation,self).save(*args, **kwargs)
