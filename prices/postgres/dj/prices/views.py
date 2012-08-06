from datetime import datetime
from django.http import HttpResponse
from django.template.context import Context, RequestContext
from django.shortcuts import render_to_response

import re

from prices.models import HousePrice

#class Dates:
distinct_dates = None
distinct_postcode = None

def get_distinct_dates():
  global distinct_dates
  if not distinct_dates:
	distinct_dates = HousePrice.objects.values_list('dateadded', flat=True).distinct()
  return distinct_dates


def get_distinct_postcodes():
  global distinct_postcode
  if not distinct_postcode:
	distinct_postcode = HousePrice.objects.values_list('postcode_part', flat=True).distinct().extra(order_by = ['postcode_part'])

  return distinct_postcode

def get_date(request):
  date = request.POST["date"].split()[0]
  return datetime.strptime(date, "%Y-%m-%d" )

def index(request):
  house_list = []
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
  houses = HousePrice.objects.get(pk=53)

  c = RequestContext(request, {
    'house_list':[houses],
    'dates': get_distinct_dates(),
    'postcodes':get_distinct_postcodes()
  })
  return render_to_response('houseprice_list.html', c)
