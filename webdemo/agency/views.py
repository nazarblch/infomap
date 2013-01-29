# -*- coding: utf-8 -*-
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from agency.models import Clients



def login(request):
    if 'username' in request.POST and 'password' in request.POST and request.POST['username'] and request.POST['password']:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)


            return HttpResponseRedirect("/agency/clients/")
        else:
            return render_to_response("agency/login.html", {'error': True})
        
    else:
        return render_to_response("agency/login.html")
        
        
    


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


def show_clients(request):

    from yafunc import get_clients

    agent = request.user.username
    clients = get_clients(agent)
    
    return render_to_response("agency/clients.html", {'clients':clients})
    
def new_client(request):

    from yafunc import create_client
    from suds import WebFault
    
    if request.is_ajax():
            login = unicode(request.POST["cllogin"])
            name = unicode(request.POST["clname"])
            sur = unicode(request.POST["clsur"])
            
            cl = create_client(login, name, sur)

            if isinstance(cl, WebFault):
                return HttpResponse("E:"+unicode(cl))

            res = '<tr id="'+str(cl.Login)+'" class="client"  height="23px" valign="center" >'
            res +=        '<td><span >'+str(cl.Login)+'</span></td>'
            res +=        '<td><span >'+unicode(cl.FIO)+'</span></td>'

            res +=        '<td><span class="info_but">info</span></td>'
            res +=        '<td><span class="del_but">del</span></td>'
            res +=        '<td><span class="choose_but">choose</span></td>'
            res += '</tr>'
            
            return HttpResponse(res)
        
def addclient_todb(request):
    from yafunc import get_clients

    if request.is_ajax():
        agent = request.user.username
        clients = get_clients(agent)
        postlogin = request.POST["login"]
        for item in clients:
            if item.Login == postlogin:
                try:
                    dbcl = Clients.objects.get(login=postlogin)
                except:
                    dbcl = Clients()
                    dbcl.login = item.Login

                    dbcl.name = unicode(item.FIO)
                    dbcl.agent = request.user
                    try:
                        dbcl.save()
                    except:
                        return HttpResponse("-1")


                request.session['client'] = dbcl.id 
                return HttpResponse("1")
            
        return HttpResponse("-1")   
    
    

    
 
    