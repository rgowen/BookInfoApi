from flask import Flask, request, abort
from flask_restful import Resource, Api
from flask_jsonpify import jsonify
import sqlite3, time, datetime, logging, os, isbnlib, amazon



def dict_factory(cursor, row): 
	d = {} 
	for idx, col in enumerate(cursor.description): 
		d[col[0]] = row[idx] 
	return d

def create_database():
	db_connect.execute("create table if not exists books(asin,title,price,lastupd,rank)")
	db_connect.commit()

def update_db(asin):
	db_connect.row_factory = sqlite3.Row
	query = db_connect.execute('select * from books where asin="{}"'.format(asin))
	for row in query:	
		if(time.time() - float(row['lastupd']) > day_seconds): # update if date is older than a day
			data = amazon.get_data(asin)
			db_connect.execute('update books set lastupd={},price={},rank={} where asin="{}"'.format(time.time(), data.price, data.rank, asin))
			db_connect.commit()
			logging.info('[{}] Updated asin/isbn {} price to {}, rank to {}'.format(datetime.datetime.now(), asin, data.price, data.rank))
		break
	else: # if no row, make a new record. amazon.py functionality will take care of the data
		new_record(asin)

class get_isbn(Resource):
	def get(self, isbn):
		output = None
		asin = amazon.isbn_to_asin(isbn)
		if(asin != '0'):
			update_db(asin)
			db_connect.row_factory = dict_factory
			query = db_connect.execute('select * from books where asin="{}"'.format(asin))
			output = jsonify(query.fetchall())
			logging.info('[{}] remote addr {} requested data for isbn {}, successful. asin = {}'.format(datetime.datetime.now(), request.remote_addr, isbn, asin))
		else:
			logging.info('[{}] remote addr {} requested data for isbn {}, failed (invalid isbn)'.format(datetime.datetime.now(), request.remote_addr, isbn))
			abort(404)
		return output
def new_record(asin): # create a new record in the db TODO: amazon api
	book = amazon.get_data(asin)
	lastupd = time.time()
	db_connect.execute("insert into books(asin,title,price,rank,lastupd) values(?,?,?,?,?)", (asin, book.title, book.price, book.rank, lastupd))
	db_connect.commit()

day_seconds = 86400 # number of seconds in a day, used for updating prices
# set up logging
os.remove('data.log')
logging.basicConfig(filename='data.log',level=logging.INFO)	
# set up db
db_connect = sqlite3.connect('data.db')
create_database()
# set up flask
app = Flask(__name__)
api = Api(app)
api.add_resource(get_isbn, '/GetIsbn/<isbn>')
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5002)