import os
from google.appengine.ext import ndb
import logging
from protorpc import messages #enums
import json


class Configurations(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    value = ndb.StringProperty(indexed=False)
    type = ndb.StringProperty(indexed=False)

    ContentJSON = 'application/json'
    ContentText = 'text/plain'

    
    @staticmethod
    def get(name):  
       val = Configurations.query(Configurations.name == name).get()
       if val == None or val == '':
          return val
       else:
        if val.type == Configurations.ContentJSON:
           body = json.loads(val.value)
           ret = json.dumps(body, sort_keys=True, indent=4)
        else:
           ret = val.value

        return {'type' : val.type, 'value' : ret}
           


    @staticmethod
    def store(name, type, value):   

        if type != Configurations.ContentJSON and type != Configurations.ContentText:
          return 400;
        else:

          if type == Configurations.ContentJSON:

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
            ds = Configurations(name = name, value = jsonStr, type=type)
            ds.put()
          else:
            ds = Configurations(name = name, value = value, type=type)
            ds.put()

          return 200

  

   
       
       
      

   



 
    