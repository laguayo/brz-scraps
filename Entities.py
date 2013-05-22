from google.appengine.ext import db
import time
import datetime
class Dealer(db.Model):
	name = db.StringProperty()
	url = db.LinkProperty()
	address = db.PostalAddressProperty()
	phone = db.PhoneNumberProperty()
	cars = db.ListProperty(db.Key)
	area = db.StringProperty()
	

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
	local_date = db.StringProperty()
	dealer = db.ReferenceProperty(Dealer)
	invalid = db.BooleanProperty(required=False)

class UserPref(db.Model):
	name = db.StringProperty()
	email = db.StringProperty()
	block = db.BooleanProperty()
	permissions = db.StringListProperty()

class Pacific_tzinfo(datetime.tzinfo):
    """Implementation of the Pacific timezone."""
    def utcoffset(self, dt):
        return datetime.timedelta(hours=-8) + self.dst(dt)

    def _FirstSunday(self, dt):
        """First Sunday on or after dt."""
        return dt + datetime.timedelta(days=(6-dt.weekday()))

    def dst(self, dt):
        # 2 am on the second Sunday in March
        dst_start = self._FirstSunday(datetime.datetime(dt.year, 3, 8, 2))
        # 1 am on the first Sunday in November
        dst_end = self._FirstSunday(datetime.datetime(dt.year, 11, 1, 1))

        if dst_start <= dt.replace(tzinfo=None) < dst_end:
            return datetime.timedelta(hours=1)
        else:
            return datetime.timedelta(hours=0)
    def tzname(self, dt):
        if self.dst(dt) == datetime.timedelta(hours=0):
            return "PST"
        else:
            return "PDT"