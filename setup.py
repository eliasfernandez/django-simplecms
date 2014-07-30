# coding=utf-8
from distutils.core import setup
import cms

long_description = open('README.md').read()

setup(
            name='django-simplecms',
            version=cms.VERSION,
            packages=['cms',
                      'cms.context_processors',
                      'cms.templatetags',
                      'cms.utils',
            ],
            package_data={
                'cms': ['static/*', "templates/*"]
            },
            description='A Django app for cms purposes that covers 90% of tasks you need from a cms',
            long_description=long_description,
            author='Elías Fernández',
            author_email='eliasfernandez@gmail.com',
            license='BSD License',
            url='http://github.com/eliasfernandez/django-simplecms',
            platforms=["any"],
            install_requires=[
              "Django",
              "PIL",
              "django-mptt",
              "django-tinymce",
              "django-suit",
              "django-filer"
            ],
            classifiers=[
                       'Development Status :: 4 - Beta',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: BSD License',
                       'Natural Language :: English (mostly)',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python',
                        ],
        )
