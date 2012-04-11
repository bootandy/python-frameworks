# Python imports
import base64
import os

# Tornado imports
import re
import uuid
import datetime
from pymongo.cursor import Cursor
import time
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from tornado.web import url

# Third-party imports
import pymongo


define("port", default=8888, type=int)
define("config_file", default="app_config.yml", help="app_config file")

# Application class
class Application(tornado.web.Application):
  def __init__(self):
    #self.config = self._get_config()
    handlers = [
      url(r'/', IndexHandler, name='index'),
      url(r'/hello', HelloWorldHandler, name='hello'),
      url(r'/price', PriceHandler, name='price'),
      url(r'/postcode', PostcodeHandler, name='postcode'),
    ]

    #xsrf_cookies is for XSS protection add this to all forms: {{ xsrf_form_html() }}
    settings = {
      'static_path': os.path.join(os.path.dirname(__file__), 'static'),
      'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
      "cookie_secret":  base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
      #'xsrf_cookies': True,
      'debug':True,
      'log_file_prefix':"tornado.log"
    }

    tornado.web.Application.__init__(self, handlers,**settings) # debug=True ,
    # Connect to mongodb
    self.connection = pymongo.Connection('localhost', 27017, max_pool_size=1000)
    self.db = self.connection ["houseprices"]

    # we preload dates & postcode_parts
    self.legal_dates = self.db.houses.distinct( 'dateadded')

    legal_postcodes_results = self.db.houses.distinct( 'postcode_part')

    self.legal_postcodes = []
    for p in legal_postcodes_results:
      self.legal_postcodes.append(p)
    self.legal_postcodes.sort()

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
  def get(self):
    data = self.db.houses.find({'price':-999999})

    self.render('list.html', data=data, price='', postcode='', dates=self.get_dates(), postcodes=self.get_postcodes() )

  def post(self):
    return self.get()

class PriceHandler(BaseHandler):
  def post(self):
    price =  int(self.get_argument("price", 0))

    date = self.get_date()

    data = self.db.houses.find({'price':price, 'dateadded':date})

    self.render('list.html', data=data, price=price, postcode='', dates=self.get_dates(), postcodes=self.get_postcodes())

class PostcodeHandler(BaseHandler):
  def post(self):
    date = self.get_date()

    postcode =  self.get_argument("postcode", "unknown")
    data = self.db.houses.find({'postcode_part':postcode, 'dateadded':date} )

    self.render('list.html', data=data, price='', postcode=postcode, dates=self.get_dates(), postcodes=self.get_postcodes())


# to redirect log file run python with : --log_file_prefix=mylog
def main():
  tornado.options.parse_command_line()
  http_server = tornado.httpserver.HTTPServer(Application())
  http_server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
  main()
