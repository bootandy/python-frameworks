# Python imports
import base64
import asyncmongo
from bson.objectid import ObjectId
import os

# Tornado imports
import pymongo
import re
import uuid
import datetime
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from tornado.web import url


define("port", default=8889, type=int)
define("config_file", default="app_config.yml", help="app_config file")

#MONGO_SERVER = '192.168.1.68'
MONGO_SERVER = 'localhost'


# Application class
class Application(tornado.web.Application):
  def __init__(self):
    #self.config = self._get_config()
    handlers = [
      url(r'/', IndexHandler, name='index'),
      url(r'/hello', HelloWorldHandler, name='hello'),
      url(r'/price', PriceHandler, name='price'),
      url(r'/postcode', PostcodeHandler, name='postcode'),
      url(r'/single', SingleFieldHandler, name='single'),

    ]

    #xsrf_cookies is for XSS protection add this to all forms: {{ xsrf_form_html() }}
    settings = {
      'static_path': os.path.join(os.path.dirname(__file__), 'static'),
      'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
      "cookie_secret":  base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
      #'xsrf_cookies': True,
      #'debug':True,
      'debug':False,
      'log_file_prefix':"tornado.log"
    }

    tornado.web.Application.__init__(self, handlers,**settings) # debug=True ,
    # Connect to mongodb
    self.db = asyncmongo.Client(pool_id='mydb', host=MONGO_SERVER, port=27017, maxcached=10, maxconnections=1000, dbname='houseprices')

    # asyncmonogo doesn't support 'distinct' so we pre load these dates
    self.syncconnection = pymongo.Connection(MONGO_SERVER, 27017)
    self.syncdb = self.syncconnection ["houseprices"]
    self.legal_dates = self.syncdb.houses.distinct( 'dateadded')
    legal_postcodes_results = self.syncdb.houses.distinct( 'postcode_part')

    self.legal_postcodes = []
    for p in legal_postcodes_results:
      self.legal_postcodes.append(p)
    self.legal_postcodes.sort()

    self.syncconnection.close()



# Handlers
class HelloWorldHandler(tornado.web.RequestHandler):
  def get(self):
    self.write("Hello World")

  def post(self):
    return self.get()

class BaseHandler(tornado.web.RequestHandler):
  @property
  def db(self):
    return self.application.db

  def get_dates(self):
    return self.application.legal_dates

  def get_postcodes(self):
    return self.application.legal_postcodes

  def get_date(self):
    return datetime.datetime.strptime(self.get_argument("date"), "%Y-%m-%d %H:%M:%S" )

class IndexHandler(BaseHandler):
  @tornado.web.asynchronous
  def get(self):
    self.db.users.find({'price':-999999}, callback=self._on_response )

  def _on_response(self, response, error):
    if error:
      raise tornado.web.HTTPError(500)
    self.render('list.html', data=response, price='', postcode='', dates=self.get_dates(), postcodes=self.get_postcodes())



class PriceHandler(BaseHandler):
  @tornado.web.asynchronous
  def post(self):
    self.price =  int(self.get_argument("price", 0))
    date = self.get_date()

    self.db.houses.find({'price':self.price, 'dateadded':date},  callback=self._on_response )


  def _on_response(self, response, error):
    if error:
      raise tornado.web.HTTPError(500)
    self.render('list.html', data=response, price=self.price, postcode='', dates=self.get_dates(), postcodes=self.get_postcodes() )


class PostcodeHandler(BaseHandler):
  @tornado.web.asynchronous
  def post(self):
    date = self.get_date()
    self.postcode =  self.get_argument("postcode", "unknown")

    self.db.houses.find({
          'postcode_part': self.postcode,
          'dateadded':date},
        callback=self._on_response )

  def _on_response(self, response, error):
    if error:
      raise tornado.web.HTTPError(500)
    self.render('list.html', data=response, price='', postcode=self.postcode, dates=self.get_dates(), postcodes=self.get_postcodes() )


class SingleFieldHandler(BaseHandler):
  @tornado.web.asynchronous
  def post(self):
    self.db.houses.find({'_id': ObjectId('4facedc7283f663b1c000013') },
        callback=self._on_response )

  @tornado.web.asynchronous
  def get(self):
    self.db.houses.find({'_id': ObjectId('4facedc7283f663b1c000013') },
        callback=self._on_response )

  def _on_response(self, response, error):
    if error:
      raise tornado.web.HTTPError(500)
    self.render('list.html', data=response, price='', postcode='', dates=self.get_dates(), postcodes=self.get_postcodes() )



# to redirect log file run python with : --log_file_prefix=mylog
def main():
  tornado.options.parse_command_line()
  http_server = tornado.httpserver.HTTPServer(Application())
  http_server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
  main()
