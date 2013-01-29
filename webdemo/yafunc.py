#!/usr/bin/python
# -*- coding: UTF-8 -*-
import traceback
from appcommon.dependency_injection import provides, requires, resource_registry
import settings
from ya_exeptions import YaTypeConvertError, YaEmptyRequestError
import httplib, urllib2

try:
    from django.http import  HttpResponse
    from django.core.context_processors import csrf
    from django.contrib.sessions.backends.db import SessionStore
except:
    pass

import time

from suds.client import Client          # WSDL-description
from suds.cache import DocumentCache    # cache WSDL-description
from suds.sax.element import Element    # adding headers (metadata, OAuth, ... )
from suds import WebFault               # differ server and client exceptions


import logging
logging.basicConfig(level=logging.INFO)

if settings.DEBUG:
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
else:
    logging.getLogger('suds.client').setLevel(logging.CRITICAL)


#=========================================================
from suds.plugin import *
class NamespaceCorrectionPlugin(MessagePlugin):
    def received(self, context):
        context.reply = context.reply.replace('"'+settings.CORRECTION_URL+'"','"API"')


class YaClient(Client):

    def __init__(self):

        Client.__init__(self, settings.WDSL_URL, plugins = [NamespaceCorrectionPlugin()])
        self.set_options(cache=DocumentCache())

        locale = Element('locale').setText('en')
        self.set_options(soapheaders=(locale))


    def SSL_Auth(self):

        class YandexCertConnection(httplib.HTTPSConnection):
            def __init__(self, host, port=None, key_file=settings.KEYFILE, cert_file=settings.CERTFILE, timeout=30):
                httplib.HTTPSConnection.__init__(self, host, port, key_file, cert_file)

        class YandexCertHandler(urllib2.HTTPSHandler):
            def https_open(self, req):
                return self.do_open(YandexCertConnection, req)
            https_request = urllib2.AbstractHTTPHandler.do_request_

        self.options.transport.urlopener = urllib2.build_opener(*[YandexCertHandler()])


    def Token_Auth(self):

        login = Element('login').setText(settings.AGENT_LOGIN)
        token = Element('token').setText(settings.AGENT_TOKEN)
        appId = Element('application_id').setText(settings.APPLICATION_ID)
        locale = Element('locale').setText('en')
        self.set_options(soapheaders=(login, token, appId, locale))

    def print_hren(self):
        print "hren"



@provides('api')
class APIProvider(object):
    def __init__(self, api):
        self.api = api

    def __str__(self):
        return 'Provider(%s)' % self.handle

@requires('api')
class APIUser(object):
    def __init__(self, **kwargs):
        pass


api = YaClient()
api.Token_Auth()
pr1 = APIProvider(api)



#=========================================================
def directRequest(methodName, params, times=3):

    try:
        api1 = resource_registry.values()[0].api
        result = api.service['APIPort'][methodName](params)
        return result
    except WebFault, err:
        if times > 0:
            time.sleep(2)
            return directRequest(methodName, params, times-1)
        else:
            return err
    except:
        err = sys.exc_info()[1]
        return 'Other error: ' + str(err)





#company
#=========================================================

