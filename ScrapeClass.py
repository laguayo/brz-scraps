import urllib2
from bs4 import BeautifulSoup

class ScrapeClass():
	def __init__( self ):
		# self.pages = ['http://www.capitolsubarusj.com','http://www.stevenscreeksubaru.com', 'http://www.livermoresubaru.com', 'http://www.subaruofoakland.com', 'http://www.carlsensubaru.com', 'http://www.marinsubaru.net', 'http://www.albanysubaru.com',' http://www.diablosubaru.com']
		self.pages = ['http://www.subaruofoakland.com']
		self.inventoryString = '/new-inventory/index.htm'
		self.modelParam = '?model=BRZ&'

	def loadSite( self ):			
		for subsite in self.pages:
			site = subsite + self.inventoryString + self.modelParam
			return ''.join(self.getCars(site))

	def getCars( self, site ):
		carstring = ['']
		try:
			print 'OPENING :' + site
			page = urllib2.urlopen(site).read()
			soup = BeautifulSoup(page, from_encoding="UTF-8")
			cars = soup.find_all("li", class_="inv-type-new")
			# self.printCars(cars)
			carstring = self.printCars(cars)
		except urllib2.URLError, e:
			 print(e)
		return carstring

	def printCars( self, mylist ):
		catCars = ['']
		for row in mylist:
			for st in row.stripped_strings:
					string = unicode(st).encode('utf-8')
					if '2013 Subaru BRZ' in string:
							# print('\n' + string)
							catCars.append('<br />'+ string)
							if "Limit" in string:
									# print("+++++++++")
									catCars.append('<br />++++++++')
					elif string == 'Satin White Pearl':
							# print('\tSatin White Pearl<============WHITE')	
							catCars.append('<br />    Satin White Pearl<============WHITE')
					elif string == '6-Speed Automatic':
							# print('\t6-Speed Automatic<============AUTOMATIC')
							catCars.append('<br />    6-Speed Automatic<============AUTOMATIC')	
					elif '$' in string:
							# print('\t' + string)	
							catCars.append('<br />    '+ string)					
					elif string not in ('VIN:','More','...',':','Adjusted Price', 'Get ePrice', 'Engine:', 'H-4 cyl', ',', 'Drive Line:','RWD', 'Transmission:', 'Interior Color:', 'Dark Gray', 'Model Code:', 'Details', '2.9% Financing','Watch Video', 'Compare','Compare Selected', 'View Details', 'Manufacturer Offer:'):
							# print('\t' + string)
							catCars.append('<br />    '+ string)
		return catCars