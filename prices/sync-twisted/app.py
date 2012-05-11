import datetime
from bson.objectid import ObjectId
from pymongo.cursor import Cursor
import re
import pymongo
from twisted.web import resource
from twisted.web._flatten import flattenString
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.server import NOT_DONE_YET
from twisted.web.template import Element, renderer, XMLFile

MONGO_SERVER = 'localhost'


class DelayedResource(Resource):
  def _delayedRender(self, request):
    request.write("<html><body>Sorry to keep you waiting.</body></html>")
    request.finish()

  def _responseFailed(self, err, call):
    call.cancel()
    err(err, "Async response demo interrupted response")

  def render_GET(self, request):
    call = reactor.callLater(5, self._delayedRender, request)
    request.notifyFinish().addErrback(self._responseFailed, call)
    return NOT_DONE_YET




class ExampleElement(Element):
  loader = XMLFile(file('templates/basic.xml'))

  def __init__(self, request, db, dates, postcodes):
    Element.__init__(self)
    self.request = request
    self.db = db
    self.dates = dates
    self.postcodes = postcodes
    self.data = self.load_data()

  def get_date_from_request(self):
    return datetime.datetime.strptime(self.request.args["date"][0], "%Y-%m-%d %H:%M:%S" )


  @renderer
  def all_data(self, request, tag):
    if self.data:
      for d in self.data:
        yield tag.clone().fillSlots( data_price=str(d['price']), data_address=d['address'] )

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
    if self.data:
      return tag( str(self.data.count()) )
    return tag('')



class PostcodeElement(ExampleElement):
  def load_data(self):
    search = {}
    try :
      search['dateadded'] = self.get_date_from_request()
    except Exception as e:
      print "no datadded"
      print e
      return None

    postcode =  self.request.args['postcode'][0]
    search ['postcode_part'] = postcode

    return self.db.houses.find( search )

class PriceElement(ExampleElement):

  def load_data(self):
    search = {}
    try :
      search['dateadded'] = self.get_date_from_request()
    except Exception as e:
      print "no datadded"
      print e
      return None

    price =  int(self.request.args['price'][0])
    search ['price'] = price

    return self.db.houses.find( search )

class SingleElement(ExampleElement):
  def load_data(self):
    return self.db.houses.find({'_id': ObjectId('4facedc7283f663b1c000013') } )



class PostcodeElementResource(Resource):
  isLeaf = True

  def __init__(self, db, postcodes, dates):
    Resource.__init__(self)
    self.db = db
    self.dates = dates
    self.postcodes = postcodes

  def render_GET(self, request):
    #print 'ElementResource' + request
    d = flattenString(request, PostcodeElement(request, self.db, self.dates, self.postcodes))

    def complete_request(html):
      request.write(html)
      request.finish()

    d.addCallback(complete_request)
    return NOT_DONE_YET

  def render_POST(self, request):
    d = flattenString(request, PostcodeElement(request, self.db, self.dates, self.postcodes))

    def complete_request(html):
      request.write(html)
      request.finish()

    d.addCallback(complete_request)
    return NOT_DONE_YET


class PriceElementResource(Resource):
  isLeaf = True

  def __init__(self, db, postcodes, dates):
    Resource.__init__(self)
    self.db = db
    self.dates = dates
    self.postcodes = postcodes

  def render_GET(self, request):
    #print 'ElementResource' + request
    d = flattenString(request, PriceElement(request, self.db, self.dates, self.postcodes))

    def complete_request(html):
      request.write(html)
      request.finish()

    d.addCallback(complete_request)
    return NOT_DONE_YET

  def render_POST(self, request):
    d = flattenString(request, PriceElement(request, self.db, self.dates, self.postcodes))

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
  connection = pymongo.Connection(MONGO_SERVER, 27017, max_pool_size=1000)
  db = connection ["houseprices"]

  dates = db.houses.distinct( 'dateadded')

  legal_postcodes_results = db.houses.distinct( 'postcode_part')

  postcodes = []
  for p in legal_postcodes_results:
    postcodes.append(p)
  postcodes.sort()


  root = resource.Resource()
  #root = ElementResource(db)
  #root.putChild("/favicon.ico", FaviconHandler)
  root.putChild("/",        PriceElementResource(db, postcodes, dates))
  root.putChild("price",    PriceElementResource(db, postcodes, dates))
  root.putChild("postcode", PostcodeElementResource(db, postcodes, dates))
  root.putChild("hello",    HelloHandler())
  factory = Site(root)
  reactor.listenTCP(8880, factory)
  reactor.run()

if __name__ == '__main__':
  main()