def create_company(request):
        try:

            strategy = { "StrategyName": request['strategy'], }

            if 'mxprice' in request.keys() and request['mxprice'] != "" :
                strategy.update({"MaxPrice": float(request['mxprice']) })
            if 'avprice' in request.keys() and  request['avprice'] != "" :
                strategy.update({"AveragePrice": float(request['avprice'])})
            if 'weeklimit' in request.keys() and  request['weeklimit'] != "" :
                strategy.update({"WeeklySumLimit": float(request['weeklimit'])})
            if 'weekclicks' in request.keys() and  request['weekclicks'] != "" :
                strategy.update({"ClicksPerWeek": int(request['weekclicks'])})

            MinusKw = request['MinusKw']


            params = {
        		   "Login": unicode(request['login']),
        		   "CampaignID": 0,
        		   "Name": unicode(request['name']),
        		   "FIO": unicode(request['fio']),
        		   "Strategy":strategy,
        		   "EmailNotification":{
        		      "MoneyWarningValue":10,
        		      "WarnPlaceInterval":60,
        		      "SendWarn":"Yes",
        		      "Email":unicode(request['email'])
        		   },
                           "StatusBehavior": "Yes",
                           "StatusContextStop": "No",
                           "ContextLimit": "Limited",
                           "AutoOptimization":  "No",
        		   "StatusMetricaControl": "Yes",
        		   "StatusOpenStat": "No",
                           "ConsiderTimeTarget": "Yes",
        		   #"AddRelevantPhrases": "Yes",
        		   #"RelevantPhrasesBudgetLimit": int(request['RelevantPhrasesBudgetLimit']),
                           "MinusKeywords": MinusKw,

        	}

            if 'ContextLimitSum' in request.keys() and  request['ContextLimitSum'] != "" :
                request["ContextLimitSum"] = int(request['contextlimitsum'])
            if 'ContextPricePercent' in request.keys() and  request['ContextPricePercent'] != "" :
                request["ContextPricePercent"] = int(request['contextpricepercent'])


            if 'TimeTarget' in request.keys() and int(request['TimeTarget']) == 1:

                timetarget = {
    				"ShowOnHolidays": request['holidays'],
    				"TimeZone": "Europe/Moscow",
                }

                if(request['holidays'] == "Yes"):
                    timetarget["HolidayShowFrom"] = int(request['hol_from'])
                    timetarget["HolidayShowTo"] = int(request['hol_to'])

                dayshours = []
                days = request['days']

                for d in days:
                    dh = {"Hours": (d.split('_')[1]).split(','), "Days": (d.split('_')[0]).split(',') }
                    dayshours.append(dh)

                timetarget.update({"DaysHours":dayshours})
                params.update({"TimeTarget":timetarget})

            if 'DisabledDomains' in request.keys() and len(request['DisabledDomains']) > 0:
                params.update({"DisabledDomains": unicode(request['DisabledDomains']) })


            campaignId = directRequest('CreateOrUpdateCampaign', params)
            return True, campaignId

        except Exception, e:
            return False, 'Create Company SOAP Fault: '+str(e)



def company_params(id):

    params = {'CampaignIDS': [int(id)]}
    campaignsParams = directRequest('GetCampaignsParams', params)
    params = campaignsParams[0]

    return params

def user_companies_info(request):

        param = {
		"Logins": request.POST.getlist('logins'),

		"Filter": {
			"StatusModerate": request.POST.getlist('fmoderate'),
			"IsActive": request.POST.getlist('fisactive'),
			"StatusArchive": request.POST.getlist('farchive'),
			"StatusActivating": request.POST.getlist('factivating'),
			"StatusShow": request.POST.getlist('fshow')
		}
                 }

        if int(request.POST['filter']) == 1:

            filt = {}
            if len(request.POST.getlist('fmoderate')) > 0 :
                        filt.update({"StatusModerate": request.POST.getlist('fmoderate') })
            if len(request.POST.getlist('fisactive')) > 0 :
                        filt.update({"IsActive": request.POST.getlist('fisactive') })
            if len(request.POST.getlist('farchive')) > 0 :
                        filt.update({"StatusArchive": request.POST.getlist('farchive') })
            if len(request.POST.getlist('factivating')) > 0 :
                        filt.update({"StatusActivating": request.POST.getlist('factivating') })
            if len(request.POST.getlist('fshow')) > 0 :
                        filt.update({"StatusShow": request.POST.getlist('fshow') })

            param.update({"Filter": filt})


        result = directRequest('GetCampaignsListFilter', param)
        return result


