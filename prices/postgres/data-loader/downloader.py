from time import sleep
import urllib2
from BeautifulSoup import BeautifulSoup
import re
import datetime
from pymongo import Connection


# run this first:
# export DJANGO_SETTINGS_MODULE=dj.settings
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "dj.settings"
from prices.models import HousePrice


ZOOPLA = "http://www.zoopla.co.uk/for-sale/property/london/sw1/westminster-belgravia-pimlico-victoria/?radius=5&q=sw1&page_size=50&include_sold=true&pn="

def get_components(links, index):
  price = ''
  for p in links[index].contents:
    if p.string:
      price += p.string
  return price

def convertPriceToInt(s):
  try:
    finds = re.findall('((\d+\,?)+)', s)
    value = finds[0][0]
    value = value.replace(',','')

    return int(value)
  except :
    return 0


def connect_mongo():
   con = Connection('localhost', 27017)
   database = con["houseprices"]
   return database

def connect_postgres():
  return None


def main():
  get_data()

def get_data():
  db = connect_mongo()
  houses = db['houses']

  fails = 0
  iterations = 0
  count = 50
  date = datetime.datetime.utcnow()
  date = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)

  while count > 0 and fails < 5:
    try:
      sleep(1)
      iterations += 1

      print "Iteration: "+str(iterations)

      page = urllib2.urlopen(ZOOPLA + str(iterations))
      soup = BeautifulSoup(page)

      count = 0

      for incident in soup('div', {'class' : 'listing-results-right' } ):
        links = incident('a')

        price = convertPriceToInt(get_components(links, 0))
        description = get_components(links, 1)
        addy =        get_components(links, 2)

        hp = HousePrice(
          description=description, 
          address=addy, 
          price=price, 
          dateadded=date,
          postcode_part=addy.split(" ")[-1],
        )
        hp.save()
        # houses.insert(
        #     {'description':description,
        #      'price':price,
        #      'address':addy,
        #      'postcode_part': addy.split(" ")[-1],
        #      'dateadded':date
        #   }
        # )
        print price

        count += 1

    except  urllib2.URLError as e:
      sleep(5)
      print "Fail - sleeping for 5s " + str(e)
      fails += 1


  print "all done"
  print "-----"

if __name__ == '__main__':
  main()
