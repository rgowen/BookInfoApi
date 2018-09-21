import mws, isbnlib
from lxml import etree

class BookData: # class to hold fetched book data
	def __init__(self, title, price, rank):
		self.title = title
		self.price = price
		self.rank = rank
	def __str__(self):
		return self.title + " " + self.price + " " + self.rank
def get_data(asin): # TODO: error handling
	# get rank and title
	response = products_api.get_matching_product(marketplace_id, [asin])
	context = etree.fromstring(response.original)
	rank = context.xpath('.//*[local-name()="Rank"]')[0].text
	title = context.xpath('.//*[local-name()="Title"]')[0].text
	# get lowest price for used
	response = products_api.get_lowest_priced_offers_for_asin(marketplace_id, asin, condition="Used")
	context = etree.fromstring(response.original)
	price = context.xpath('.//*[local-name()="Amount"]')[0].text
	return BookData(title, price, rank)

# load mws credentials from config file
with open('mws.cfg', 'r') as f: # 0 = MWS_ACCOUNT_ID, 1 = MWS_ACCESS_KEY, 2 = MWS_SECRET_KEY, 3 = MARKETPLACE_ID
	mws_cred = [line.strip() for line in f]
	
def isbn_to_asin(isbn): # returns isbn10 (asin) 
	clean = isbnlib.canonical(isbn)
	if(len(isbn) == 10):
		if(isbnlib.is_isbn10(clean)):
			return clean
		else:
			return '0'
	elif(len(isbn) == 13):
		if(isbnlib.is_isbn13(clean)):
			return isbnlib.to_isbn10(clean)
	else:
		return '0'
		
marketplace_id = mws_cred[3] # easier to use variable for marketplace id
products_api = mws.Products(account_id=mws_cred[0], secret_key=mws_cred[2], access_key=mws_cred[1], region='US')
