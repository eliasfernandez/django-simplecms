# django-simplecms


Tool to include a basic cms which can create pages hierarchy with "n" associated contents for each one. The content type included are:

* Text
* Text and image
* Image
* Gallery
* List 
* Table 
* Html
* Form
* File
* File list 
  

## Requirements and installation


It requires:

* Django == 1.11
* PIL
* mptt
* tinymce
* suit
* filer


You can try it without django suit but it is highly recommendable. To install simply use

	pip install git+https://github.com/eliasfernandez/django-simplecms

...


## Configuration

### settings.py

Context processor must be loaded in a required order for cms to work. `cms` depends on `mptt`, `suit` depends on `cms` and `django.contrib.admin` relies on `suit`. A working order could be like this:

    INSTALLED_APPS = [
        ...
        'easy_thumbnails',
        'mptt',
        'cms',
        'suit',
        'filer',
        'django.contrib.admin',
        'web',
        ...
        ]

#### Template context processor

On the last line just add `cms.context_processors.page.processor` it will be the responsible of the hierarchy between the different elements.

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    ...
                    'cms.context_processors.page.processor',
                ],
            },
        },
    ]

#### Other variables

`settings.HOME_SLUG` will be used as a proxy for the first page on the pagetree.

### urls.py
Just add a line including the cms urls module.

    urlpatterns = [
        ...
        url(r'^', include('cms.urls')), 
    ]

## Initial data

For the structure to be created just migrate the cms app to the database structure:

    $: python manage.py migrate cms

Since that moment, you can start creating cms contents. 

Enjoy and give me some feedback
