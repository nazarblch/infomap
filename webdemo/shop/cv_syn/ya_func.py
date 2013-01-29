# -*- coding: utf-8 -*-
from yafunc import directRequest
import time

#----------------Yandex подсказки----------------------------------------------

def suggestion(keywords):
    param = {'Keywords': keywords}
    return directRequest('GetKeywordsSuggestion', param)
    
#--------------WordStat---------------------------------------------------------

def wordstat_report(phrases, geos = ""):
    i = 0 
    for phr in phrases:
        phrases[i] = unicode(phr)        
        
    params = {'Phrases': phrases,}

    if geos != "" :
        params['GeoID'] = geos 
    
    res = directRequest('CreateNewWordstatReport', params) 
    return res  
    
    
def del_wordstat_report(num):
    params = int(num)
    res = directRequest('DeleteWordstatReport', params)
    return res  

def check_wordstat_report():
    return directRequest('GetWordstatReportList', "")   

def get_wordstat_report(num):
    params = int(num)
    return directRequest('GetWordstatReport', params) 

#-----------Wordstat Search Also all result-----------------------------------------------------------------------
def wordstat_search_also(phrases): 
    reportstatearr =  check_wordstat_report()
    if len(reportstatearr) > 4: 
        del_wordstat_report(reportstatearr[0].ReportID)
        time.sleep(2)
    reportnum = wordstat_report(phrases, '')

    for k in range(10):
        time.sleep(15)
        reportstatearr =  check_wordstat_report()
        reportstatedict = dict((item.ReportID, item.StatusReport) for item in reportstatearr)
        if reportstatedict[reportnum] == "Done": break

    kphrases = get_wordstat_report(reportnum)
    kphrases = [[wsitem.Phrase for wsitem in phr.SearchedAlso] for phr in kphrases]

    return kphrases

#------------------------------------------------------------------------------------------------------------------

