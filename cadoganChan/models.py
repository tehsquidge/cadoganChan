from django.db import models
from django.utils.timezone import now as utcnow
import os
import uuid

# Create your models here.

def get_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('cadoganChan/images/uploads', filename)
    
class Board(models.Model):
	id = models.CharField(max_length=3,unique=True,primary_key=True)
	name = models.CharField(max_length=32)
	
	def __unicode__(self):
		return self.id
	
class Thread(models.Model):
	board = models.ForeignKey(Board)
	stickied = models.BooleanField()
	locked = models.BooleanField()
	last_updated = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return unicode(self.id)
	
class Post(models.Model):
	name = models.CharField(max_length=32,blank=True)
	thread = models.ForeignKey(Thread)
	datetime = models.DateTimeField(default=utcnow)
	email = models.CharField(max_length=32,blank=True) #this will be validated later... for sage and noko and shit
	subject = models.CharField(max_length=32,blank=True)
	comment = models.TextField(blank=True)
	image = models.ImageField(upload_to=get_image_path,blank=True)
	def __unicode__(self):
		return unicode(self.id)

