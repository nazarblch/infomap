from django.forms.forms import BoundField
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django import forms
from django.template import RequestContext, loader
from django.core.cache import cache
from django.views.decorators.cache import never_cache
import os
import subprocess
import time
import threading

from fbgraph import *
import cdalgs
import pickle

class AlgForm(forms.Form):
  uid = forms.IntegerField(required=False, widget=forms.HiddenInput())
  alg = forms.ChoiceField(choices=())
  include_seed = forms.BooleanField(required=False)
  def __init__(self, *args, **kwargs):
    algs = kwargs.pop('algs', None)
    super(AlgForm, self).__init__(*args, **kwargs)
    if algs is not None:
      self._algs = algs
      self.fields['alg'].choices = [(ind, algs[ind].name) for ind in range(len(algs))]
  def clean(self):
    cleaned_data = super(AlgForm, self).clean()
    alg_index = cleaned_data.get("alg")
    include_seed = bool(cleaned_data.get("include_seed"))
    if alg_index is not None:
      alg_index = int(alg_index)
      alg = self._algs[alg_index]
      if (alg.fixed_include_seed is not None) and (alg.fixed_include_seed != include_seed):
        raise forms.ValidationError("Algorithm '" + alg.name + "' can't be executed with include_seed=" + str(include_seed))
    return cleaned_data

class Group:
  def __init__(self, form, name):
    self.name = name
    self.form = form
    self.fields = []
  def get_fields(self):
    for name, field in self.fields:
      yield BoundField(self.form, field, name)
class AlgFormW(forms.Form):
  uid = forms.IntegerField(required=False, widget=forms.HiddenInput())
  algw = forms.ChoiceField(choices=())
  include_seed = forms.BooleanField(required=False)
  def __init__(self, *args, **kwargs):
    algs = kwargs.pop('algs', None)
    simw_float_settings = kwargs.pop('float_settings', None)
    simw_float_settings_groups = kwargs.pop('float_settings_groups', None)
    super(AlgFormW, self).__init__(*args, **kwargs)
    if algs is not None:
      self.fields['algw'].choices = algs

    self.field_groups = []
    self.grouped_fields_names = set()
    if simw_float_settings_groups is not None:
      field_groups_names = list(set([v[0] for v in simw_float_settings_groups.itervalues()]))
      field_groups_names.sort()
      self.field_groups = []
      group_by_name = dict()
      for n in field_groups_names:
        g = Group(self, n)
        self.field_groups.append(g)
        group_by_name[n] = g

      for fid, fname, fdef in simw_float_settings:
        if simw_float_settings_groups.has_key(fid):
          groupname, comment = simw_float_settings_groups[fid]
          f = forms.FloatField(label=fname, help_text=comment)
          self.fields[fid] = f
          group_by_name[groupname].fields.append( (fid, f) )
          self.grouped_fields_names.add(fid)
        else:
          self.fields[fid] = forms.FloatField(label=fname)
    else:
      for fid, fname, fdef in simw_float_settings:
        self.fields[fid] = forms.FloatField(label=fname)


  def nongrouped_fields(self):
    for f in self.visible_fields():
      if f.name not in self.grouped_fields_names:
        yield f

  def field_groups(self):
    for g in self.field_groups:
      yield g


class ExecAlg(threading.Thread):
  def __init__(self, alg, net, include_seed):
    threading.Thread.__init__(self)
    self.comms = None
    self.comments = None
    self.comm_ws = None
    self.alg = alg
    self.net = net
    self.include_seed = include_seed
  def run(self):
    self.comms, self.comments, self.comm_ws = self.alg.execute(self.net, self.include_seed)

