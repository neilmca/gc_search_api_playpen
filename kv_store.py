#!/usr/bin/python
#
# Copyright 2011 Google Inc. All Rights Reserved.

"""A simple guest book app that demonstrates the App Engine search API."""

import logging
from cgi import parse_qs
from datetime import datetime
import re
import random
import os
import string
import urllib
from urlparse import urlparse
from configuration import Configurations
import json
import webapp2



# _ENCODE_TRANS_TABLE = string.maketrans('-: .@', '_____')

class BaseHandler(webapp2.RequestHandler):
    """The other handlers inherit from this class.  Provides some helper methods
    for rendering a template."""

    @webapp2.cached_property
    def jinja2(self):
      return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, template_args):
      self.response.write(self.jinja2.render_template(filename, **template_args))


class MainPage(BaseHandler):
    """Handles search requests for comments."""



    def get(self):
        """Handles a get request with a query."""
        self.response.write(' POST or GET to /configuration?key=[key]')

class ConfigurationHandler(BaseHandler):
    """Handles requests to index comments."""

    def put(self):
        """Handles a post request."""
 

          

        key = self.request.get('key')
        body = None        
        if key == None or key == '':
             self.response.write('key not specified')
             return


        #

        body = self.request.body
        if body == None or body =='':
            self.response.write('body not specified')
            return

        
        if self.request.content_type != "application/json" and self.request.content_type != Configurations.ContentText:
            webapp2.abort(400, 'invalid content_type only application/json and text/plain are supported')      
        else:
            resp = Configurations.store(key, self.request.content_type, body)

        if resp != 200:
            webapp2.abort(resp, 'error writing key-value')  


        

    def get(self):
        """Handles a post request."""
        #key = self.request.get_json('key')
        key = self.request.get('key')
        val = None
        if key != None:
            val = Configurations.get(key)

        if val == None or val == '':
            self.response.write('key not found=%s' % key)
            return

        logging.info(val)
        self.response.headers['Content-Type'] = val['type'].encode('utf8')
        self.response.write(val['value'])

logging.getLogger().setLevel(logging.DEBUG)


application = webapp2.WSGIApplication(
    [('/', MainPage),
     ('/configuration', ConfigurationHandler)],
    debug=True)


