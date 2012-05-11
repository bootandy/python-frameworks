import datetime
import pymongo
import re

# from twisted.internet import epollreactor
# epollreactor.install()

from twisted.internet.defer import Deferred
from twisted.web import resource, server
from twisted.web._flatten import flattenString
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

from twisted.web.server import NOT_DONE_YET
from twisted.web.template import Element, renderer, XMLFile
import txmongo
from twisted.internet import defer

from simple_query import *

#MONGO_SERVER = '192.168.1.68'
MONGO_SERVER = 'localhost'



class ExampleElement(Element):
  loader = XMLFile(file('templates/basic.xml'))

  def __init__(self, request, db, dates, postcodes):
    Element.__init__(self)

    self.request = request
    self.db = db
    self.postcodes = postcodes
    self.dates = dates

  def get_date_from_request(self):
    return datetime.datetime.strptime(self.request.args["date"][0], "%Y-%m-%d %H:%M:%S" )


  def _on_error_response(self, response, error, message):
    if error:
      print "error "+message
    print "response! "+message


  #  @renderer
  def _all_data_callback(self, data, error, tag):
    self.data_count = len(data)
    if data:
      for d in data:
        yield tag.clone().fillSlots( data_price=str(d['price']), data_address=d['address'] )

      #
  @renderer
  def date_dropdown(self, request, tag):
    #print "calling date_dropdown"

    for d in self.dates:
      yield tag.clone().fillSlots(date=str(d))


  @renderer
  def postcodes_dropdown(self, request, tag):
    #print "calling date_dropdown"
    for d in self.postcodes:
      yield tag.clone().fillSlots(postcode=str(d))


  @renderer
  def price(self, request, tag):
    if "price" in self.request.args:
      return tag( self.request.args['price'] )
    return tag( '' )


  @renderer
  def postcode(self, request, tag):

    if "postcode" in self.request.args:
      return tag( self.request.args['postcode'] )
    return tag( '' )

  @renderer
  def datacount(self, request, tag):
    try:
      return tag.clone().fillSlots( datacount = str(self.data_count) )
    except AttributeError:
      return tag('')


class PriceExampleElement(ExampleElement):
  @renderer
  def all_data(self, request, tag):

    search = {}
    try :
      search['dateadded'] = self.get_date_from_request()
      pass
    except Exception as e:
      print "no datadded"
      print e
      return tag.clone().fillSlots( data_price='', data_address='' )

    price =  int(self.request.args['price'][0])
    search ['price'] = price

    #f = txmongo.filter.sort( txmongo.filter.ASCENDING("address") )
    #d = self.db.find(search, filter=f)
    d = self.db.find(search)

    d.addCallback(self._all_data_callback, request, tag)
    d.addErrback(self._on_error_response, request, "this is passed as a param")
    return d

class PostcodeExampleElement(ExampleElement):
  @renderer
  def all_data(self, request, tag):

    search = {}
    try :
      search['dateadded'] = self.get_date_from_request()
      pass
    except Exception as e:
      print "no datadded"
      print e
      return tag.clone().fillSlots( data_price='', data_address='' )

    postcode =  self.request.args['postcode'][0]
    search ['postcode_part'] = postcode

    d = self.db.find(search)

    d.addCallback(self._all_data_callback, request, tag)
    d.addErrback(self._on_error_response, request, "this is passed as a param")
    return d




class PostcodeElementResource(Resource):
  isLeaf = True

  def __init__(self, dates, postcodes, db):
    Resource.__init__(self)
    self.db = db
    self.dates = dates
    self.postcodes = postcodes

  def render_GET(self, request):
    #print 'ElementResource' + request
    d = flattenString(request, PostcodeExampleElement(request, self.db, self.dates, self.postcodes))

    def complete_request(html):
      request.write(html)
      request.finish()

    d.addCallback(complete_request)
    return NOT_DONE_YET

  def render_POST(self, request):
    d = flattenString(request, PostcodeExampleElement(request, self.db, self.dates, self.postcodes))

    def complete_request(html):
      request.write(html)
      request.finish()

    d.addCallback(complete_request)
    return NOT_DONE_YET

class PriceElementResource(Resource):
  isLeaf = True

  def __init__(self, dates, postcodes, db):
    Resource.__init__(self)
    self.db = db
    self.dates = dates
    self.postcodes = postcodes

  def render_GET(self, request):
    #print 'ElementResource' + request
    d = flattenString(request, PriceExampleElement(request, self.db, self.dates, self.postcodes))

    def complete_request(html):
      request.write(html)
      request.finish()

    d.addCallback(complete_request)
    return NOT_DONE_YET

  def render_POST(self, request):
    d = flattenString(request, PriceExampleElement(request, self.db, self.dates, self.postcodes))

    def complete_request(html):
      request.write(html)
      request.finish()

    d.addCallback(complete_request)
    return NOT_DONE_YET


#class FaviconHandler(Resource):
#  def render_GET(self, request):
#    request.setResponseCode(404)

class HelloHandler(Resource):

  def render_GET(self, request):
    #print "hello handler"
    d = flattenString(request,"Hello World")

    def complete_request(html):
      request.write(html)
      request.finish()

    d.addCallback(complete_request)
    return NOT_DONE_YET


def main():
  #connect_mongo().addCallback(setup())
  setup()




def setup():
  _db = txmongo.lazyMongoConnectionPool(MONGO_SERVER, 27017)
  collection = _db.houseprices.houses
  root = resource.Resource()

  # Can not do a 'distinct' query with async mongo - so use a sync connection for this
  sync_connection = pymongo.Connection(MONGO_SERVER, 27017, max_pool_size=10)
  sync_db = sync_connection ["houseprices"]

  dates = sync_db.houses.distinct( 'dateadded')

  legal_postcodes_results = sync_db.houses.distinct( 'postcode_part')

  postcodes = []
  for p in legal_postcodes_results:
    postcodes.append(p)
  postcodes.sort()

  sync_connection.close()


  #root = ElementResource(db)
  #root.putChild("/favicon.ico", FaviconHandler)
  root.putChild("/", PriceElementResource(dates, postcodes, collection))
  root.putChild("price", PriceElementResource(dates, postcodes, collection))
  root.putChild("postcode", PostcodeElementResource(dates, postcodes, collection))
  root.putChild("single", SingleElementResource(dates, collection))
  root.putChild("hello", HelloHandler())
  factory = Site(root)
  reactor.listenTCP(8881, factory)
  reactor.run()

def mini(self, data, error):
  print "hello"

if __name__ == '__main__':
  print "hello"
  main()

