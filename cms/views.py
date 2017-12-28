# coding = utf-8
# Create your views here.
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404

from cms.models import *
from cms.models import get_page_for_group
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext, loader
from django import forms
from django.template import TemplateDoesNotExist


def show(request, slug):
    
    slugpieces = slug.split("/")
    if len(slugpieces) > 1:
        slug = slugpieces[-1]
  
    user_groups = request.user.groups
    page = get_page_for_group(user_groups, slug)
    
    if page is None:
        raise Http404

    request.page = page
    
    try:
        template_backend = loader.select_template(("cms/custom/page_%s.html" % page.id, "cms/page.html"))

    except TemplateDoesNotExist:
        content.html =  _('There is no template asociated with page')

    return render(request, template_backend.template.name)



        
        
