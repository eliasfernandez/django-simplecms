from django import template
from django.apps import apps
from cms.utils.content import render
from cms.models import  PageRelation
from cms.models import  get_pages_for_group
import datetime

register = template.Library()

@register.tag(name="menu")
def do_menu(parser, token):
    try:
        bits = token.split_contents()
        
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires at less one argument" % token.contents.split()[0])
    
 
    if len(bits) == 2:
        return MenuNode(bits[1])
    elif len(bits) == 3:
        return MenuNode(bits[1], pk=bits[2] )
    elif len(bits) == 4:
        return MenuNode(bits[1], pk=bits[2] , current = bits[3] )


class MenuNode(template.Node):
    """template filter like {%menu cms.Page object.parent <current id> %}"""
    def __init__(self, model, **kwargs):
        self.model=model
        
        if kwargs.has_key("pk"):
            self.pid = kwargs['pk']
        
        if kwargs.has_key("current"):
            self.current = kwargs['current']
        
        
    def render(self, context):
        model = apps.get_model(*self.model.split('.'))
        if(hasattr(self,"pid")):
            pid=template.Variable(self.pid).resolve(context)
        else:
            pid = None
        user_groups = context["request"].user.groups

        nodes = get_pages_for_group(user_groups).filter(parent_id=pid)
        context['nodes'] = nodes
        if hasattr(self,"current"):
            context['current_menu'] = model.visible.get(pk = template.Variable(self.current).resolve(context) )
        elif context.has_key('object') and context['object']:
            context['current_menu'] = context['object']
            
        return ''
    

@register.inclusion_tag('cms/breadcrumb.html', takes_context=True)
def breadcrumb(context, page):
    tree = []
    current_page = page
    
    tree.append(current_page)
    while page.parent:
        if page.parent.hidden==False:
            tree.append(page.parent)
            
        page = page.parent

    tree.reverse()
    context.update({'tree' : tree, 'current_page': current_page})
    
    return context


# class BreadcrumbNode(template.Node):
#     def __init__(self, model, **kwargs):
#         self.model=model
#         if kwargs.has_key("pk"):
#             self.id = kwargs['pk']
        
#     def render(self, context):
#         model = get_model(*self.model.split('.'))
#         if(hasattr(self,"id")):
#             node = template.Variable(self.id).resolve(context)
#         else:
#             node = None

#         nodes = []
#         nodes.insert(0, node)
#         while node.parent:
#             node = node.parent
#             if not node.is_root_node():
#                 nodes.insert(0, node)
        
#         context['nodes'] = nodes
#         if context.has_key('object') and context['object']:
#             context['current_menu']=context['object']
            
#         return ''



@register.tag(name="content")
def do_content(parser, token):
    try:
        bits = token.split_contents()
        
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires at less one argument" % token.contents.split()[0])
    
    if len(bits) == 2:
        return ContentNode(bits[1])
    elif len(bits) == 3:
      
        return ContentNode(bits[1], pk=bits[2] )



class ContentNode(template.Node):
    def __init__(self, model, **kwargs):
        self.model=model
        if kwargs.has_key("pk"):
            self.pid = kwargs['pk']
        
        
    def render(self, context):
     
        if(hasattr(self,"pid")):
            pid=template.Variable(self.pid).resolve(context)
       
        #    items = parent.get_childrens()
        else:
            return
        
        nodes = PageRelation.objects.filter(pk=pid)
        contents = render(context['request'],nodes)
        
        context['nodes'] =contents
        return ''
        #return 'datetime.datetime.now().strftime(self.format_string)'
    