import traceback
from algorithms.ignatich.utils import get_nmi, maxind
#TODO: render_comms and render_comms_stored share a lot of code
def render_comms(req, gapi):
  try:
    t = loader.get_template('demo_head.html')
    c = RequestContext(req, {})
    yield t.render(c)

    #FIXME: can't save net in session, looks like we can't add any keys to session in this generator
    #FIXME: need some gc/serialization
    yield '<div id="load-status">loading egonet...</div>\n'
    nets = cache.get(req.session.session_key + ".net")
    if nets is not None:
      net = pickle.loads(nets)
      if net.access_token != gapi.access_token:
        net = None
    else:
      net = None
    if net is None:
      for x in gapi.load_egonet_progr():
        if isinstance(x, EgoNet):
          net = x
        else:
          yield '''<script type="text/javascript"> var e = document.getElementById('load-status'); e.innerHTML = "loading egonet...%s/%s"; </script>\n''' % (x[0], x[1])
      nets = pickle.dumps(net)
    cache.set(req.session.session_key + ".net", nets, 60*60)

    algs, algsw = cdalgs.create_algs(os.path.join(settings.SITE_ROOT, '..'))
    
    form = AlgForm(req.GET, algs=algs)
    formw_params = req.GET.copy()
    simw_float_settings = net.get_float_settings()
    #a hack, needed since bounded forms don't have default values in django
    for fid, fname, fdef in simw_float_settings:
      if not formw_params.has_key(fid):
        formw_params[fid] = str(fdef)
    formw = AlgFormW(formw_params, algs=[(ind, algsw[ind].name) for ind in range(len(algsw))], float_settings=simw_float_settings)
    user_comms = net.get_flists()
    user_comms_names = [fl["name"] for fl in net.flists]
    alg_tab_index = 0
    if req.GET.has_key("algw"):
      alg_tab_index = 1
    if form.is_valid():
      alg_index = int(form.cleaned_data['alg'])
      include_seed = bool(form.cleaned_data['include_seed'])

      alg = algs[alg_index]
    elif formw.is_valid():
      alg_tab_index = 1
      alg_index = int(formw.cleaned_data['algw'])
      include_seed = bool(formw.cleaned_data['include_seed'])
      sim_settings = dict()
      for fid, fname, fdef in simw_float_settings:
        sim_settings[fid] = float(formw.cleaned_data[fid])
      alg = algsw[alg_index]
      net.sim_settings = sim_settings
    else:
      alg = None

    if alg is not None:
      yield '''<script type="text/javascript"> var e = document.getElementById('load-status'); e.innerHTML = "executing '%s'"; </script>\n''' % (alg.name)
      tm_start = time.time()
      t = ExecAlg(alg, net, include_seed)
      t.start()
      while True:
        t.join(timeout=5)
        if not t.isAlive(): break
        tm = time.time()-tm_start
        yield '''<script type="text/javascript"> var e = document.getElementById('load-status'); e.innerHTML = "executing '%s' (%.1fs passed)"; </script>\n''' % (alg.name, tm)
      comms = t.comms
      comments = t.comments
      comm_ws = t.comm_ws
    else:
      comms = None
      comments = None
      comm_ws = None
      include_seed = False

    if (comms is None) and (comments is not None):
      raise Exception("algorithm execution error:\n" + comments)

    if comm_ws is not None:
      comm_reprs = [ comms[cind][maxind(comm_ws[cind])] for cind in range(len(comms))]
    else:
      comm_reprs = None


    if comms is not None:
      nmi = get_nmi(comms, user_comms)
    else:
      nmi = None

    yield '''<script type="text/javascript"> var e = document.getElementById('load-status'); e.parentNode.removeChild(e); </script>\n'''
      
    friends_names = []
    friends_imgs = []
    edges = [ [e[0], e[1]] for e in net.edges]
    for i in range(len(net.friends)):
      friends_names.append(net.friends[i]['name'])
      friends_imgs.append(net.friends[i]['picture'])
    if include_seed:
      friends_names.append("seed")
      friends_imgs.append(settings.STATIC_URL + "a.gif")
      seed_ind = len(friends_names) - 1
      for x in range(0, seed_ind - 1):
        edges.append([x, seed_ind])
      
    t = loader.get_template('demo.html')
    c = RequestContext(req, {'net': net, 'comms': comms, 'alg': alg, 'form': form, 'formw': formw,
                             'alg_tab_index': alg_tab_index,
                             'friends_names': friends_names,
                             'friends_imgs': friends_imgs,
                             'edges': edges, 'comments': comments,
                             'user_comms': user_comms, 'user_comms_names': user_comms_names, "nmi": nmi,
                             'comm_reprs': comm_reprs, 'comm_ws': comm_ws,
      })
    yield t.render(c)
  except Exception as ex:
    #django can't handle exceptions automatically, since we already started to create output
    yield '''<br/> Exception:<pre>%s</pre>''' % traceback.format_exc(ex)

