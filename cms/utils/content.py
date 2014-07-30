# coding=utf-8
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext,  Context, loader
from django import forms
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.template.base import TemplateDoesNotExist
from django.core.exceptions import ObjectDoesNotExist

_builtin_context_processors =  ('django.core.context_processors.csrf',)


def get_standard_processors():
    '''
    to avoid recursivity in the request context
    '''
    from django.conf import settings
    
    processors=[]
    collect = []
    contxtprocessors = list(settings.TEMPLATE_CONTEXT_PROCESSORS)
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
    def __init__(self, request, dict_=None, processors=None, current_app=None,
            use_l10n=None, use_tz=None):
        Context.__init__(self, dict_, current_app=current_app,
                use_l10n=use_l10n, use_tz=use_tz, autoescape=False)
        
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
    for field_name in obj._meta.get_all_field_names():
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
 
        field = obj._meta.get_field_by_name(field_name)[0]
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
    user = cntxt.get('user')
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
            cntxt.new()
            user_can_edit = user.has_perm("cms.change_"+ctype.model)   
            
            admin_links=[]
            
            if user_can_edit:
                admin_links.append( "<a title='editar' class='cms cms-edit' href='/admin/cms/%s/%s/'>Editar</a>" % (ctype.model, content.id) )
            
            cntxt.update(model_to_dict(content))
            cntxt.update(content.__dict__)

            cntxt.update({"ctype":ctype.model})
            content.html =  t.render(cntxt)
        
        except TemplateDoesNotExist:
            content.html =  _('There is no template asociated with %s content type '  )% ctype.model

        contents.append({'type':ctype.model, 'object': content })
        # if (ctype.model == 'textimage'):
        #     import ipdb; ipdb.set_trace()
    return contents

