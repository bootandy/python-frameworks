# Create your views here.
from datetime import datetime
from django.http import HttpResponse
import re
from django.template.context import Context, RequestContext
import pymongo
from models import HousePrice
from django.shortcuts import render_to_response
from django_mongodb_engine.contrib import MongoDBManager


# Hack to fix bug - confusion over pymongo & bson objectids
import sys
import bson.objectid
pymongo.objectid = bson.objectid
sys.modules["pymongo.objectid"] = bson.objectid
from bson.objectid import ObjectId


#class Dates:
distinct_dates = None
distinct_postcode = None

def get_distinct_dates():
  global distinct_dates

  if not distinct_dates:
    sync_connection = pymongo.Connection('localhost', 27017)
    sync_db = sync_connection ["houseprices"]
    distinct_dates = sync_db.houses.distinct( 'dateadded')

  return distinct_dates


def get_distinct_postcodes():
  global distinct_postcode

  if not distinct_postcode:
    sync_connection = pymongo.Connection('localhost', 27017)
    sync_db = sync_connection ["houseprices"]
    distinct_postcode = sync_db.houses.distinct( 'postcode_part')
    distinct_postcode.sort()

  return distinct_postcode


def get_date(request):
  date = request.POST["date"].split()[0]
  return datetime.strptime(date, "%Y-%m-%d" )


def hi(request):
  return HttpResponse("Hello World")

def index(request):
  house_list = [] #HousePrice.objects.all().order_by('-dateadded')
  c = RequestContext(request, {
    'house_list':[],
    'dates': get_distinct_dates(),
    'postcodes':get_distinct_postcodes()
  })
  return render_to_response('houseprice_list.html', c)

def price(request):
  price =  int(request.POST["price"])

  houses = HousePrice.objects.filter(price=price).filter(dateadded=get_date(request)).all()

  c = RequestContext(request, {
    'house_list':houses,
    'dates': get_distinct_dates(),
    'postcodes':get_distinct_postcodes()
  })
  #data = self.db.houses.find({}).sort( 'address' )
  return render_to_response('houseprice_list.html', c)

def postcode(request):
  postcode =  request.POST["postcode"]

  houses = HousePrice.objects.filter(postcode_part=postcode).filter(dateadded=get_date(request)).all()

  c = RequestContext(request, {
    'house_list':houses,
    'dates': get_distinct_dates(),
    'postcodes':get_distinct_postcodes()
  })
  #data = self.db.houses.find({}).sort( 'address' )
  return render_to_response('houseprice_list.html', c)

def single(request):

  houses = HousePrice.objects.raw_query({'_id':ObjectId('4facedc7283f663b1c000013')} )

  c = RequestContext(request, {
    'house_list':houses,
    'dates': get_distinct_dates(),
    'postcodes':get_distinct_postcodes()
  })
  return render_to_response('houseprice_list.html', c)
