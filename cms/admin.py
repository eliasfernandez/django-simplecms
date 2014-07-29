#coding=utf-8

from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import  HttpResponse
from django.utils.html import escape, escapejs
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.forms import TextInput

from django.conf.urls import patterns
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.forms.models import BaseInlineFormSet
from django.utils.text import  capfirst
from django.forms import ModelForm

from django.core.urlresolvers import reverse_lazy

from cms.models import *



class ContentAdmin(admin.ModelAdmin):
    " Class from which all the content type classes inherit "
    exclude = ["deleted",]

    def get_model_perms(self, *args, **kwargs):
        perms = admin.ModelAdmin.get_model_perms(self, *args, **kwargs)
        perms['list_hide'] = True
        return perms
   
    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        pk_value = obj._get_pk_val()
        if "_popup" in request.POST:
            return HttpResponse(
                '<!DOCTYPE html><html><head><title></title></head><body>'
                '<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script></body></html>' % (escape(pk_value), escapejs(obj)))
        return super(ContentAdmin, self).response_change(request, obj)

    class Media:
        js = (
                '/static/admin/js/genericcollection.js',
                '/static/admin/js/jquery.tablednd.js',
                )
    

class ContentMceAdmin(ContentAdmin):
    class Media:
        js = ('/static/tiny_mce/tiny_mce.js',)


class ImageAdmin(ContentAdmin):
     fieldsets = (
         (None, {
             'fields': ('image',('name','caption','alt'),('width','height'),'content' )
         }),
         ('Optional data', {
             'classes': ('collapse','extrapretty'),
             #'classes': ('grp-collapse','grp-closed'),
             'fields': ('hidden','link')
         }),
     ) 

admin.site.register(Image, ImageAdmin)
admin.site.register(Html, ContentAdmin)

admin.site.register(Text, ContentMceAdmin)
admin.site.register(TextImage, ContentMceAdmin)
admin.site.register(Form, ContentAdmin)
admin.site.register(Table, ContentMceAdmin)
admin.site.register(List, ContentAdmin)


class FileAdmin(ContentMceAdmin):
    exclude = ('file_list','deleted',)

admin.site.register(File, FileAdmin)

class PageRelationForm(ModelForm):
    fields=['content_type', 'object_id', 'sorting']
    readonly_fields = ["content_type",]
    
    class Meta:
        model = PageRelation
        

class BaseFormSet(BaseInlineFormSet):

    def _construct_form(self, i, **kwargs):
        form = super(BaseFormSet, self)._construct_form(i, **kwargs)
        has_instance  = form.initial.has_key("content_type")
        if has_instance:
            field = form.fields.get('content_type')
            field.widget.attrs["disabled"] = "disabled"
        
        return form
     
      


class PageRelationInline(admin.options.InlineModelAdmin):
    """
    Inline content admin from page form
    """
    verbose_name = _(u"Page content")
    verbose_name_plural = _(u"Page contents")
    model = PageRelation
    extra = 0 
    fields = ( "sorting",'content_type','object_id')
     
    formset = BaseFormSet


    # define the sortable
    sortable_field_name = "sorting"
    ct_field = "content_type"
    ct_fk_field = "object_id"
    template = 'admin/edit_inline/tabular.html'

    
    def __init__(self, parent_model, admin_site):
       
        super(PageRelationInline, self).__init__(parent_model, admin_site)
        ctypes = ContentType.objects.all().order_by('id').values_list('id', 'app_label','model')
        elements = ["%s: '%s/%s'" % (id, app_label, model) for id, app_label, model in ctypes]
        self.content_types = "{%s}" % ",".join(elements)
   
    def get_formset(self, request, obj=None):
        result = super(PageRelationInline, self).get_formset(request, obj)
        result.form = PageRelationForm
        result.content_types = self.content_types
        result.ct_fk_field = self.ct_fk_field
        result.ct_field = self.ct_field
        result.sortable_field_name = self.sortable_field_name
        return result

    
 
