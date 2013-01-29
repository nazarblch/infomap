from agency.models import Clients
from shop.models import ShopInfo


def get_default_info(request):

    if "shop" not in request.session:
        request.session["shop"] = ShopInfo.objects.get(name = "mobileshop")
        shopobj = request.session["shop"]
        request.session['client'] = shopobj.client.id
	

    if 'client' not in request.session:
        raise IndentationError("Client hasn't been defined")

    if 'shop' not in request.session:
        raise IndentationError("Shop hasn't been defined")


    clid = int(request.session['client'])
    cl = Clients.objects.get(id=clid)
    cllogin = cl.login
    shopname = request.session["shop"].name
    shopid = request.session["shop"].id

    return  {
        "username": request.user.username,
        "cllogin": cllogin,
        "shopname": shopname,
        "shopid": shopid,
        "clid": clid,
        }




import hotshot
import os
import time
import settings

try:
    PROFILE_LOG_BASE = settings.PROFILE_LOG_BASE
except:
    PROFILE_LOG_BASE = "/tmp"


def profile(log_file):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof',
    where the time stamp is in UTC. This makes it easy to run and compare
    multiple trials.

    hotshot2calltree your_project.prof > your_project.out

    python -m cProfile -o your_project.pyprof your_project.py
    pyprof2calltree -i your_project.pyprof -o your_project.out

    kcachegrind is a program to analise your_project.out

    Try apt-get install kcachegrind command if you use linux OS or
    firstly install linux.

    """

    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            (base, ext) = os.path.splitext(log_file)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer
