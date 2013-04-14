from django.forms import ModelForm, ValidationError
from models import Board, Thread, Post
import re

class threadForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(threadForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = True
        
    class Meta:
        model = Post
        exclude = ("datetime","thread")
	def clean_email(self):
		cleaned_data = self.cleaned_data
		email = cleaned_data.get("email")
		if(email == "noko" or email == "sage" or (re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None) or email == ""):
			return cleaned_data
		else:
			self._errors["email"] = self.error_class([u'Email must be blank, valid, noko or sage.'])
		return cleaned_data

class postForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(postForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = Post
        exclude = ("datetime","thread")

    def clean(self):
		cleaned_data = self.cleaned_data
		comment = cleaned_data.get("comment")
		image = cleaned_data.get("image")
		email = cleaned_data.get("email")
		if(email == "noko" or email == "sage" or (re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None) or email == ""):
			pass
		else:
			self._errors["email"] = self.error_class([u'Email must be blank, valid, noko or sage.'])
		if(comment or image):
			return cleaned_data
		else:
			self._errors["comment"] = self.error_class([u'You must post an image AND/OR a comment.'])
		return cleaned_data
