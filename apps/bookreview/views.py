# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from models import *

from datetime import datetime

def index(request):
	return render(request, 'bookreview/index.html')

def books(request):
	if 'id' not in request.session:
		return redirect('/bookreview')
	try:
		user=User.objects.get(id=request.session['id'])
		books=Book.objects.all()
		reviews=Review.objects.all().order_by('-created_at')

		context ={ 
			'user': user,
			'reviews':reviews[:3],
			'books':books,

		}
	except User.DoesNotExist:
		return redirect ("/bookreview")
	return render(request, 'bookreview/books.html', context)
	
def register(request):	
	print "register"
	if request.method=='POST':
		errors = {}
		errors = User.objects.basic_validator(request.POST) 
		for x in errors:
			messages.warning(request, errors[x])	
		if( 'user' in errors):
			request.session['id']=errors['user'].id	
			return redirect('/bookreview/books')
		else:
			messages.warning(request, "Email already Taken")

	return redirect('/bookreview')
	
def login(request):	
	if request.method=='POST':
		errors = User.objects.login(request.POST)
	if 'user' in errors:
		request.session['id']=errors['user'].id
		return redirect('/bookreview/books')

	for x in errors:
			messages.warning(request, errors[x])	
	return redirect('/bookreview')			
	

def add(request):
	if 'id' not in request.session:
		return redirect('/bookreview')	
	authorlist= Book.objects.values_list('author', flat=True).distinct()
	print authorlist

	context = {
		'authorlist':authorlist
	}
	return render(request, 'bookreview/add.html', context)

def newbook(request):
	if 'id' not in request.session:
		return redirect('/bookreview')

	if request.method=='POST':
		errors = {}
		errors = Book.objects.basic_validator(request.POST)
		errors2 = Review.objects.basic_validator(request.POST)	
		for x in errors:
			messages.warning(request, errors[x])
		if( not len(errors)):
			book = Book.objects.addbook(request.POST, request.session['id'])

			if(book):
				Review.objects.addreview(request.POST, book.id, request.session['id'])
				return redirect('/bookreview/books/' + str(book.id))
			else:
				messages.warning(request, "Title is already in the system, please resubmit")
	return redirect('/bookreview/add')

def showbook(request, id):
	if 'id' not in request.session:
		return redirect('/bookreview')
	try:
		book = Book.objects.get(id=id)
		reviews = book.book_reviews.all()

		allusers=User.objects.all()
		context = {
			'id':request.session['id'],
			'book':book,
			'reviews':reviews,
			'allusers':allusers,
		}
		return render(request, 'bookreview/showbook.html', context)

	except Book.DoesNotExist:
		return redirect ("/bookreview")
	return redirect('/bookreview')

def showuser(request, id):
	try:
		user=User.objects.get(id=id)
	except User.DoesNotExist:
		return redirect ("/bookreview")
	booklist=[]
	for x in user.user_reviews.all():
		if x.book not in booklist:
			booklist.append(x.book)
	count = len(user.user_reviews.all())
	context = { 'user': user, 'books':booklist, 'count':count}

	return render(request, 'bookreview/users.html', context)

def deletereview(request, id):
	bookid = Review.objects.deletereview(id, request.session['id'])
	print bookid
	if(bookid):
		return redirect('/bookreview/books/' + str(bookid))
	else:
		return redirect('/bookreview/books')

def newreview(request, id):
	if 'id' not in request.session:
		return redirect('/bookreview')
	Review.objects.addreview(request.POST, id, request.session['id'])
	return redirect('/bookreview/books/' + str(id))

def logout(request):
	request.session.clear()
	return redirect('/bookreview')