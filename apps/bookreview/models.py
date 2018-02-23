  # Inside models.py
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
import re
import bcrypt
from django.db import IntegrityError

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
	def basic_validator(self, postData):
		errors = {}
		if(not EMAIL_REGEX.match(postData['email'].lower())):
			errors['email'] = "Invalid email"
		if len(postData['name'])<2:
			errors['name'] = "First name should be more than 2 characters"
		if len(postData['alias'])<2:
			errors['alias'] = "Alias should be more than 2 characters"			
		if (postData['password'] != postData['passwordconfirm']) :
			errors['password_match'] = "Passwords don't match"
		if len(postData['password'])<8:
			errors['password'] = "Password must be at least 8 characters"		
		


		if(not len(errors)):
			hash1 = bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt())						
			try:
				User.objects.create(name=postData['name'], alias=postData['alias'], email=postData['email'].lower(), password=hash1)
				user = User.objects.get(email=postData['email'].lower())
				errors['user']=user
			except IntegrityError as e:
				if 'constraint' in e.message:
					return errors
		return errors

	def login(self, postData):
		errors = {}
		email = postData['email'].lower()
		try:
			user = User.objects.get(email=email)
			if(bcrypt.checkpw(postData['password'].encode(), user.password.encode())):
				return user
			errors['incorrect'] = "Incorrect Username Or Password"
		except User.DoesNotExist:
			errors['incorrect'] = "Incorrect Username Or Password"
		return False


class BookManager(models.Manager):
	def basic_validator(self, postData):
		errors = {}
		if len(postData['title']) < 2:
			errors['title'] = "Title must be at least 2 Characters"
		if len(postData['author']) < 2 and len(postData['authornew']) <2:
			errors['author'] = "Author must be at least 2 Characters"
		return errors

	def addbook(self, postData, id):
		try:
			if(Book.objects.filter(title=postData['title'].lower())):
				print "check succeed"
				return False
			if (postData['authornew']):
				Book.objects.create(title=postData['title'].lower(), author=postData['authornew'], uploader=User.objects.get(id=id))
			else:
				Book.objects.create(title=postData['title'].lower(), author=postData['author'], uploader=User.objects.get(id=id))

			book = Book.objects.get(title=postData['title'].lower())
			return book
		except IntegrityError as e:
			if 'constraint' in e.message:
				return False
		return False

class ReviewManager(models.Manager):
	def basic_validator(self, postData):
		errors ={}
		if(int(postData['rating']) < 0 or int(postData['rating']) >5):
			errors['rating'] = "Rating must be between 1-5 inclusive"
		if(len(postData['review'])) < 1:
			errors['review'] = "Review must not be empty"			
		return errors

	def addreview(self, postData, bookid, id):
		Review.objects.create(content=postData['review'],rating=postData['rating'], book=Book.objects.get(id=bookid), reviewer=User.objects.get(id=id))

	def deletereview(self, reviewid, reviewerid):
		review = Review.objects.get(id=reviewid)
		user = User.objects.get(id=reviewerid)
		if(review.reviewer == user):
			relatedbook = review.book
			review.delete()
			return relatedbook.id
		else:
			return 0


class User(models.Model):
	name = models.CharField(max_length=255)
	alias = models.CharField(max_length=255)
	email = models.CharField(max_length=255, unique=True)
	password = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	objects=UserManager()

class Book(models.Model):
	title=models.CharField(max_length=255, unique=True)
	author=models.CharField(max_length=255)
	uploader=models.ForeignKey(User, related_name='uploaded_books')
	objects=BookManager()

class Review(models.Model):
	content=models.CharField(max_length=255)
	rating=models. PositiveSmallIntegerField()
	reviewer=models.ForeignKey(User, related_name='user_reviews')
	book=models.ForeignKey(Book, related_name='book_reviews')
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	objects=ReviewManager()