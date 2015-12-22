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

import webapp2
from webapp2_extras import jinja2

from google.appengine.api import search
from google.appengine.api import users

ARTISTS = ("Editors", "Oasis", "Phil Collins", "The Bangles", "Kenny Logins",  "R.E.M.", "Buzzcocks", "Alice Cooper", "The Enemy", "Rolling Stones")
TRACKS = ("Dice", "An End as a Start", "Posion", "Disarm", "No Time For Tears",  "Cornflake Girl", "The End", "The Beginning", "Doll Parts", "the end of the beginning")
ALTERNATE = ("The weather is really hot", "Really hot weather is a pain")


_INDEX_NAME = 'track'

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

        uri = urlparse(self.request.uri)
        query = ''
        if uri.query:
            query = parse_qs(uri.query)
            query = query['query'][0]

        # sort results by author descending
        expr_list = [search.SortExpression(
            expression='title', default_value='',
            direction=search.SortExpression.DESCENDING)]
        # construct the sort options
        sort_opts = search.SortOptions(
             expressions=expr_list)
        query_options = search.QueryOptions(
            limit=3,
            sort_options=sort_opts)
        #query_obj = search.Query(query_string=query, options=query_options)

        #if query string has "" then it is a phrase search. Remove first
        logging.info('query start = %s' % query)

        doResultsSetFilter = False
        if len(query) > 0 and query[0] == '"':
            doResultsSetFilter = True

        #trim initial "
        query = re.sub('^"', '', query)
        #trim trailing "
        query = re.sub('"$', '', query)

        logging.info('query end = %s, doResultsSetFilter = %s' % (query, doResultsSetFilter))

        query_obj = search.Query(query_string=query) #NMC without options
        results = search.Index(name=_INDEX_NAME).search(query=query_obj)

        resultCount = len(results.results)
        resultList = results
        #do secoond filter it we had removed the ""
        if doResultsSetFilter:
            secondaryFilter = []
            for scored_document in results:
                if query in scored_document.field('title').value:
                    logging.info('MATCHED %s' % scored_document.field('title').value)
                    secondaryFilter.append(scored_document)
                else:
                    logging.info('NOT MATCHED %s' % scored_document.field('title').value)
            resultCount = len(secondaryFilter)
            resultList = secondaryFilter
            logging.info('secondaryFilter count %d' % resultCount)
            logging.info('secondaryFilter  %s' % resultList)



        
        template_values = {
            'results': resultList,
            'number_returned': resultCount,
        }
        self.render_template('index.html', template_values)


def CreateTrackDocument(id, title, artist, lite):
    """Creates a search.Document from content written by the author."""
   
    if lite == True:
        exploded = tokenize_phrase(title)
    else:
        exploded = tokenize_phrase_gennasway(title)    
    
    return search.Document(doc_id =id,
        fields=[search.TextField(name='title', value=title),
                search.TextField(name='titleexploded', value=exploded),
                search.TextField(name='artist', value=artist),
                search.DateField(name='date', value=datetime.now().date())])

def tokenize_phrase_gennasway(phrase):
    a = []

    a.append(phrase) #add full phrase
    if len(phrase) > 2:
        for i in range(0, len(phrase)-2):
            if phrase[i] == ' ':
                continue
            for j in range(i+2,  len(phrase)+1):
                a.append(phrase[i:j])        
    
    return ','.join(a)

def tokenize_phrase(phrase):
    a = []
    a.append(phrase) #add full phrase
    for word in phrase.split():
        a.append(tokenize_phrase_gennasway(word))
    
    return ','.join(a)


def GenerateTrackDataAndIndex(count):
    keyprefix = 'key%s'

    for index in range(0, count):
        k1 = re.sub('0.', '', str(random.random()))
        trackid1 = keyprefix % k1

        k2 = re.sub('0.', '', str(random.random()))
        trackid2 = keyprefix % k2

        tracktitle = random.choice(TRACKS)
        artist =  random.choice(ARTISTS)

        search.Index(name=_INDEX_NAME).put(CreateTrackDocument(trackid1, tracktitle, artist, True))
        #search.Index(name=_INDEX_NAME).put(CreateTrackDocument(trackid2, tracktitle, artist, False))

def GenerateFixedTrackDataAndIndex():
    keyprefix = 'key%s'

    for index in range(0, 10):
        k1 = re.sub('0.', '', str(random.random()))
        trackid1 = keyprefix % k1

        k2 = re.sub('0.', '', str(random.random()))
        trackid2 = keyprefix % k2

        tracktitle = TRACKS[index]
        artist =  ARTISTS[index]

        search.Index(name=_INDEX_NAME).put(CreateTrackDocument(trackid1, tracktitle, artist, True))
        #search.Index(name=_INDEX_NAME).put(CreateTrackDocument(trackid2, tracktitle, artist, False))

def GenerateFixedAlternateDataAndIndex():
    keyprefix = 'key%s'

    for index in range(0, len(ALTERNATE)):
        k1 = re.sub('0.', '', str(random.random()))
        trackid1 = keyprefix % k1

        k2 = re.sub('0.', '', str(random.random()))
        trackid2 = keyprefix % k2

        tracktitle = ALTERNATE[index]
        artist =  ARTISTS[index]

        search.Index(name=_INDEX_NAME).put(CreateTrackDocument(trackid1, tracktitle, artist, True))
        #search.Index(name=_INDEX_NAME).put(CreateTrackDocument(trackid2, tracktitle, artist, False))


class Comment(BaseHandler):
    """Handles requests to index comments."""

    def post(self):
        """Handles a post request."""
 

          

        content = self.request.get('content')
        query = self.request.get('search')
        tracksToAdd = 0

        try:
            tracksToAdd = int(self.request.get('tracks'))
        except:
            pass
        


        logging.info('content = %s' % content)
        logging.info('query = %s' % query)
        logging.info('tracksToAdd = %d' % tracksToAdd)

        
        if tracksToAdd > 0:
            #GenerateFixedTrackDataAndIndex()
            #GenerateTrackDataAndIndex(tracksToAdd)
            GenerateFixedAlternateDataAndIndex()
        if query:
            self.redirect('/?' + urllib.urlencode(
                #{'query': query}))
                {'query': query.encode('utf-8')}))
        else:
            self.redirect('/')

logging.getLogger().setLevel(logging.DEBUG)


application = webapp2.WSGIApplication(
    [('/', MainPage),
     ('/sign', Comment)],
    debug=True)


