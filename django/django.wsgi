import os, sys;  #raise Exception(sys.path)

sys.path.append('/home/andy/dev/python/houseprices/dj/hp')
sys.path.append('/home/andy/dev/python/houseprices/dj')
sys.path.append('/home/andy/dev/python/houseprices')
sys.path.append('/home/andy/dev/python/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'dj.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# import sys; 

# def application(environ, start_response):
#     status = '200 OK'
#     output = 'Hello World!'

#     response_headers = [('Content-type', 'text/plain'),
#                         ('Content-Length', str(len(output)))]
#     start_response(status, response_headers)


#     print >> sys.stderr, 'sys.prefix = %s' % repr(sys.prefix)
#     print >> sys.stderr, 'sys.path = %s' % repr(sys.path)

#     return [output]
#     