def update_company(request):

   try:
        params = {'CampaignIDS': [int(request.POST['Id'])]}
        campaignsParams = directRequest('GetCampaignsParams', params)

        #изменить параметры
        params = campaignsParams[0]

        #стратегия
        if request.POST['strategy'] != "" and request.POST['strategy'] != None:
        	params.Strategy.StrategyName = request.POST['strategy']

                if request.POST['mxprice'] != "" and request.POST['mxprice'] != None:
	        	params.Strategy.MaxPrice = float(request.POST['mxprice'])
                if request.POST['avprice'] != "" and request.POST['avprice'] != None:
	        	params.Strategy.AveragePrice = float(request.POST['avprice'])
                if request.POST['weeklimit'] != "" and request.POST['weeklimit'] != None:
	        	params.Strategy.WeeklySumLimit = float(request.POST['weeklimit'])
                if request.POST['weekclicks'] != "" and request.POST['weekclicks'] != None:
	        	params.Strategy.ClicksPerWeek = int(request.POST['weekclicks'])

        #минус слова
        params.MinusKeywords = []
        MinusKw = request.POST.getlist('MinusKw')
        for word in MinusKw:
            params.MinusKeywords.append(unicode(word))

        #время
        if int(request.POST['TimeTarget']) == 1:
                #выходные
                if request.POST['holidays'] != "" and request.POST['holidays'] != None:
			params.TimeTarget.ShowOnHolidays = request.POST['holidays']
			if request.POST['hol_from'] != "" and request.POST['hol_from'] != None:
				params.TimeTarget.HolidayShowFrom = int(request.POST['hol_from'])
                        if request.POST['hol_to'] != "" and request.POST['hol_to'] != None:
				params.TimeTarget.HolidayShowTo = int(request.POST['hol_to'])

                #все дни
                if request.POST['days'] != "" and request.POST['days'] != None:

                        days = request.POST.getlist('days')
                        params.TimeTarget.DaysHours = []

			i = 0
		        for d in days:
                                params.TimeTarget.DaysHours[i].Days = (d.split('_')[0]).split(',')
				params.TimeTarget.DaysHours[i].Hours = (d.split('_')[1]).split(',')
                        	i = i + 1

	#email
	if request.POST['email'] != "" and request.POST['email'] != None:
		params.EmailNotification.Email = request.POST['email']

	# % расхода и % цены клика в рекламной сети яндех :::10
        if request.POST['contextlimitsum'] != "" and request.POST['contextlimitsum'] != None:
		params.ContextLimitSum = int(request.POST['contextlimitsum'])
	if request.POST['contextpricepercent'] != "" and request.POST['contextpricepercent'] != None:
        	params.ContextPricePercent = int(request.POST['contextpricepercent'])

        #релевантные фразы
	if len(request.POST['RelevantPhrases']) > 0:
		params.AddRelevantPhrases = request.POST['RelevantPhrases']
		params.RelevantPhrasesBudgetLimit = int(request.POST['RelevantPhrasesBudgetLimit'])

        #враждебные домены
        if len(request.POST['DisabledDomains']) > 0:
                params.DisabledDomains = unicode(request.POST['DisabledDomains'])



        #сохранить параметры в API
        result = directRequest('CreateOrUpdateCampaign', params)
        return HttpResponse(str(result))

   except Exception, e:
	return HttpResponse('Update company Id: ' + request.POST['Id'] + ' SOAP Fault: '+str(e))


def company_balance(request):

    nums = request.POST.getlist("num")

    i = 0
    for n in nums:
        nums[i] = int(n)
        i = i + 1

    params = nums

    res = directRequest('GetBalance', params)
    return HttpResponse(str(res))


def company_archive(Id):

    cid = int(Id)

    params = {
              'CampaignID': cid
    }

    res = directRequest('ArchiveCampaign', params)
    return res

def company_unarchive(Id):

    cid = int(Id)

    params = {
              'CampaignID': cid
    }

    res = directRequest('UnArchiveCampaign', params)
    return res


def company_del(Id):

    cid = int(Id)

    params = {
              'CampaignID': cid
    }
    res = directRequest('DeleteCampaign', params)
    return res

def company_resume(Id):

    cid = int(Id)

    params = {
              'CampaignID': cid
    }

    res = directRequest('ResumeCampaign', params)
    return res

def company_stop(Id):

    cid = int(Id)

    params = {
              'CampaignID': cid
    }

    res = directRequest('StopCampaign', params)
    return res


def company_stat(Ids, startp, endp):

    params = {
              "CampaignIDS": [int(Id) for Id in Ids],
              "StartDate": startp,   #'2011-05-14'
              "EndDate": endp
    }

    res = directRequest('GetSummaryStat', params)
    return res

def company_metr_goals(Id):

    cid = int(Id)

    params = {
              'CampaignID': cid
    }

    res = directRequest('GetStatGoals', params)
    return res


