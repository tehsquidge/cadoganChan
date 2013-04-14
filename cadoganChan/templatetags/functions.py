import os
from os import path

import PIL
from django import template
from django.template import Library
import re
import string
from string import maketrans
import crypt
import sys
from datetime import datetime
from django.utils import timezone
from cadoganChan.models import Board, Thread, Post
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models.fields.files import ImageFieldFile
from PIL import Image as PImage
from urlparse import urljoin

register = Library()

class NotImageFieldError(ValueError):
    pass

def get_thumb(imagefield, width, height):
    size = width, height
    pathname, filename = path.split(imagefield.path)
    shortname, extname = path.splitext(filename)
    thumbname = '%s-%dx%d%s' % (shortname, width, height, extname)
    p = path.join(pathname, 'thumbs', thumbname)
    if path.isfile(p):
        pass
    else:
        if not path.isdir(path.dirname(p)):
            os.mkdir(path.dirname(p), 0755)
        img = PImage.open(imagefield.path)
        img.thumbnail(size, PImage.ANTIALIAS)
        img.save(p)

    return urljoin(imagefield.url, 'thumbs/' + thumbname)


def get_rescale(imagefield, width, height):
    pathname, filename = path.split(imagefield.path)
    shortname, extname = path.splitext(filename)
    thumbname = '%s-%dx%d%s' % (shortname, width, height, extname)
    p = path.join(pathname, 'rescaled', thumbname)
    if path.isfile(p):
        pass
    else:
        if not path.isdir(path.dirname(p)):
            os.mkdir(path.dirname(p), 0755)
        img = PImage.open(imagefield.path)
        src_width, src_height = img.size
        src_ratio = float(src_width) / float(src_height)
        dst_ratio = float(width) / float(height)

        if dst_ratio < src_ratio:
            crop_height = src_height
            crop_width = crop_height * dst_ratio
            x_offset = float(src_width - crop_width) / 2
            y_offset = 0
        else:
            crop_width = src_width
            crop_height = crop_width / dst_ratio
            x_offset = 0
            y_offset = float(src_height - crop_height) / 3
        img = img.crop((int(x_offset), int(y_offset), int(x_offset+crop_width), int(y_offset+crop_height)))
        img = img.resize((width, height), PImage.ANTIALIAS)
        img.save(p)

    return urljoin(imagefield.url, 'rescaled/' + thumbname)

class ThumbNail(template.Node):
    def __init__(self, imagestr, width, height, rescale=False):
        self.imagestr = template.Variable(imagestr)
        self.width = width
        self.height = height
        self.rescale = rescale

    def render(self, context):
        image = self.imagestr.resolve(context)
        if not isinstance(image, ImageFieldFile):
            raise NotImageFieldError, '%s is not an instance of ImageFieldFile.' % self.imagestr
        if self.rescale:
            self.url = get_rescale(image, self.width, self.height)
        else:
            self.url = get_thumb(image, self.width, self.height)
        return self.url

@register.tag(name='thumb')
def do_thumb(parser, token):
    try:
        tagname, imagestr, widthstr, heightstr, rescalestr = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly 4 arguments" % token.contents.split()[0]
    try:
        width = int(widthstr)
        height = int(heightstr)
        if rescalestr in ('1', 'yes', 'true', 'True'):
            rescale = True
        else:
            rescale = False
    except ValueError:
        raise template.TemplateSyntaxError, 'Arguments error in tag %r' % token.contents.split()[0]
    return ThumbNail(imagestr, width, height, rescale)





def trip(text):
	if text == "":
		return "Anonymous"
	if (text.find('!') == -1):
		return text
	i = text.split('!')
	name = i[0]
	i[1] = text.replace('\\', '')
	if '##' in i[1]:
		trip = text.replace('#', '')
	else:
		trip = i[1]
	trip = unicode(trip).encode('shift-jis')
	salt = trip + 'H.'
	salt = re.sub('/[^\.-z]/', '.', salt[1:3])
	salt = salt.translate(maketrans(':;<=>?@[\]^_`', 'ABCDEFGabcdef'))
	return name + '#' + unicode(crypt.crypt(trip, salt)[-10:])

register.filter(trip)

def humanize_timesince(start_time):
	delta = datetime.now() - start_time.replace(tzinfo=None)

	num_years = delta.days / 365
	if (num_years > 0):
		return "%d year%s" % (num_years, plural(num_years))

	num_weeks = delta.days / 7
	if (num_weeks > 0):
		return "%d week%s" % (num_weeks, plural(num_weeks))

	if (delta.days > 0):
		return "%d day%s" % (delta.days, plural(delta.days))

	num_hours = delta.seconds / 3600
	if (num_hours > 0):
		return "%d hour%s" % (num_hours, plural(num_hours))

	num_minutes = delta.seconds / 60
	if (num_minutes > 0):
		return "%d minute%s" % (num_minutes, plural(num_minutes))

	return "a few seconds"
 
register.filter(humanize_timesince)

def plural(x):
	if(x != 1):
                plural = 's'
        else:
             	plural = ''
	return plural

def text_process(text):
	regex = re.compile(">(?P<quote>.+)")
	occurances = regex.findall(text)
	for occurance in occurances:
		text = text.replace(">"+occurance, "<span class=\"quote\">&gt;"+occurance+"</span>")
	### @123 replacement... will fully link to the correct board
	regex = re.compile("@(?P<id>\w+)")
	occurances = regex.findall(text)
	for occurance in occurances:
		try:
			post = Post.objects.get(id=occurance)
			thread = post.thread
			board = thread.board
			url = reverse("cadoganChan.views.thread", args=[board,thread]) + "#post_"+occurance
			text = text.replace("@"+occurance, "<a href=\""+url+"\">@"+occurance+"</a>")
		except:
			pass
	return text
	
register.filter(text_process)
