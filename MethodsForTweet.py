from beautifultable import BeautifulTable
import sys
import time
import json
import io
from functools import partial
from urllib2 import URLError
from httplib import BadStatusLine
import twitter
from collections import Counter
from IPython import embed

#LOGIN####################################################################
def oauth_login():
  CONSUMER_KEY = 'J0ampc57qwuH9GFgqwHRGv1sc'
  CONSUMER_SECRET = '5wov4YJhPNgl1ir2PoDkhxhBxvKziWJHIb924dj0UoLHoMllL9'
  OAUTH_TOKEN = '871057036515000321-iiOARqB6lODIY0gIkj7lijd0TXJqz0m'
  OAUTH_TOKEN_SECRET = 'NPyhkMCmxUyh1g20F1789TTjLyIr8F7PbpCmPzlFkWBnk'

  auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                             CONSUMER_KEY, CONSUMER_SECRET)
  twitter_api = twitter.Twitter(auth=auth)
  return twitter_api

#BUSCAR_TWEET############################################################
def twitter_search(twitter_api, q, max_results, **kw):
  search_results = twitter_api.search.tweets(q=q, count=100, **kw)
    
  statuses = search_results['statuses']

  max_results = min(1000, max_results)
  tweet_count = 0

  for _ in range(10):
      try:
          next_results = search_results['search_metadata']['next_results']
      except KeyError, e: 
          break
          
      kwargs = dict([ kv.split('=') 
                      for kv in next_results[1:].split("&") ])
      
      search_results = twitter_api.search.tweets(**kwargs)
      statuses += search_results['statuses']
      
      tweet_count += 100
      print tweet_count
      
      if len(statuses) > max_results: 
          break
          
  return statuses

#HACER UNA PETICION A TWITTER###############################################

def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):

        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e

        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429:
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
                (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    wait_period = 2
    error_count = 0

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise

#OBTENER IDS DE SEGUIDORES#######################################################

def get_friends_followers_ids(twitter_api, screen_name=None, user_id=None,
                              #friends_limit=maxint, followers_limit=maxint):
                              friends_limit=100, followers_limit=100):
                              #friends_limit, followers_limit):

    assert (screen_name != None) != (user_id != None), \
    "Must have screen_name or user_id, but not both"

    get_friends_ids = partial(make_twitter_request, twitter_api.friends.ids, count=5000)
    get_followers_ids = partial(make_twitter_request, twitter_api.followers.ids, count=5000)

    friends_ids, followers_ids = [], []

    for twitter_api_func, limit, ids, label in [
                    [get_friends_ids, friends_limit, friends_ids, "friends"],
                    [get_followers_ids, followers_limit, followers_ids, "followers"]
                ]:

        if limit == 0: continue

        cursor = -1
        while cursor != 0:
            if screen_name:
                response = twitter_api_func(screen_name=screen_name, cursor=cursor)
            else: # user_id
                response = twitter_api_func(user_id=user_id, cursor=cursor)

            if response is not None:
                ids += response['ids']
                cursor = response['next_cursor']

            if len(ids) >= limit or response is None:
                break
    return friends_ids[:friends_limit], followers_ids[:followers_limit]

#####Guardar en un texto plano
def save_json(filename, data):
  #with io.open('resources/ch09-twittercookbook/{0}.json'.format(filename),
  with io.open('date.json'.format(filename),
               'w', encoding='utf-8') as f:
    f.write(unicode(json.dumps(data, ensure_ascii=False)))


#####Leer De un texto Plano
def load_json(filename):
  with io.open('date.json'.format(filename),
               encoding='utf-8') as f:
    return f.read()
##################################
def get_friends_profile(twitter_api, screen_names=None, user_ids=None):
    assert (screen_names != None) != (user_ids != None), \
    "Must have screen_names or user_ids, but not both"

    table = BeautifulTable()
    table.column_headers = ["NOMBRE", "SCREEN NAME", "UBICACION", "NUM SEGUIDORES"]
    items_to_info = {}
    items = screen_names or user_ids
    while len(items) > 0:
        items_str = ','.join([str(item) for item in items[:100]])
        items = items[100:]

        if screen_names:
            response = make_twitter_request(twitter_api.users.lookup,
                                            screen_name=items_str)
        else: # user_ids
            response = make_twitter_request(twitter_api.users.lookup,
                                            user_id=items_str)
        print 'Tus amigos son: '
        for key in response:
          name = key['name']
          screen_name = key['screen_name']
          location = key['location']
          seguidores = key['followers_count']
          table.append_row([name.encode('utf-8'), screen_name.encode('utf-8'), location.encode('utf-8') , seguidores ])
    #print table
    return table
#HERE
##################################
def get_followers_profile(twitter_api, screen_names=None, user_ids=None):
    assert (screen_names != None) != (user_ids != None), \
    "Must have screen_names or user_ids, but not both"

    table = BeautifulTable()
    table.column_headers = ["NOMBRE", "SCREEN NAME", "UBICACION", "NUM SEGUIDORES"]
    items_to_info = {}
    items = screen_names or user_ids
    while len(items) > 0:
        items_str = ','.join([str(item) for item in items[:100]])
        items = items[100:]

        if screen_names:
            response = make_twitter_request(twitter_api.users.lookup,
                                            screen_name=items_str)
        else: # user_ids
            response = make_twitter_request(twitter_api.users.lookup,
                                            user_id=items_str)
        print 'tus seguidores son: '
        for key in response:
          #print "nombre: " + key['name'] + "| su twitter es:  " + key['screen_name'] + 
          #"| ubicacion: "+ key['location'] + "seguidores: " + str(key['followers_count'])
          name = key['name']
          screen_name = key['screen_name']
          location = key['location']
          seguidores = key['followers_count']
          table.append_row([name.encode('utf-8'), screen_name.encode('utf-8'), location.encode('utf-8') , seguidores ])
    print table
          

