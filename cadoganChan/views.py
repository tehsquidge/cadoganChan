from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django import forms
from django.utils import timezone
from django.core.urlresolvers import reverse

from models import Board, Thread, Post
from forms import threadForm, postForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def index(request):
    context = RequestContext(request)
    context['boards'] = Board.objects.all()
    #context['form'] = threadForm(data = request.POST)
    return render_to_response('cadoganChan/index.html', context)


#new threads are created in a board 
def board(request, board):
	context = RequestContext(request)
	context['form'] = threadForm()
	context['current_board'] = get_object_or_404(Board, id=board)
	context['success_message'] = ''
	if request.method == 'POST':
		request.POST.board_id = board
		context['form'] = threadForm(request.POST or None, request.FILES or None)
		if(context['form'].is_valid()):
			post = context['form'].save(commit=False)
			thread = Thread(board=context['current_board'])
			thread.save()
			post.thread = thread
			post.save()
			context['form'] = threadForm()
			if(post.email == "noko"):
				return HttpResponseRedirect(reverse("cadoganChan.views.thread", args=[board,thread.id]) +"#post_"+str(post.id))
			else:
				context['success_message'] = "<div class=\"successMessage\">Thread Added... <a href=\""+reverse("cadoganChan.views.thread", args=[board,thread.id])+"#post_"+str(post.id)+"\">view</a></div>"
				return render_to_response('cadoganChan/postAdded.html',context)
	context['boards'] = Board.objects.all()
	threads = Thread.objects.filter(board=board).order_by("last_updated").reverse()
	paginator = Paginator(threads, 10) # Show 25 contacts per page
	page = request.GET.get('page')
	try:
		context['threads'] = paginator.page(int(page or 1))
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		context['threads'] = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		context['threads'] = paginator.page(paginator.num_pages)
	return render_to_response('cadoganChan/viewBoard.html', context)

#posts are created here  
def thread(request,board_id,thread_id):
    context = RequestContext(request)
    context['form'] = postForm()
    context['current_board'] = get_object_or_404(Board, id=board_id)
    context['thread'] = get_object_or_404(Thread, id=thread_id)
    
    #if we are adding a new thread
    if request.method == 'POST' and (not context['thread'].locked):
		request.POST.board_id = board_id
		context['form'] = postForm(request.POST or None, request.FILES or None)
		if(context['form'].is_valid()):
			post = context['form'].save(commit=False)
			if(post.email != "sage"): #sage stops bumping
				context['thread'].last_updated = timezone.now()
			post.thread = context['thread']
			context['thread'].save()
			post.save()
			context['form'] = postForm()
			if(post.email == "noko"): #noko returns us to the thread instantly
				return HttpResponseRedirect(reverse("cadoganChan.views.thread", args=[board_id,thread_id]) +"#post_"+str(post.id))
			else: #else show success page
				context['success_message'] = "<div class=\"successMessage\">Post Added... <a href=\""+reverse("cadoganChan.views.thread", args=[board_id,thread_id])+"\">back</a></div>";
				return render_to_response('cadoganChan/postAdded.html', context)
		else:
			context['boards'] = Board.objects.all()
			return render_to_response('cadoganChan/viewThread.html', context)
    else:
		context['boards'] = Board.objects.all()
		return render_to_response('cadoganChan/viewThread.html', context)

	