def set_company_rate(request):

        params = {
          'CampaignID': int(request.POST['Id']),
          'Mode': unicode(request.POST['mode']),
          'PriceBase': unicode(request.POST['pricebase']),
          'ProcBase': unicode(request.POST['procbase']),
          'Proc': int(request.POST['proc']),
          'MaxPrice': float(request.POST['maxprace']),
        }

        res = directRequest('SetAutoPrice', params)
        response = ''
        for s in res:
           response += s.encode('utf-8')

        return HttpResponse(response)



#banner
#=========================================================


def create_banner(request):

    try:

        banner = api.factory.create('BannerInfo')
        banner.CampaignID = int(request.POST['Id'])
        banner.BannerID = 0
        banner.Title = unicode(request.POST['title'])
        banner.Text = unicode(request.POST['text'])
        banner.Href = unicode(request.POST['url'])
        banner.Geo = request.POST['geo']

        banner.Sitelinks = []

        Sitelinks = request.POST.getlist('Sitelinks')
        i = 0
        for title_hr in Sitelinks:
            banner.Sitelinks[i].Title = unicode(title_hr.split("&_&")[0]);
            banner.Sitelinks[i].Href = unicode(title_hr.split("&_&")[1]);
            i = i + 1

        if int(request.POST["ContactInfo"]) == 1:

            banner.ContactInfo.Country = unicode(request.POST['country'])
            banner.ContactInfo.CountryCode = request.POST['countrycode']
            banner.ContactInfo.City = unicode(request.POST['city'])
            banner.ContactInfo.CityCode = request.POST['citycode']
            banner.ContactInfo.Phone = request.POST['phone']
            banner.ContactInfo.CompanyName = unicode(request.POST['companyname'])
            banner.ContactInfo.WorkTime = unicode(request.POST['worktime'])
            if len(request.POST['phoneext']) > 0:
                banner.ContactInfo.PhoneExt = request.POST['phoneext']
            if len(request.POST['extramessage']) > 0:
                banner.ContactInfo.ExtraMessage = unicode(request.POST['extramessage'])
            if len(request.POST['contactemail']) > 0:
                banner.ContactInfo.ContactEmail = unicode(request.POST['contactemail'])

        else:
            del(banner.ContactInfo)


        banner.MinusKeywords = []
        MinusKw = request.POST.getlist('MinusKw')
        for word in MinusKw:
            banner.MinusKeywords.append(unicode(word))

        #поисковая фраза
        phrase = make_phrase(request)
        banner.Phrases = [phrase]

        #сохранить данные в API
        params = [banner]
        bannerID = directRequest('CreateOrUpdateBanners', params)
        return HttpResponse(str(bannerID))

    except Exception, e:
        return HttpResponse('Create banner SOAP Fault: '+str(e))

#phrase
#=========================================================


def make_phrase(request):

        phrase = api.factory.create('BannerPhraseInfo')
        phrase.PhraseID = 0
        phrase.Phrase = unicode(request.POST['phrase'])
        phrase.AutoBroker = "Yes"
        if len(request.POST['price']) > 0:
            phrase.Price = float(request.POST['price'])
        if len(request.POST['contextprice']) > 0:
            phrase.ContextPrice = float(request.POST['contextprice'])
        if len(request.POST['isrubric']) > 0:
            phrase.IsRubric = request.POST['isrubric']
        if len(request.POST['autobudgetpriority']) > 0:
            phrase.AutoBudgetPriority = request.POST['autobudgetpriority']


        #переменные, подставляемые в ссылку на сайт
        userParams = api.factory.create('PhraseUserParams')
        if len(request.POST['param1']) > 0:
            userParams.Param1 = unicode(request.POST['param1'])
        if len(request.POST['param2']) > 0:
            userParams.Param2 = unicode(request.POST['param2'])


        phrase.UserParams = userParams

        return phrase


def add_phrase(request):
        params = {'BannerIDS': [int(request.POST['Id'])]}
        bannerParams = directRequest('GetBanners', params)[0]

        phrase = make_phrase(request)
        bannerParams.Phrases.append(phrase)

        params = [bannerParams]
        bannerIDS = directRequest('CreateOrUpdateBanners', params)
        return HttpResponse(str(bannerIDS[0]))


