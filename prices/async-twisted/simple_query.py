import datetime
import pymongo
import re
from bson.objectid import ObjectId

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


class SingleElement(Element):
  loader = XMLFile(file('templates/simple.xml'))

  def __init__(self, request, db, dates):
    Element.__init__(self)
    self.request = request
    self.db = db
    self.dates = dates

  def get_date_from_request(self):
    return datetime.datetime.strptime(self.request.args["date"][0], "%Y-%m-%d %H:%M:%S" )

  @renderer
  def all_data(self, request, tag):

    search = {}
    # search['price'] = int(300000)
    # d = self.db.find( search )

    o = ObjectId('4f7b5cec283f660e89000000')
    search['_id'] = o
    d = self.db.find(search)
    #d = self.db.houses.find({'_id': ObjectId("4f7b5cec283f660e89000000") })

    d.addCallback(self._all_data_callback, request, tag)
    d.addErrback(self._on_error_response, request, "this is passed as a param")
    return d

  def _on_error_response(self, response, error, message):
    if error:
      print "error "+message
    print "response! "+message

  def _all_data_callback(self, data, error, tag):
    if data:
      for d in data:
        yield tag.clone().fillSlots( data_price=str(d['price']), data_address=d['address'] )

  @renderer
  def date_dropdown(self, request, tag):
    for d in self.dates:
      yield tag.clone().fillSlots(date=str(d))




class SingleElementResource(Resource):
  isLeaf = True

  def __init__(self, dates, db):
    Resource.__init__(self)
    self.db = db
    self.dates = dates

  def render_POST(self, request):
    return self.render_it(request)
  
  def render_GET(self, request):
    return self.render_it(request)

  def render_it(self, request):
    d = flattenString(request, SingleElement(request, self.db, self.dates))

    def complete_request(html):
      request.write(html)
      request.finish()

    d.addCallback(complete_request)
    return NOT_DONE_YET

    #self.db.houses.find({'_id': ObjectId('4f7b5cec283f660e89000000') },
#    self.render('list.html', data=response, price='', postcode='', dates=self.get_dates(), postcodes=self.get_postcodes() )
