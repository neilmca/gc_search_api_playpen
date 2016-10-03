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
    type = ndb.StringProperty(indexed=False)
    value = ndb.StringProperty(indexed=False)

    ContentJSON = 'application/json'
    ContentText = 'text/plain'

    
    @staticmethod
    def get(community, platform, app_version, property_set_version = ''):  

       results = Properties.query(Properties.community == community, Properties.platform == platform, Properties.app_version == app_version, Properties.property_set_version == property_set_version).fetch()

       properties = []
       for res in results:
          if res.type == Properties.ContentJSON:
               body = json.loads(res.value)
               val = body
          else:
               val = res.value
          properties.append({
            'type' : res.type,
            'key' : res.name,
            'value' : val,
            })
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

       logging.info(jObj)
       return json.dumps(jObj,indent = 2, sort_keys=True, separators=(',', ': '))


           


    @staticmethod
    def put_key(community, platform, app_version, name, type, value, property_set_version = ''):   

        if property_set_version == '':
          property_set_version = 'default'

        if type != Properties.ContentJSON and type != Properties.ContentText:
          return 400;
        else:

          if type == Properties.ContentJSON:

            try:
                body = json.loads(value)
            except Exception, e:
                logging.exception(e)            
                return 400
            else:
                pass
            finally:
                pass

            jsonStr = json.dumps(body, sort_keys=True, indent=4)
            value = jsonStr

          #create hash of fields to form DS key so that we don't create new keys but overwrite existing
          hash_key = str(hashlib.sha1(community + platform + app_version + property_set_version + name).hexdigest())
          ds = Properties(community=community, platform=platform, app_version=app_version, property_set_version=property_set_version, name=name, type=type, value=value, id = hash_key)
          ds.put()

          return 200

  

   
       
       
      

   



 
    