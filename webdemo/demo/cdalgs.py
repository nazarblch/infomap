import os
import subprocess
import tempfile
from algorithms.ignatich.egonet import EgoNet
from algorithms.ignatich.lkw import do_lkw

def get_comm_member_weigts(net, comm, include_seed, use_weights=False):
  """seed's weights is always 0"""
  w = [0.0 for x in range(len(comm))]
  if use_weights:
    threshold = net.sim_settings['threshold']

    #TODO: try including seed
    m, n = net.get_matrix(include_seed)

    for aind in range(len(comm)):
      a = comm[aind]
      for bind in range(len(comm)):
        b = comm[bind]
        if a < b:
          if m[a][b] > threshold:
            w[aind] += m[a][b]
            w[bind] += m[a][b]

    if include_seed:
      seed = n-1
      if seed in comm:
        seed_ind = comm.index(seed)
        w[seed_ind] = 0.0
  else:
    #we ignore seed here, since he will only add 1 to every member
    for a, b in net.edges:
      if a < b:
        if (a in comm) and (b in comm):
          aind = comm.index(a)
          bind = comm.index(b)
          w[aind] += 1
          w[bind] += 1
  return w

class CDAlgorithm:
  def __init__(self, name):
    self.name = name

import shutil

class ExecExt(CDAlgorithm):
  def __init__(self, algs, fn, name, args=["%(egonet_fn)s"], outfn=None, chdir=None, egonet_format="uw", rm_dirs=None, fixed_include_seed=None):
    CDAlgorithm.__init__(self, name)
    self.algs_path = algs
    if fn is not None:
      self.fn = os.path.join(self.algs_path, fn)
    self.args = list(args)
    self.outfn = outfn
    self.chdir = chdir
    self.egonet_format = egonet_format
    self.rm_dirs = rm_dirs
    self.fixed_include_seed = fixed_include_seed

  def execute(self, net, include_seed):
    #FIXME: should check which parametes are needed
    tf = tempfile.NamedTemporaryFile(mode="w", prefix="lcd", delete=False)
    outtf = None
    params = None
    try:
      if self.egonet_format == "uw":
        net.write_to_file(tf, include_seed)
      elif self.egonet_format == "w":
        net.write_to_file_w(tf, include_seed)
      else:
        tf.close()
        raise Exception("ExecExt: unknown egonet format - " + self.egonet_format)
      tf.close()

      outtf = tempfile.NamedTemporaryFile(mode="w", prefix="lcd", delete=False)
      outtf.close()
      cmd = [self.fn]
      params = {"egonet_fn": tf.name, 'out_fn': outtf.name,
          'algs_path': self.algs_path}
      if self.chdir is not None:
        os.chdir(self.chdir % params)
      for c in self.args:
        cmd.append(c % params)
      p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      pout, perr = p.communicate()
      retcode = p.returncode

      if self.outfn is None:
        text = pout
      else:
        fn = self.outfn % params
        text = open(fn, "r").read()

      res = []
      for ln in text.split("\n"):
        ln = ln.strip()
        if ln == "": continue
        if ln[0] == "#": continue
        v = map(int, ln.split(" "))
        res.append(v)

      if retcode != 0:
        res = None

      comments = "exec retcode: %s\noutput:\n%s\n\nstderr:\n%s\n" % (retcode, pout, perr)
      if res is None:
        ws = None
      else:
        ws = [get_comm_member_weigts(net, c, include_seed=include_seed, use_weights=(self.egonet_format == "w")) for c in res]

      return res, comments, ws
    finally:
      os.remove(tf.name)
      if outtf is not None:
        os.remove(outtf.name)
      if (params is not None) and (self.rm_dirs is not None):
        for rm_dir in self.rm_dirs:
          path = rm_dir % params
          shutil.rmtree(path, ignore_errors=True)

class ExecExtPy(ExecExt):
  def __init__(self, algs, pyfn, name, args=["%(egonet_fn)s"], outfn=None, fixed_include_seed=None):
    ExecExt.__init__(self, algs, None, name, args, outfn, fixed_include_seed=fixed_include_seed)
    self.fn = "python"
    self.args.insert(0, os.path.join(self.algs_path, pyfn))

class WeightedLinkCommunities(CDAlgorithm):
  def __init__(self, name, similarity="std"):
    CDAlgorithm.__init__(self, name)
    self.similarity = similarity
  def execute(self, net, include_seed):
    res = do_lkw(net, include_seed, self.similarity)
    ws = [get_comm_member_weigts(net, c, include_seed=include_seed, use_weights=True) for c in res]
    return res, "", ws

def create_algs(algs_path):
  return ([
    ExecExtPy(algs_path, "algorithms/ignatich/lk.py", "Link Communities"),
    ExecExtPy(algs_path, "algorithms/ignatich/lk.py", "Link Communities (mod similarity)", ["%(egonet_fn)s", "dummy"]),
    ExecExtPy(algs_path, "algorithms/ignatich/dslpa.py", "DSLPA"),
    ExecExt(algs_path, "../extras/OSLOM2/oslom_undir", "OSLOM", ["-uw", "-r", "50", "-hr", "0", "-t", "0.2", "-f", "%(egonet_fn)s"],
        "%(egonet_fn)s_oslo_files/tp", "%(algs_path)s/../extras/OSLOM2", rm_dirs=["%(egonet_fn)s_oslo_files/"]),
    ExecExtPy(algs_path, "../extras/cohasion.py", "Cohesion", ["%(egonet_fn)s", "%(out_fn)s"], "%(out_fn)s", fixed_include_seed=True),
    ], [
    ExecExt(algs_path, "../extras/OSLOM2/oslom_undir", "OSLOM (weighted)", ["-w", "-r", "50", "-hr", "0", "-t", "0.2", "-f", "%(egonet_fn)s"],
        "%(egonet_fn)s_oslo_files/tp", "%(algs_path)s/../extras/OSLOM2", "w", rm_dirs=["%(egonet_fn)s_oslo_files/"]),
    WeightedLinkCommunities("Weighted Link Communities"),
    WeightedLinkCommunities("Weighted Link Communities(mod similarity)", similarity="mod"),
    WeightedLinkCommunities("Weighted Link Communities(vector weights)", similarity="vec"),
    ])