import nazarblch.collect_fb_data.mongo as mongonet
import nazarblch.collect_fb_data.similarity_functions as similarity_functions
import nazarblch.collect_fb_data.default_include as default_include
from algorithms.ignatich.mongoproxy import EgoNetProxy

def render_comms_stored(req, mn):
  try:
    t = loader.get_template('demo_head.html')
    c = RequestContext(req, {})
    yield t.render(c)

    yield '<div id="load-status">loading egonet...</div>\n'

    net = EgoNetProxy(mn)

    algs, algsw = cdalgs.create_algs(os.path.join(settings.SITE_ROOT, '..'))

    simw_float_settings = []
    for k, v in default_include.user_user_sim_coefs.iteritems():
      simw_float_settings.append( (k, k, v) )

    simw_float_settings.append( ("threshold", "Threshold:", 0) )

    #FIXME: vector weights are not supported for stored data now
    form = AlgForm(req.GET, algs=algs)

    formw_params = req.GET.copy()
    #a hack, needed since bounded forms don't have default values in django
    for fid, fname, fdef in simw_float_settings:
      if not formw_params.has_key(fid):
        formw_params[fid] = str(fdef)
    formw = AlgFormW(formw_params, algs=[(ind, algsw[ind].name) for ind in range(len(algsw)) if algsw[ind].name != "Weighted Link Communities(vector weights)"], float_settings=simw_float_settings, float_settings_groups=default_include.user_user_sim_coefs_categories)
    user_comms = net.get_flists()
    user_comms_names = [fl["name"] for fl in net.flists]

    friends_names = []
    friends_imgs = []
    for f_ind in range(len(net.friends)):
      friends_names.append(net.friends[f_ind]['name'])
      friends_imgs.append(net.friends[f_ind]['picture'])

    edges = [ [e[0], e[1]] for e in net.edges]

    alg_tab_index = 0
    if req.GET.has_key("algw"):
      alg_tab_index = 1

    if formw.is_valid():
      alg_index = int(formw.cleaned_data['algw'])
      include_seed = bool(formw.cleaned_data['include_seed'])
      sim_settings = dict()
      for fid, fname, fdef in simw_float_settings:
        sim_settings[fid] = float(formw.cleaned_data[fid])
      alg = algsw[alg_index]
      net.sim_settings = sim_settings
      alg_tab_index = 1
    elif form.is_valid():
      alg_index = int(form.cleaned_data['alg'])
      include_seed = bool(form.cleaned_data['include_seed'])
      alg = algs[alg_index]
    else:
      alg = None

    if alg is not None:
      yield '''<script type="text/javascript"> var e = document.getElementById('load-status'); e.innerHTML = "executing '%s'"; </script>\n''' % (alg.name)
      tm_start = time.time()
      t = ExecAlg(alg, net, include_seed)
      t.start()
      while True:
        t.join(timeout=5)
        if not t.isAlive(): break
        tm = time.time()-tm_start
        yield '''<script type="text/javascript"> var e = document.getElementById('load-status'); e.innerHTML = "executing '%s' (%.1fs passed)"; </script>\n''' % (alg.name, tm)
      comms = t.comms
      comments = t.comments
      comm_ws = t.comm_ws
    else:
      comms = None
      comments = None
      comm_ws = None

    yield '''<script type="text/javascript"> var e = document.getElementById('load-status'); e.parentNode.removeChild(e); </script>\n'''

    if (comms is None) and (comments is not None):
      raise Exception("algorithm execution error:\n" + comments)

    if comm_ws is not None:
      comm_reprs = [ comms[cind][maxind(comm_ws[cind])] for cind in range(len(comms))]
    else:
      comm_reprs = None
    if comms is not None:
      nmi = get_nmi(comms, user_comms)
    else:
      nmi = None

    t = loader.get_template('demo_stored.html')
    c = RequestContext(req, {'net': net, 'comms': comms, 'alg': alg, 'form': form, 'formw': formw,
                               'alg_tab_index': alg_tab_index,
                               'friends_names': friends_names,
                               'friends_imgs': friends_imgs,
                               'edges': edges, 'comments': comments,
                               'user_comms': user_comms, 'user_comms_names': user_comms_names, "nmi": nmi,
                               'comm_reprs': comm_reprs, 'comm_ws': comm_ws,
                               })
    yield t.render(c)
  except Exception as ex:
    #django can't handle exceptions automatically, since we already started to create output
    yield '''<br/> Exception:<pre>%s</pre>''' % traceback.format_exc(ex)

