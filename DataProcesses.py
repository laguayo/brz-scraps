import webapp2
import urllib2
import logging
import re

from Entities import *
from google.appengine.ext import db
from bs4 import BeautifulSoup
from google.appengine.api import taskqueue

class StoreDealers(webapp2.RequestHandler):
	inventoryString = '/new-inventory/index.htm'
	modelParam = '?model=BRZ&'
	def store_dealer(self, force, name, url, address, phone):
		dealer = db.GqlQuery("SELECT * FROM Dealer WHERE url = :1 ", url).get()
		if dealer == None or force == 'true':
			new_dealer = Dealer(key_name=url,name=name, url=url, address=address, phone=phone)
			new_dealer.put()
			logging.info( 'Saved dealer: %s', new_dealer.name )
		return
	def init_dealers_bay(self, force):
		check_db = Dealer.all(keys_only=True)
		logging.info( force )
		if check_db.get() == None or force == 'true':
			dealers = ['http://www.stevenscreeksubaru.com', 'http://www.livermoresubaru.com',
			 'http://www.subaruofoakland.com', 'http://www.carlsensubaru.com', 
			 'http://www.marinsubaru.net', 'http://www.albanysubaru.com',
			 'http://www.diablosubaru.com', 'http://www.hanleesnapasubaru.com',
			 'http://www.serramontesubaru.com', 'http://www.putnamsubaruofburlingame.com',
			 'http://www.subaruofglendale.net', 'http://www.subarushermanoaks.com',
			 'http://www.subarupacific.com', 'http://www.puentehillssubaru.com',
			 'http://www.subarusantamonica.com', 'http://www.timmonssubaru.com',
			 'http://www.sierrasubaru.com', 'http://www.southcoastsubaru.com']
			for u in dealers:
				car_url = u + StoreDealers.inventoryString + StoreDealers.modelParam
				logging.info( 'Saving dealer: %s', car_url )
				self.store_dealer(force, ' ',car_url,' ','0')
			return True
		else:
			return False
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		if self.request.get("init"):
			frce = self.request.get("force") if self.request.get("force") == 'true' else 'false'
			if self.init_dealers_bay(frce) == True:
				self.response.write("Initialized Dealer Db")
			else:
				self.response.write("Dirty DB")
		else:
			url = self.request.get("url") 
			if not url:
				self.response.write("missing arguments")
			name = self.request.get("name") if self.request.get("name") else ' '
			addr = self.request.get("addr") if self.request.get("addr") else ' '
			phone = self.request.get("phone") if self.request.get("phone") else '0000000000'
			self.store_dealer(name, url, addr, phone)
		return
	def post(self):
		url = self.request.get('url')
		dealer = Dealer(key_name=url)
		dealer.name = self.request.get('name')
		dealer.addr = self.request.get('addr')
		dealer.phone =self.request.get('phone')
		dealer.url = url
		dealer.put()
		logging.info("Saved dealer %s", dealer.name)
		self.redirect('/dealer/list')
class ParseDealer(webapp2.RequestHandler):
	def get(self):
		taskqueue.add(queue_name='carparse', url='/dealer/parse', params = {})
		return
app = webapp2.WSGIApplication([('/task/cars', ParseDealer)],debug=True)

#url = /dealer/parse/*
class ParseDealersTask(webapp2.RequestHandler):
	#post will result in starting a task across all dealers
	def post(self):
		dealers = Dealer.all()
		for dealer in dealers:
			logging.info('Parsing Dealer: %s', dealer.name)
			old_keys = set(dealer.cars)
			car_keys = self.get_url(dealer.url)
			self.invalidate_old(car_keys, old_keys)
		return
	#get will process one dealer in key based on dealer name
	def get(self, name):
		self.response.headers['Content-Type'] = 'text/plain'
		# name = self.request.get('name')
		dealer = Dealer.gql('WHERE name = :1', name).get()
		if dealer != None:
			logging.info('Dealer %s', dealer.name)
			url = dealer.url
			self.get_url(url)
			self.response.write('Started Parsing Dealer ' + dealer.name)
		else:
			self.response.write('Dealer not found ' + name)
		return
	def invalidate_old(self, cars, old_keys):
		for k in old_keys:
			if k not in cars:
				car = Car.get(k)
				car.invalid = True
				car.put()
	def get_url(self, url):
		logging.info('Getting url: %s',url)
		if 'BRZ' not in url:
			brz_url = url + StoreDealers.inventoryString + StoreDealers.modelParam
		else:
			brz_url = url
		try:
			page = urllib2.urlopen(brz_url).read()
			soup = BeautifulSoup(page, from_encoding="UTF-8")
			cars = soup.find_all("li", class_="inv-type-new")
			logging.info('Found %s cars',len(cars))
			car_set = set()
			for car_html in cars:
				car_set.add(self.parse_car(car_html, url))
			return car_set
		except urllib2.URLError, e:
			 logging.error(e)
	def parse_car(self, car_str, url):
		try:
			vin = unicode(car_str.find(class_='hproduct').attrs['data-vin'])
			c = Car(key_name=vin, vin=vin)
			media = car_str.find(class_='media')
			c.model = unicode(car_str.find(class_='url').string)
			c.price = self.get_price(car_str.find_all(class_='value'))
			c.link = unicode(media.a.attrs['href'])
			c.img_src = unicode(media.img.attrs['src'])
			try:
				description = car_str.find(class_='description').text.replace('\n','')
				desc_dict = dict(e.split(':') for e in description.split(','))
			except (ValueError, TypeError):
				logging.error('Error Parsing Car line Description %s \te = %s', car_str)
				return
			logging.info('Car Description dict %s', desc_dict)
			
			c.transmission = unicode(desc_dict[' Transmission'])
			c.ex_color = unicode(desc_dict[' Exterior Color'])
			c.int_color = unicode(desc_dict[' Interior Color'])
			c.model_type = unicode(desc_dict[' Model Code'])
			if ' Stock #' in desc_dict:
				c.stock_num = desc_dict[' Stock #']
			if 'Limit' in c.model:
				c.trim = 'Limited'
			else:
				c.trim = 'Premium'
			c.dealer = Dealer.gql('WHERE url = :1 ', url).get().key()
			c.key_name = c.vin
			self.store_car(c)
			return c.key()
		except AttributeError, e:
			logging.error('Error Parsing Car line %s \ne = %s', car_str, e) 
		return
	def store_car(self, car):
		dealer = Dealer.get(car.dealer.key())
		car.put()
		if dealer != None:
			if car.key() not in set(dealer.cars):
				dealer.cars.append(car.key())
				dealer.put()
		car.put()
		logging.info( 'Saved car: %s', car.vin )
		return
	def get_price(self, prices):
		for p in prices:
			if '$' in p.string:
				logging.info('Price %s',p)
				non_decimal = re.compile(r'[^\d.]+')
				prStr = non_decimal.sub('', p.string)
				return int(prStr)
		return 0