def set_rate(request):

        params = [
           {
              'PhraseID': int(request.POST['Id']),
              'BannerID': int(request.POST['bannerId']),
              'CampaignID': int(request.POST['companyId']),
              'Price': float(request.POST['price']),
              'AutoBudgetPriority': str(request.POST['priority']),
              'AutoBroker': 'Yes',
              #'ContextPrice': float(request.POST['contextprice'])
           }
        ]

        res = directRequest('UpdatePrices', params)
        return HttpResponse(str(res))



def phrases_info(request):

    banners = request.POST.getlist("banner")

    params = banners

    res = directRequest('GetBannerPhrases', params)
    response = ''
    for s in res:
        response += str(s)+"<br>"

    return HttpResponse(response)



#keywords
#=========================================================
# less then calls 1000 per day
# cost = 10
# we have = 32000 per day
'''
10 фраз в одном запросе и 1000 фраз в течение суток
'''


def get_synonyms(request):

        synonyms = request
        u_synonyms = []

        for word in synonyms:
            if word != '':
                u_synonyms.append(unicode(word))

        params = {
             'Keywords': u_synonyms
        }

        return directRequest('GetKeywordsSuggestion', params)



def wordstat_report(phrases, geos = ""):

        i = 0
        for phr in phrases:
            phrases[i] = unicode(phr)

        params = {
    		'Phrases': phrases,
    	}

        if geos != "" :
            params['GeoID'] = geos

        try:
            res = directRequest('CreateNewWordstatReport', params)
        except Exception, e:
            print e, 'CreateNewWordstatReport'
            res = directRequest('CreateNewWordstatReport', params)

        return res


def del_wordstat_report(num):
        params = int(num)

        try:
            res = directRequest('DeleteWordstatReport', params)
        except Exception, e:
            print e, 'DeleteWordstatReport'
            res = directRequest('DeleteWordstatReport', params)

        return res

def check_wordstat_report():

    try:
        return directRequest('GetWordstatReportList', "")
    except Exception, e:
        print e, 'GetWordstatReportList'
        return directRequest('GetWordstatReportList', "")


def get_wordstat_report(num):
        params = int(num)

        try:
            return directRequest('GetWordstatReport', params)
        except Exception, e:
            print e, 'GetWordstatReport'
            return directRequest('GetWordstatReport', params)




def wordstat(phrases, showsmax=3000, showsmin=10, geos = ""):

    kphrases1 = []
    req_phrases = []

    steps = len(phrases)/50 + int(len(phrases)%50 > 0)

    for step in range(steps):

        phr50 = phrases[step*50: (step+1)*50]

        kphrases1_new, req_phrases_new = wordstat_50_phr(phr50, showsmax, showsmin, geos)
        kphrases1.extend(kphrases1_new)
        req_phrases.extend(req_phrases_new)


    return kphrases1, req_phrases


def wordstat_50_phr(phrases, showsmax, showsmin, geos):
    
    listcount = len(phrases)/10 + int(len(phrases)%10 > 0)


    for i in range(3):

        reportstatearr =  check_wordstat_report()

        if len(reportstatearr) > 0:
            for reportstate in reportstatearr:
                del_wordstat_report(reportstate.ReportID)
            time.sleep(2)

        else:
            break


    reportnums = {}
    for listnum in range(listcount):
        reportnums[listnum] = wordstat_report(phrases[listnum*10:listnum*10+10], geos)

    for k in range(10):
        time.sleep(10)
        reportstatearr =  check_wordstat_report()
        reportstatedict = dict((item.ReportID, item.StatusReport) for item in reportstatearr)
        
        br = True
        for listnum in range(listcount):
            if reportstatedict[reportnums[listnum]] != "Done": br = False

        if br: break
        
    kphrases1 = []
    req_phrases = []     

    for listnum in range(listcount):
        kphrases = get_wordstat_report(reportnums[listnum])
        try:
            kphrases1 += [[ (wsitem.Phrase, wsitem.Shows) for wsitem in phr.SearchedWith if wsitem.Shows in range(showsmin,showsmax) ] for phr in kphrases]
            req_phrases += [phr.Phrase for phr in kphrases]

        except:
            for phr in kphrases:
                print phr



    return kphrases1, req_phrases