@never_cache
def fbuser(req):
  redirect_uri = req.build_absolute_uri().replace("ispras.ru/", "ispras.ru:7059/")
  gapi = FBGraphAPI(settings.FB_APP_ID, settings.FB_APP_SECRET)
  gapi.load_session(req.session)
  r = gapi.acquire_token(req, redirect_uri)
  gapi.save_session(req.session)
  if r is not None:
    return r

  r = HttpResponse(render_comms(req, gapi))
  r["X-Accel-Buffering"] = "no"
  return r

def index(req):
  return render_to_response('index.html', {})

class AccessTokensForm(forms.Form):
  uid = forms.ChoiceField(choices=())
  def __init__(self, *args, **kwargs):
    tokens_by_id = kwargs.pop('tokens', None)
    super(AccessTokensForm, self).__init__(*args, **kwargs)
    if tokens_by_id is not None:
      self.fields['uid'].choices = [(id, t[1]) for id, t in tokens_by_id.iteritems()]

@never_cache
def circlestoken(req):
  import pymongo
  conn = pymongo.Connection()
  db = conn['circles']
  tokens_by_id = dict()
  for t in db.tokens.find():
    tokens_by_id[t["id"]] = (t["access_token"], t["name"])
  form = AccessTokensForm(req.GET, tokens=tokens_by_id)
  if form.is_valid():
    uid = form.cleaned_data['uid']
    atoken = tokens_by_id[uid][0]
    gapi = FBGraphAPI(settings.FB_APP_ID, settings.FB_APP_SECRET)
    gapi.set_token(atoken)
    r = HttpResponse(render_comms(req, gapi))
    r["X-Accel-Buffering"] = "no"
    return r

  return render_to_response('circlestoken.html', {'form': form})

class MongoNetChooseForm(forms.Form):
  uid = forms.ChoiceField(choices=())
  def __init__(self, *args, **kwargs):
    name_by_id = kwargs.pop('names', None)
    super(MongoNetChooseForm, self).__init__(*args, **kwargs)
    if name_by_id is not None:
      self.fields['uid'].choices = [(id, name) for id, name in name_by_id.iteritems()]

@never_cache
def stored(req):
  import pymongo
  conn = pymongo.Connection()
  db = conn['circles']
  name_by_id = mongonet.extract_seed_ids(db)
  form = MongoNetChooseForm(req.GET, names=name_by_id)
  if form.is_valid():
    uid = form.cleaned_data["uid"]
    mn = mongonet.MongoNet(str(uid), db=db)
    r = HttpResponse(render_comms_stored(req, mn))
    r["X-Accel-Buffering"] = "no"
    return r

  return render_to_response('circlestoken.html', {'form': form})
