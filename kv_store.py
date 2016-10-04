#!/usr/bin/python
#


import logging
from cgi import parse_qs
from datetime import datetime
import re
import random
import os
import string
import urllib
from urlparse import urlparse
from properties_store import Properties
import json
import webapp2
from serving_property_set_store import ServingPropertSet



# _ENCODE_TRANS_TABLE = string.maketrans('-: .@', '_____')

class BaseHandler(webapp2.RequestHandler):
    """The other handlers inherit from this class.  Provides some helper methods
    for rendering a template."""

    @webapp2.cached_property
    def jinja2(self):
      return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, template_args):
      self.response.write(self.jinja2.render_template(filename, **template_args))

def split_path(path):
    #strip leading /
    path = re.sub('^/', '', path)
    
    #if there is still a '/ then it means community lookup code is included
    path_split = path.split('/')

    if len(path_split) < 4:
        #should be something like /mtv1/ios/3.2/properties
        webapp2.abort(400, detail="invalid number of params")

    return {'community':path_split[0], 'platform': path_split[1], 'app_version':path_split[2]}

class PropertiesHandler(BaseHandler):
    """Handles search requests for comments."""

    #Example: GET /mtv1/ios/3.2/properties - gets property set for serving version
    #Example: GET /mtv1/ios/3.2/properties?version={v} - gets named version property set
    #Example: POST /mtv1/ios/3.2/properties?&version={v} - add keys to specific version - body contains keys in json

    def get(self):
        """Handles a get request to get all keys in property set."""
        
        path_split = split_path(self.request.path)

        #get serving version
        version = self.request.get('version')
        if version == None or version == '':
            resp = ServingPropertSet.get(community=path_split['community'], platform = path_split['platform'], app_version = path_split['app_version'])
            version = resp['serving_version']

        resp = Properties.get(community=path_split['community'], platform = path_split['platform'], app_version = path_split['app_version'], property_set_version = version)

        self.response.write(resp)

    def post(self):
        """Handles a post request to add keys"""   

        path_split = split_path(self.request.path)     

        body = None 
        body = self.request.body
        if body == None or body =='':
            self.response.write('body not specified')
            return

        version = self.request.get('version')
        if version == None or version == '':
            webapp2.abort(400, 'version not specified')      
        
        if self.request.content_type != Properties.ContentJSON:
            webapp2.abort(400, 'invalid content_type only application/json is supported')      
        else:
            #load into json
            keys = json.loads(body)
            resp = Properties.put_keys(community=path_split['community'], platform = path_split['platform'], app_version = path_split['app_version'], keys = keys, property_set_version = version)

        if resp != 200:
            webapp2.abort(resp, 'error writing key-value')  

    
class ServingPropertySetHandler(BaseHandler):
    """Handles search requests for comments."""

    #Example: GET /mtv1/ios/3.2/servingVersion
    #Example: GET /mtv1/ios/3.2/servingVersion
    #Example: PUT /mtv1/ios/3.2/servingVersion?version={v}

    def get(self):
        """Handles a get request to get the serving property set"""
        
        path_split = split_path(self.request.path)
        resp = ServingPropertSet.get(community=path_split['community'], platform = path_split['platform'], app_version = path_split['app_version'])
        self.response.write(json.dumps(resp,indent = 2, sort_keys=True, separators=(',', ': ')))

    def put(self):
        """Handles a get request to get the serving property set"""

        version = self.request.get('version') 
        if version == None or version == '':
             self.response.write('version not specified')
             return
        
        path_split = split_path(self.request.path)
        resp = ServingPropertSet.putVersion(community=path_split['community'], platform = path_split['platform'], app_version = path_split['app_version'], version = version)
        

        self.response.write(resp)



class MainHandler(BaseHandler):
    """Handles search requests for comments."""



    def get(self):
        """Handles a get request with a query."""
        

        self.response.write('Main')

   
logging.getLogger().setLevel(logging.DEBUG)


application = webapp2.WSGIApplication(
    [('/.*/properties', PropertiesHandler),
     ('/.*/servingVersion', ServingPropertySetHandler),
     ('/.*', MainHandler)],
    debug=True)


