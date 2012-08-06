Alias /site_media/ "/home/andy/dev/python/python-frameworks/prices/django/"
<Directory "/home/andy/dev/python/python-frameworks/prices/django/">
Order allow,deny
Options Indexes
Allow from all
IndexOptions FancyIndexing
</Directory>

Alias /yui/ "/home/andy/dev/python/python-frameworks/prices/django/build/"
<Directory "/home/andy/dev/python/python-frameworks/prices/django/build">
Order allow,deny
Options Indexes
Allow from all
IndexOptions FancyIndexing
</Directory>

Alias /media/ "/home/andy/dev/python/python-frameworks/prices/django/trunk/django/contrib/admin/media/"
<Directory "/home/andy/dev/python/python-frameworks/prices/django/trunk/django/contrib/admin/media">
Order allow,deny
Options Indexes
Allow from all
IndexOptions FancyIndexing
</Directory>


WSGIScriptAlias / "/home/andy/dev/python/python-frameworks/prices/django/django.wsgi"

<Directory "/home/andy/dev/python/python-frameworks/prices/django/apache">
Allow from all
</Directory>