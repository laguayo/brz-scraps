#!/usr/bin/env python
import webapp2
import urllib2
import logging
import jinja2
import os


from Entities import *
from bs4 import BeautifulSoup
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import taskqueue
from DataProcesses import *
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class StoreAuthUsers(webapp2.RequestHandler):
	def is_user_auth(self):
		user = users.get_current_user()
		
		if user:
			q = db.GqlQuery("SELECT * FROM UserPref WHERE email = :1", user.email())
			user_pref = q.get()
			if user_pref != None:
				logging.info("User %s visited", user_pref.email)
				return not user_pref.block
			else:
				logging.info('Redirecting Blocked user %s ',user.email())
				template = JINJA_ENVIRONMENT.get_template('welcome.html')
				self.response.write(template.render())
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		 	
	def put_auth_user(self, name, email):
		new_user = UserPref(name=name, 
							email=email, block=False, key_name=email)
		if not UserPref.get(new_user.key()):
			logging.info("User %s saved", email)
			new_user.put()
		return
	def get(self):
		save = self.request.get("save")
		user = users.get_current_user()
		if save and user:
			self.put_auth_user(user.nickname(), user.email())
			self.redirect('/')
		else:
			template = JINJA_ENVIRONMENT.get_template('welcome.html')
			self.response.write(template.render())
		return
class NewDealerForm(webapp2.RequestHandler):
	def get(self, action, dealer):
		if StoreAuthUsers(self.request, self.response).is_user_auth():
			if action == 'edit' and dealer:
				template_values = { 'd' : Dealer.gql('WHERE name = :1', dealer).get() }
			else:
				template_values = { 'd' : None }
			template = JINJA_ENVIRONMENT.get_template('dealer_form.html')
			self.response.write(template.render(template_values))
		return
class ListDealers(webapp2.RequestHandler):
	def get(self, sort):
		if StoreAuthUsers(self.request, self.response).is_user_auth():
			if sort and sort != '1':
				dealers = Dealer.all().order(sort).fetch(100)
			else:
				dealers = Dealer.all().fetch(100)
			template_values = { 'dealers' : dealers }
			template = JINJA_ENVIRONMENT.get_template('dealers.html')
			self.response.write(template.render(template_values))
		return
class WelcomePage(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('welcome.html')
		self.response.write(template.render())
		return
class MainHandler(webapp2.RequestHandler):
	def get(self):
		if StoreAuthUsers(self.request, self.response).is_user_auth():
			sort = self.request.get('sort')
			if sort:
				cars = Car.all().order(sort).fetch(100)
			else:
				cars = Car.all().fetch(100)
			for c in cars:
				pac_date = datetime.fromtimestamp(time.mktime(c.last_date.timetuple()), Pacific_tzinfo())
				c.local_date = pac_date.strftime('%m/%d/%y %I:%M %p')
			template_values = { 'cars' : cars }
			template = JINJA_ENVIRONMENT.get_template('index.html')
			self.response.write(template.render(template_values))
		return
app = webapp2.WSGIApplication([('/', MainHandler),
								('/users', StoreAuthUsers),
								('/welcome', WelcomePage),
								('/task/cars', ParseDealer),
								('/dealer/save', StoreDealers),
								(r'/dealer/list/(.*)', ListDealers),
								(r'/dealer/parse/(.*)', ParseDealersTask),
								(r'/dealer/(\w+)/(.*)', NewDealerForm)],
                              debug=True)
