import os, sys;  #raise Exception(sys.path)


#Calculate the path based on the location of the WSGI script.
apache_configuration= os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.dirname(project)
sys.path.append(workspace) 



sys.path.append('/home/andy/dev/python/python-frameworks/prices/django/hp')
sys.path.append('/home/andy/dev/python/python-frameworks/prices/django')
sys.path.append('/home/andy/dev/python/python-frameworks/prices')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

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