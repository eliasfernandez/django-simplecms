from django.forms import ValidationError, Form
from django.core.mail import send_mail
from django.conf import settings


class CmsForm(Form):    
    """
    http://djangosnippets.org/snippets/714/
    Dynamic form that allows the user to change and then verify the data that was parsed
    """
    def setFields(self, kwds):
        """
        Set the fields in the form
        """
        #keys = kwds.keys()
        #keys.sort()
        self.listfields = kwds
        for k in kwds:
            self.fields[k[0]] = k[1]
            
    def setData(self, kwds):
        """
        Set the data to include in the form
        """
        keys = kwds.keys()

        for k in keys:
            self.data[k] = kwds[k]
            
    def is_valid(self):
        return len(self.errors)==0
    
    def send(self, to_list):
        content_fields = {}
        for name,field in self.cleaned_data.items():
            content_fields[name] = field
        content = ""
        for field in self.listfields:
            if field[0] in content_fields and isinstance(content_fields[field[0]], str):
                content += field[0] + ":" + content_fields[field[0]] + "\n"
        if(self.cleaned_data.has_key('subject')):
            subject = self.cleaned_data['subject']
        else:
            subject =  self.cleaned_data.values()[0]

        send_mail(subject, content, settings.DEFAULT_FROM_EMAIL, to_list)
                
    def validate(self, post):
        """
        Validate the contents of the form
        """
        self.cleaned_data = {}
        for name,field in self.fields.items():
            try:
                if post.has_key(name):
                    self.cleaned_data[name] = field.clean(post[name])
                else:

                    if field.required :
                        raise ValidationError(
                            'Este campo es obligatorio.',
                            code='required'
                        )
                    
            except ValidationError, e:
                self.errors[name] = e.messages
                
                
                
                
                
                
                
                
