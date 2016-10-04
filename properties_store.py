import os
from google.appengine.ext import ndb
import logging
from protorpc import messages #enums
import json
import hashlib


class Properties(ndb.Model):
    community = ndb.StringProperty(indexed=True)
    platform = ndb.StringProperty(indexed=True)
    app_version = ndb.StringProperty(indexed=True)
    property_set_version = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=True)
    value = ndb.StringProperty(indexed=False)

    ContentJSON = 'application/json'
    ContentText = 'text/plain'

    
    @staticmethod
    def get(community, platform, app_version, property_set_version = ''):  

       results = Properties.query(Properties.community == community, Properties.platform == platform, Properties.app_version == app_version, Properties.property_set_version == property_set_version).fetch()

       properties = {}
       for res in results:
          val_json = json.loads(res.value)
          properties[res.name] = val_json['value']

       jObj = {
        'properties' : properties, 
        'meta': 
          {
          'community':community, 
          'platform':platform, 
          'app_version':app_version, 
          'version':property_set_version,
          'key_count': len(properties)
          }
        }

       return json.dumps(jObj,indent = 2, sort_keys=True, separators=(',', ': '))


           


    @staticmethod
    def put_keys(community, platform, app_version, keys, property_set_version = ''):   

        if property_set_version == '':
          property_set_version = 'default'

        for key in keys:
          kvp_json = {'key': key, 'value':keys[key]}
          kvp_str = json.dumps(kvp_json)
          #create hash of fields to form DS key so that we don't create new keys but overwrite existing
          hash_key = str(hashlib.sha1(community + platform + app_version + property_set_version + key).hexdigest())
          ds = Properties(community=community, platform=platform, app_version=app_version, property_set_version=property_set_version, name=str(key), value=kvp_str, id = hash_key)
          ds.put()

        return 200

  

   
       
       
      

   



 
    