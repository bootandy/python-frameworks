#!/usr/bin/python
from gevent.wsgi import WSGIServer
from application import application
print 'Serving on 8000...'
WSGIServer(('', 8000), application).serve_forever()

# export PYTHONPATH=~/dev/python/houseprices/
