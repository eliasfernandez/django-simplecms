# coding = utf-8
# Create your views here.

from cms.models import PageRelation
from cms.models import Page
from cms.models import get_pages_for_group
from cms.utils.content import render
from django.conf import settings
from django.contrib.auth.models import Group

def get_page_from_slug(request):
    
    page = None

    slugpieces = request.path.split("/")
    slugpieces.pop()
    if len(slugpieces) == 1 and slugpieces[0]=='' :
    
        slug= settings.HOME_SLUG
        pages = get_pages_for_group(request.user.groups).filter(slug = slug)
        
        if(pages.count()==1):
            page=pages[0]

        slugpieces.pop()
    
    while len(slugpieces)>0:
    
        slug=slugpieces.pop()
        pages = get_pages_for_group(request.user.groups).filter(slug=slug)
    
        if(pages.count()==1):
            page=pages[0]
            break
    return page

def processor(request):
    #@todo: cache page objects for each url    
    if hasattr(request, "page"):
        page = request.page
    else:
        page = get_page_from_slug(request)   
    
    if page == None:
        return {}
        
    relations = PageRelation.objects.filter(page = page)
    contents = render (request,relations)
    return {'page':page, 'contents':contents}
