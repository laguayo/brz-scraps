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
	def put_auth_user(self, name, email):
		new_user = UserPref(name=name, 
							email=email, block=False, key_name=email)
		new_user.put()
		return
	def get(self):
		save = self.request.get("save")
		user = users.get_current_user()
		logging.info("User %s found", user.email())
		if save:
			self.put_auth_user(user.nickname(), user.email())
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.write( 'Saved User email ' + user.email() )
		return
class NewDealerForm(webapp2.RequestHandler):
	def get(self):
		return
class MainHandler(webapp2.RequestHandler):
	def is_user_auth(self, email):
		q = db.GqlQuery("SELECT * FROM UserPref WHERE email = :1", email)
		user_pref = q.get()
		logging.info("User %s visited", user_pref.email)
		if user_pref != None:
			return not user_pref.block
		else:
			return False
	def get(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		if user:
			if self.is_user_auth(user.email()):
				sort = self.request.get('sort')
				if sort:
					cars = Car.all().order(sort).fetch(100)
				else:
					cars = Car.all().fetch(100)
				template_values = { 'cars' : cars }
				template = JINJA_ENVIRONMENT.get_template('index.html')
				self.response.write(template.render(template_values))
			else:
				logging.info('Blocked user %s ',user.email())
				self.response.headers['Content-Type'] = 'text/plain'
				self.response.write("Hello Subaru World")
		else:
			self.redirect(users.create_login_url(self.request.uri))
		return
app = webapp2.WSGIApplication([('/', MainHandler),
								('/users', StoreAuthUsers),
								('/dealers', StoreDealers),
								('/cars', ParseDealersTask),
								('/carsStart', ParseDealer)],
                              debug=True)