class PageAdmin(admin.ModelAdmin):
    " Main page admin "
    
    exclude = ["deleted",]    
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('hidden', 'name','slug', 'subtitle', 'description', 'new_tab', 'parent')
        }),
        ('Optional data', {
            'classes': ('collapse','extrapretty'),
            
            'fields': ('image','meta_title','meta_description','meta_keywords','redirect_url', 'visible_for')
        }),
    )
    list_display = ('get_name', 'slug',  'move','published')
    search_fields = ('name', )
    list_per_page = 1000
    inlines = [PageRelationInline,]
    
    def get_name(self, obj):
        return u"<span style='padding-left:%spx;'>  %s </span>" %(obj.level*15, obj.name)
    
    get_name.allow_tags=True

    def published(self, obj,allow_tags=True):
        if(obj.hidden==False):
           
            return mark_safe(u"<img src='/static/admin/img/icon-yes.gif' />")
        else:
            return mark_safe(u"<img src='/static/admin/img/icon-no.gif' />")
    
    published.allow_tags=True    
    
    def move(self, obj):
        """
        Returns html with links to move_up and move_down views.
        """
        button = u'<a href="%s" class="sortable" ><i class="icon-arrow-%s icon-alpha5"></i></a>'
        
        prefix =getattr(settings, 'STATIC_URL')
        
        
        html = "<div class='inline-sortable'>"
        link = '%d/move_up/' % obj.pk
        html += button % (link,  'up') + "  "
        link = '%d/move_down/' % obj.pk
        html += button % (link,  'down')
        html +="</div>"

        return html
    move.allow_tags = True
    move.short_description = ugettext_lazy('Move')
    
    def get_urls(self):
        admin_view = self.admin_site.admin_view
        urls = patterns('',
            (r'^(?P<item_pk>\d+)/move_up/$', admin_view(self.move_up)),
            (r'^(?P<item_pk>\d+)/move_down/$', admin_view(self.move_down)),
        )
        return urls + super(PageAdmin, self).get_urls()

    def move_up(self, request, item_pk):
        """
        (change ordering) of the page with
        id=``item_pk``.
        """
        if self.has_change_permission(request):
            item = get_object_or_404(Page, pk=item_pk)
            item.move_up()
        else:
            raise PermissionDenied
        return redirect('admin:cms_page_changelist')

    def move_down(self, request, item_pk):
        """
        (change ordering) of the page with
        id=``item_pk``.
        """
        if self.has_change_permission(request):
            item = get_object_or_404(Page, pk=item_pk)
            item.move_down()
        else:
            raise PermissionDenied
        return redirect('admin:cms_page_changelist')
    
    class Media:
        js = (
                '/static/admin/js/genericcollection.js',
                '/static/admin/js/jquery.tablednd.js',
                )
        
        css = {
                'all':('/static/admin/css/page.css',)  
             }
        
admin.site.register(Page,PageAdmin)


class ImageFileInline(admin.TabularInline):
    fieldsets = (
        (None, {
            'fields': ('image',('caption','alt'),'link' )
        }),
    )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'30'})},
    }
    model = ImageFile    
    extra = 1

class GalleryAdmin(ContentAdmin):
    inlines = [ImageFileInline,] 
    fieldsets = (
        (None, {
            'fields': ('name',('max_width','max_height','columns'),('is_slider', 'lightbox', 'crop') )
        }),
        ('Optional data', {
            'classes': ('grp-collapse','grp-closed',),
            'fields': ('hidden',)
        }),
    )   
    
admin.site.register(Gallery,GalleryAdmin)


class FileInline(admin.TabularInline):
    fieldsets = (
        (None, {
            'fields': ('name','file_link','order' )
        }),
        ('Optional data', {
            #'classes': ('grp-collapse','grp-closed',),
            'classes': ('collapse','extrapretty'),
            'fields': ('hidden', 'content')
        }),
    )
    sortable_field_name = "order"
    model = File
    extra = 0

class FilelistAdmin(ContentAdmin):
    fieldsets = (
        (None, {
            'fields': ('name','hidden')
        },),
    )
    inlines = [FileInline,]  
    
admin.site.register(Filelist,FilelistAdmin)


