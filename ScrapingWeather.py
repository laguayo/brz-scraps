import urllib3
from bs4 import BeautifulSoup

class ScrapingWeather:

	def __init__( self ):
		self.pages = ['http://www.capitolsubarusj.com','http:/www.stevenscreeksubaru.com', 'http://www.livermoresubaru.com', 'http://www.subaruofoakland.com', 'http://www.carlsensubaru.com', 'http://www.marinsubaru.net', 'http://www.albanysubaru.com',' http://www.diablosubaru.com']
		self.inventoryString = '/new-inventory/index.htm'
		self.modelParam = '?model=BRZ&'

	def loadSite( self ):			
		for subsite in self.pages:
			site = subsite + ScrapingWeather.inventoryString + ScrapingWeather.modelParam
			self.getCars(site)

	def getCars( self, site ):
		print '\n\nOPENING :' + site
		try:
			page = urllib2.urlopen(site).read()
			soup = BeautifulSoup(page)
			cars = soup.find_all("li", class_="inv-type-new")
			self.printCars(cars)
		except urllib2.URLError, e:
			handleError(e)
		return

	def printCars( self, mylist ):
		for row in mylist:
			for string in row.stripped_strings:
					if '2013 Subaru BRZ' in string:
							print('\n' + string)
							if "Limit" in string:
									print("+++++++++")
					elif string == 'Satin White Pearl':
							print('\tSatin White Pearl<============WHITE')	
					elif string == '6-Speed Automatic':
							print('\t6-Speed Automatic<============AUTOMATIC')	
					elif '$' in string:
							print('\t' + string)						
					elif string not in ('VIN:','More','...',':','Adjusted Price', 'Get ePrice', 'Engine:', 'H-4 cyl', ',', 'Drive Line:','RWD', 'Transmission:', 'Interior Color:', 'Dark Gray', 'Model Code:', 'Details', '2.9% Financing','Watch Video', 'Compare','Compare Selected', 'View Details', 'Manufacturer Offer:'):
							print('\t' + string)
		return