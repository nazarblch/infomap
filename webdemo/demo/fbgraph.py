from django.http import HttpResponseRedirect
from django.utils.http import urlencode
import httplib
import json
from algorithms.ignatich.egonet import EgoNet

class FBGraphAPI:
  def __init__(self, FB_APP_ID, FB_APP_SECRET):
    if FB_APP_ID is None or FB_APP_SECRET is None: raise Exception("need fb app id and secret in settings")
    self.FB_APP_ID = FB_APP_ID
    self.FB_APP_SECRET = FB_APP_SECRET
    self.access_token = None
    self.last_redirect = None
    self.conn = None
    
  def load_session(self, sess):
    if 'last_redirect' in sess:
      self.last_redirect = sess['last_redirect']
    if 'access_token' in sess:
      self.access_token = sess['access_token']
  def save_session(self, sess):
    sess['last_redirect'] = self.last_redirect
    sess['access_token'] = self.access_token
    
  def acquire_token(self, req, redirect_uri):
    """Get access_token, returns None if ok or HttpResponseRedirect if redirect is required."""
    if self.access_token is not None:
      return None
    code = req.GET.get("code", None)
    if code is not None and code != "":
      if self.last_redirect is None:
	raise Exception("url with code, but no requests made")
      #FIXME: may not be the best way to handle this, but
      #       it's easier to save redirect_uri than to trim code and state from it
      if not redirect_uri.startswith(self.last_redirect):
	raise Exception("redirect_uri changed")
      conn = httplib.HTTPSConnection("graph.facebook.com")
      conn.request("GET", "/oauth/access_token?" + urlencode([("client_id", self.FB_APP_ID), ("redirect_uri", self.last_redirect), ("client_secret", self.FB_APP_SECRET), ("code", code)]))
      auth_resp = conn.getresponse()
      auth_resp_data = auth_resp.read()
      conn.close()
      self.last_redirect = None
      pref = "access_token="
      #FIXME: shouldn't ignore expires
      for p in auth_resp_data.split("&"):
        if p.startswith(pref):
          self.access_token = p[len(pref):]
          return None
      raise Exception("error receiving access_token, response: " + auth_resp_data)
    else:
      scope = "user_likes,friends_likes,user_hometown,friends_hometown,user_education_history,friends_education_history,user_work_history,friends_work_history,read_friendlists"
      auth_uri = "https://www.facebook.com/dialog/oauth?" + urlencode([("client_id", self.FB_APP_ID), ("redirect_uri", redirect_uri),("scope", scope), ("state", "somestate")])
      self.last_redirect = redirect_uri
      return HttpResponseRedirect(auth_uri)

      
  def get_access_token(self):
    return self.access_token


  def set_token(self, token):
    self.access_token = token
    
  def request(self, req_str):
    if self.conn is None:
      self.conn = httplib.HTTPSConnection("graph.facebook.com")
    self.conn.request("GET", req_str + "?" + urlencode([("access_token", self.access_token)]))
    auth_resp = self.conn.getresponse()
    res = json.load(auth_resp)
    #conn.close()
    
    return res

  def load_friends(self, user_id, fields="name,picture"):
    """returns array of dicts with u'name' and u'id' keys"""
    resp = self.request("/%s/friends&fields=%s" % (user_id, fields))
    if not resp.has_key("data"):
      raise Exception("failed to get friends of %s: %s" % (user_id, repr(resp)))
    return resp["data"]

  def load_user(self, user_id, fields="name,picture"):
    """returns array of dicts with u'name' and u'id' keys"""
    resp = self.request("/%s&fields=%s" % (user_id, fields))
    return resp

  def load_mutualfriends(self, u1, u2):
    """returns array of dicts with u'name' and u'id' keys"""
    resp = self.request("/%s/mutualfriends/%s" % (u1, u2))
    if not resp.has_key("data"):
      raise Exception("failed to get mutual friends of %s/%s: %s" % (u1, u2, repr(resp)))
    return resp["data"]

  def load_likes(self, user_id):
    resp = self.request("/%s/likes" % (user_id))
    if not resp.has_key("data"):
        raise Exception("failed to get likes of %s: %s" % (user_id, repr(resp)))
    return resp["data"]


  #FIXME: dirty hack, needed because cb's can't yield
  def load_egonet_progr(self):
    if self.access_token is None:
      raise Exception("access_token must be aquired first")
    g = EgoNet()
    g.access_token = self.access_token
    g.friends = self.load_friends("me", "name,picture,languages,gender,hometown,education,work")
    g.me = self.load_user("me", "name,picture,languages,gender,hometown,education,work")

    g.flists = self.request("/me/friendlists")["data"]
    g.flists_members = dict()
    for fl in g.flists:
      fl_id = fl["id"]
      g.flists_members[fl_id] = self.request("/%s/members" % fl_id)["data"]

    sz = len(g.friends)
    yield (0, sz)
    index_by_id = dict()
    ind = 0
    for f in g.friends:
      index_by_id[f["id"]] = ind
      ind += 1
    g.edges = list()
    ind = 0
    g.likes = []
    for f in g.friends:
      ffs = self.load_mutualfriends("me", f["id"])
      for ff in ffs:
        if index_by_id.has_key(ff["id"]):
          g.edges.append( (ind, index_by_id[ff["id"]]) )
        else:
          print "why can't we find a mutual friend????" #FIXME
      g.likes.append(self.load_likes(f["id"]))
      ind += 1
      yield (ind, sz)
    g.likes.append(self.load_likes("me"))
    
    yield g
    