#forecast
#=========================================================
'''
max 100 фраз на запрос
<= 7 слов в ключевой фразе
'''
PHRASES_PER_REQUEST = 99

def budget_forecast(phrases, geo = None, categories = None):

        if not isinstance(phrases, list):
            try:
                phrases = list(phrases)
            except Exception, e:
                raise YaTypeConvertError(e, "Failed to make list from "+str(type(phrases)))

        if not len(phrases):
            raise YaEmptyRequestError("budget_forecast phrases is empty")

        res = {}

        if not geo: geo = []

        steps = len(phrases)/PHRASES_PER_REQUEST
        if len(phrases)%PHRASES_PER_REQUEST != 0: steps += 1

        for step in range(steps):

            res.update(
                get_one_forecast(
                    phrases[PHRASES_PER_REQUEST*step: PHRASES_PER_REQUEST*(step+1)],
                    geo
                )
            )


        return res


def del_budget_forecast(num):

        params = int(num)
        res = directRequest('DeleteForecastReport', params)
        return res


def check_budget_forecast():

        res = directRequest('GetForecastList', '')

        response = ''
        for s in res:
            response += str(s)+"<br>"

        return response


def get_budget_forecast(num):

        params = int(num)

        res = directRequest('GetForecast', params)

        return res



def get_one_forecast(phrases, geo):



    phrases = map(lambda str:unicode(str),phrases)

    reports = lambda: directRequest("GetForecastList", {})
    delete = lambda forecastId: directRequest("DeleteForecastReport", forecastId)
    new_forecast = lambda phrases, geoID: directRequest("CreateNewForecast",dict(Phrases=phrases, GeoID = geoID))
    get_forecast = lambda forecastId: directRequest("GetForecast", forecastId)

    start_reports = reports()

    def get_ready_forecast(forecastId):
        status = "Pending"
        while status == 'Pending':
            time.sleep(2)
            try:
                report = filter(lambda forecast: forecast.ForecastID == forecastId, reports())
                if report.__len__() == 0:
                    raise Exception("report not found")

                status = report[0].StatusForecast
            except Exception, e:
                print traceback.print_exc()
                print e
                print filter(lambda forecast: forecast.ForecastID == forecastId, reports())


        forecast = get_forecast(forecastId)
        return forecast

    if len(start_reports) < 5:
        forecastId = new_forecast(phrases,geo)
        forecast = get_ready_forecast(forecastId)
    else:
        delete(start_reports[0]["ForecastID"])
        forecastId = new_forecast(phrases,geo)
        forecast = get_ready_forecast(forecastId)

    def check_type(obj):
        if isinstance(obj, float) or isinstance(obj, int) or isinstance(obj, long) or isinstance(obj, list):
            return obj

        return unicode(obj)


    forecast_dict = {}

    for i in range(len(forecast[1])):

        try:
            forecast_dict[forecast[1][i].Phrase] = dict(
                (name, check_type(getattr(forecast[1][i], name))) for name in dir(forecast[1][i]) if not name.startswith('__')
            )
        except:
            print forecast[1]



    return forecast_dict


#user data
#=========================================================
'''
доступно 32000 баллов на сутки

добавление объявления ― 12 баллов;
редактирование объявления ― 4 балла;
добавление новой фразы ― 2 балла;
редактирование фразы ― 1 балл;
получение подсказок к ключевым словам ― 3 балла за запрос;
получение статистики запросов ― 10 баллов за фразу.

На количество доступных для использования баллов влияют следующие факторы:

    количество отклоненных на модерации объявлений;
    количество фраз, отключенных за низкий CTR;
    средний CTR рекламной кампании;
    средний бюджет рекламной кампании.

'''


def userunits(names=["genromix"]):
    params = names
    return directRequest('GetClientsUnits', params)

def get_clients(agent):

    params = {
       'Login': agent,
       'Filter': {
          'StatusArch':'No'
        },
    }

    return directRequest('GetSubClients', params)

def create_client(Login, Name, Surname):

    params = {
       'Login': unicode(Login),
       'Name': unicode(Name),
       'Surname': unicode(Surname)
    }

    return directRequest('CreateNewSubclient', params)




#additional information
#=========================================================

def regions():

    res = directRequest('GetRegions', "")
    return dict((item.RegionID, item.RegionName) for item in res)


