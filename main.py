#!/usr/bin/env python
import webapp2
import urllib2
import logging
import jinja2
import os

from DataProcesses import *
from google.appengine.api import users
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class StoreAuthUsers(webapp2.RequestHandler):
	def get_user_auth(self):
		user = users.get_current_user()
		if user:
			q = db.GqlQuery("SELECT * FROM UserPref WHERE email = :1", user.email())
			user_pref = q.get()
			if user_pref != None:
				logging.info("User %s visited", user_pref.email)
				return user_pref
			else:
				logging.info('Redirecting Blocked user %s ',user.email())
				template = JINJA_ENVIRONMENT.get_template('welcome.html')
				self.response.write(template.render())
		else:
			self.redirect(users.create_login_url(self.request.uri))
	def is_user_auth(self):
		user_pref = self.get_user_auth()
		if user_pref:
			return not user_pref.block
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
		user = StoreAuthUsers(self.request, self.response).get_user_auth()
		if not user.block:
			if action == 'edit' and dealer:
				template_values = { 'd' : Dealer.gql('WHERE name = :1', dealer).get(), 'user' : user }
			else:
				template_values = { 'd' : None, 'user' : user }
			template = JINJA_ENVIRONMENT.get_template('dealer_form.html')
			self.response.write(template.render(template_values))
		return
class ListDealers(webapp2.RequestHandler):
	def get(self, sort):
		user = StoreAuthUsers(self.request, self.response).get_user_auth()
		if not user.block:
			if sort and sort != '1':
				dealers = Dealer.all().order(sort).fetch(100)
			else:
				dealers = Dealer.all().fetch(100)
			template_values = { 'dealers' : dealers, 'user' : user }
			template = JINJA_ENVIRONMENT.get_template('dealers.html')
			self.response.write(template.render(template_values))
		return
class WelcomePage(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('welcome.html')
		self.response.write(template.render())
		return
class EditUser(webapp2.RequestHandler):
	def get(self, action, email):
		if action in ['edit', 'view', 'new']:
			user_pref = StoreAuthUsers(self.request, self.response).get_user_auth()
			if user_pref != None and 'Edit_Dealers' in user_pref.permissions or users.is_current_user_admin():
				if action == 'new':
					new_user = UserPref()
					template_values = { 'user' : new_user }
				else: 
					curr_user = UserPref.gql("WHERE email = :1", email).get()
					template_values = { 'user' : curr_user }

				template = JINJA_ENVIRONMENT.get_template('user_form.html')
				self.response.write(template.render(template_values))
			else:
				self.redirect('/')
		return
	def post(self, action, dummy):
		email = self.request.get('email')
		user = UserPref(key_name=email)
		user.email = email
		if self.request.get('name'):
			user.name = self.request.get('name')
		if self.request.get('block'):
			user.block = True
		else:
			user.block = False
		if self.request.get('permissions'):
			user.permissions = self.request.get('permissions').split(',')
		if user.put():	
			logging.info("Saved User %s", user.name)
			self.redirect('/')
		return
class MainHandler(webapp2.RequestHandler):
	def get(self):
		if StoreAuthUsers(self.request, self.response).is_user_auth():
			cars = Car.all().fetch(100)
			logging.info("Loaded %s cars", len(cars))
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
								(r'/users/(\w+)/(.*)', EditUser),
								('/dealer/save', StoreDealers),
								(r'/dealer/list/(.*)', ListDealers),
								(r'/dealer/parse/(.*)', ParseDealersTask),
								(r'/dealer/(\w+)/(.*)', NewDealerForm)],
                              debug=True)
