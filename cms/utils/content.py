# coding=utf-8
from itertools import chain
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext,  Context, loader
from django import forms
try:
    from django.utils.module_loading import import_module

except ImportError:
    from django.utils.importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist
from django.core.exceptions import ObjectDoesNotExist

_builtin_context_processors =  ('django.template.context_processors.csrf',)


def get_standard_processors():
    '''
    to avoid recursivity in the request context
    '''
    from django.conf import settings
    
    processors=[]
    collect = []
    contxtprocessors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
    contxtprocessors = [x for x in contxtprocessors if x[0:3]<>'cms']
    collect.extend(contxtprocessors)
    collect.extend(_builtin_context_processors)
    for path in collect:
        i = path.rfind('.')
        module, attr = path[:i], path[i+1:]
        try:
            mod = import_module(module)
        except ImportError, e:
            raise ImproperlyConfigured('Error importing request processor module %s: "%s"' % (module, e))
        try:
            func = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (module, attr))
        processors.append(func)

    return tuple(processors)

class CmsRequestContext(Context):
    """
    Like RequestContext but without special processors
    """
    def __init__(self, request, dict_=None, use_l10n=None, use_tz=None):
    
        Context.__init__(self, dict_, use_l10n=use_l10n, use_tz=use_tz, autoescape=False)
        
        for prcssor in get_standard_processors():
            self.update(prcssor(request))

def model_to_dict(obj, exclude=['AutoField', 'ForeignKey', \
    'OneToOneField']):
    '''
        serialize model object to dict with related objects

        author: Vadym Zakovinko <vp@zakovinko.com>
        date: January 31, 2011
        http://djangosnippets.org/snippets/2342/
    '''
    tree = {}
    field_names = list(set(chain.from_iterable(
        (field.name, field.attname) if hasattr(field, 'attname') else (field.name,)
        for field in obj._meta.get_fields()
        if not (field.many_to_one and field.related_model is None)
    )))
    for field_name in field_names:
        try:
            field = getattr(obj, field_name)
        except (ObjectDoesNotExist, AttributeError):
            continue
 
        if field.__class__.__name__ in ['RelatedManager', 'ManyRelatedManager']:
            if field.model.__name__ in exclude:
                continue
 
            if field.__class__.__name__ == 'ManyRelatedManager':
                exclude.append(obj.__class__.__name__)
            subtree = []
            for related_obj in getattr(obj, field_name).all():
                value = model_to_dict(related_obj, \
                    exclude=exclude)
                if value:
                    subtree.append(value)
            if subtree:
                tree[field_name] = subtree
 
            continue
 
        field = obj._meta.get_field(field_name)
        if field.__class__.__name__ in exclude:
            continue
 
        if field.__class__.__name__ == 'RelatedObject':
            exclude.append(field.model.__name__)
            tree[field_name] = model_to_dict(getattr(obj, field_name), \
                exclude=exclude)
            continue
 
        value = getattr(obj, field_name)
        if value:
            tree[field_name] = value
 
    return tree
        
def render(request, relations):
    """

    Esta función se encarga de dado un listado de relaciones página objeto, 
    devolver el objeto y renderizarlo en la propiedad html teniendo en cuenta 
    todos los contextos excepto los que se crean en la app 'cms'
    
    """
    cntxt = CmsRequestContext(request)

    contents = []
    for rel in relations:
        
        ctype= rel.content_type
        model = ctype.model_class()
        
        if(hasattr(model,'cms_prepare')):
            content = model.cms_prepare( model.visible.get(pk = rel.object_id), request)
        #           
        else:
            
            content = model.visible.get(pk = rel.object_id)
                
         
        try:
            t = loader.select_template(("cms/custom/%s.html"% rel.id,"cms/custom/page_%s_%s.html"% (rel.page_id, rel.content_type.model), "cms/%s.html" % ctype.model))    
            
            cntxt = model_to_dict(content)
            #cntxt.update(content.__dict__)
            cntxt["ctype"]=ctype.model

            content.html =  t.render(cntxt)
        
        except TemplateDoesNotExist:
            content.html =  _('There is no template asociated with %s content type '  )% ctype.model

        contents.append({'type':ctype.model, 'object': content })
    return contents

