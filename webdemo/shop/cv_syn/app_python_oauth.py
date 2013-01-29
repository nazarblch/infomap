# -*- coding: utf-8 -*-
#Описание примера http://api.yandex.ru/direct/doc/examples/python-suds.xml

#1. Подключение suds и настройка логирования
#=========================================================
from suds.client import Client
from suds.cache import DocumentCache
from suds.sax.element import Element
from suds import WebFault

import logging
logging.basicConfig(level=logging.INFO)
if __debug__:
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
else:
    logging.getLogger('suds.client').setLevel(logging.CRITICAL)
    

#2. Плагин для коррекции ответов
#=========================================================
from suds.plugin import *
class NamespaceCorrectionPlugin(MessagePlugin):
    def received(self, context):
        context.reply = context.reply.replace('"http://namespaces.soaplite.com/perl"','"API"')


#3. Экземпляр класса suds.Client
#=========================================================
api = Client('http://soap.direct.yandex.ru/wsdl/v4/', plugins = [NamespaceCorrectionPlugin()])
api.set_options(cache=DocumentCache())


#4. Метаданные в заголовках SOAP-пакетов
#=========================================================
locale = Element('locale').setText('en')

#5 SSL-авторизация
#==================================================================
login = Element('login').setText('genromix')
token = Element('token').setText('895750b6f51d494e91e6a59e06a11e51')
appId = Element('application_id').setText('1ba17deb0ba44efe9edf9b329269ca75')
locale = Element('locale').setText('en')
api.set_options(soapheaders=(login, token, appId, locale))


#6. Функция для вызова методов API
#=========================================================
def directRequest(methodName, params):
    '''
    Вызов метода API Яндекс.Директа:
       api - экземпляр класса suds.Client
       methodName - имя метода
       params - входные параметры
    В случае ошибки программа завершается,
    иначе возвращается результат вызова метода
    '''
    try:
        result = api.service['APIPort'][methodName](params)
        return result
    except WebFault, err:
        print unicode(err)
    except:
        err = sys.exc_info()[1]
        print 'Other error: ' + str(err)
    exit(-1)

