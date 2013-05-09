from google.appengine.ext import db

class Dealer(db.Model):
	name = db.StringProperty()
	url = db.LinkProperty()
	address = db.PostalAddressProperty()
	phone = db.PhoneNumberProperty()
	cars = db.ListProperty(db.Key)

class Car(db.Model):
	model = db.StringProperty()
	price = db.IntegerProperty()
	transmission = db.StringProperty()
	ex_color = db.StringProperty()
	int_color = db.StringProperty()
	model_type = db.StringProperty()
	vin = db.StringProperty()
	trim = db.StringProperty()
	stock = db.IntegerProperty()
	img_src = db.StringProperty()
	link = db.StringProperty()
	last_date = db.DateTimeProperty(auto_now=True)
	dealer = db.ReferenceProperty(Dealer)
	invalid = db.BooleanProperty(required=False)

class UserPref(db.Model):
	name = db.StringProperty()
	email = db.StringProperty()
	block = db.BooleanProperty()
