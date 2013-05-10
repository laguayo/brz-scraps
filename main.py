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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class StoreAuthUsers(webapp2.RequestHandler):
	def is_user_auth(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		if user:
			q = db.GqlQuery("SELECT * FROM UserPref WHERE email = :1", user.email())
			user_pref = q.get()
			if user_pref != None:
				logging.info("User %s visited", user_pref.email)
				return not user_pref.block
			else:
				return False
		else:
			logging.info('Blocked user %s ',user.email())
			template = JINJA_ENVIRONMENT.get_template('welcome.html')
			self.response.write(template.render())
	def put_auth_user(self, name, email):
		new_user = UserPref(name=name, 
							email=email, block=False, key_name=email)
		logging.info("User %s saved", email)
		new_user.put()
		return
	def get(self):
		save = self.request.get("save")
		user = users.get_current_user()
		if save:
			self.put_auth_user(user.nickname(), user.email())
			self.redirect('/')
		return
class NewDealerForm(webapp2.RequestHandler):
	def get(self, action, dealer):
		if StoreAuthUsers().is_user_auth():
			if action == 'edit' and dealer:
				template_values = { 'd' : Dealer.gql('WHERE name = :1', dealer).get() }
			else:
				template_values = { 'd' : None }
			template = JINJA_ENVIRONMENT.get_template('dealer_form.html')
			self.response.write(template.render(template_values))
		return
class ListDealers(webapp2.RequestHandler):
	def get(self):
		if StoreAuthUsers().is_user_auth():
			sort = self.request.get('sort')
			if sort:
				dealers = Dealer.all().order(sort).fetch(100)
			else:
				dealers = Dealer.all().fetch(100)
			template_values = { 'dealers' : dealers }
			template = JINJA_ENVIRONMENT.get_template('dealers.html')
			self.response.write(template.render(template_values))
		return
class MainHandler(webapp2.RequestHandler):
	def get(self):
		if StoreAuthUsers().is_user_auth():
			sort = self.request.get('sort')
			if sort:
				cars = Car.all().order(sort).fetch(100)
			else:
				cars = Car.all().fetch(100)
			template_values = { 'cars' : cars }
			template = JINJA_ENVIRONMENT.get_template('index.html')
			self.response.write(template.render(template_values))
		return
app = webapp2.WSGIApplication([('/', MainHandler),
								('/users', StoreAuthUsers),
								('/dealer/save', StoreDealers),
								(r'/dealer/parse/(.*)', ParseDealersTask),
								(r'/dealer/(\w+)/(.*)', NewDealerForm),
								('/dealer/list', ListDealers)],
                              debug=True)
