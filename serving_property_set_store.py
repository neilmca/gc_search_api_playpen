import os
from google.appengine.ext import ndb
import logging
from protorpc import messages #enums
import json
import hashlib

class ServingPropertSet(ndb.Model):
    community = ndb.StringProperty(indexed=True)
    platform = ndb.StringProperty(indexed=True)
    app_version = ndb.StringProperty(indexed=True)
    serving_version = ndb.StringProperty(indexed=False)
    
    @staticmethod
    def get(community, platform, app_version): 
       
       set = ServingPropertSet.query(ServingPropertSet.community == community, ServingPropertSet.platform == platform, ServingPropertSet.app_version == app_version).get()
       if set == None:
       	version = 'default'
       else:
       	version = set.serving_version

       resp = {
       	'community':set.community, 
        'platform':set.platform, 
        'app_version':set.app_version, 
        'serving_version': version,
       }
       return resp
       


    @staticmethod
    def putVersion(community, platform, app_version, version): 
       
       hash_key = str(hashlib.sha1(community + platform + app_version).hexdigest())
       ds = ServingPropertSet(community=community, platform=platform, app_version=app_version, serving_version=version, id = hash_key)
       ds.put()