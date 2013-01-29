# -*-coding: utf-8 -*-


import string
import difflib
import sys
import re
import urllib
import urllib2
import json

url = "http://translate.google.com/translate_a/t?client=t&text={0}&hl=en&sl={1}&tl={2}&multires=1"

def printParams(data):
    for x in data:
        print(u"\t{0}".format(x))


def tr(text, sourcelang, targetlang):
    """
    Translates given string(text) from sourcelang to targetlang
    using Google Translate
    """
    request = urllib2.Request(url.format(text, sourcelang, targetlang),
      headers={ 'User-Agent': 'Mozilla/5.0', 'Accept-Charset': 'utf-8' })
    response = urllib2.urlopen(request).read()
    fixedJSON = re.sub(r',{2,}', ',', response).replace(',]', ']')
    data = json.loads(fixedJSON)
    result = {}
    result["definition"] = data[0][0]
    for row in data[1]:
        try:
            result[row[0]] = row[1]
        except:
            pass
    return result


def testgoogle():
    """
    Usage:
    first arg - string to translate
    second arg - source lang
    third arg - target lang
    """
    if len(sys.argv) == 4:
        text = urllib.quote(sys.argv[1])
        sl = sys.argv[2]
        tl = sys.argv[3]
        r = tr(text, sl, tl)
        print(u"{0} / {1} / {2}".format(r["definition"][0],
                                        r["definition"][1],
                                        r["definition"][2] or r["definition"][3]))
        del r["definition"]
        for key, val in r.iteritems():
            print(key)
            printParams(val)
    else:
        print(testgoogle.__doc__)


def find_substr_in_arr(substr, arr, cutoff=0.6, variants=1):
    
    res=set([])
    for arr_i in arr:
        
        comb_of_words = map(lambda a, b: ' '.join([a,b]), arr_i.split(' ')[:-1], arr_i.split(' ')[1:])
        comb_of_words.extend(arr_i.split())
        
        try: res.add( difflib.get_close_matches(substr, comb_of_words, variants, cutoff)[0] )
        except:pass
        
    return res


def translit(s, lang=""):
    "Russian translit: converts 'привет'->'privet'"
    assert s is not str, "Error: argument MUST be string"


    russian = ({     'юй': 'yuy', 'ей': 'yay',
                    'Юй': 'Yuy', 'Ей': 'Yay',
              },
              {
            'а': 'a',  'б': 'b',  'в': 'v',  'г': 'g', 'д': 'd', 'е': 'e',
            'ё': 'yo', 'ж': 'zh', 'з': 'z',  'и': 'i', 'й': 'y', 'к': 'k',
            'л': 'l',  'м': 'm',  'н': 'n',  'о': 'o', 'п': 'p', 'р': 'r',
            'с': 's',  'т': 't',  'у': 'u',  'ф': 'f', 'х': 'h', 'ц': 'c',
            'ч': 'ch', 'ш': 'sh', 'щ': 'sh', 'ъ': '',  'ы': 'y', 'ь': '',
            'э': 'e',  'ю': 'yu', 'я': 'ya',

            'А': 'A',  'Б': 'B',  'В': 'V',  'Г': 'G', 'Д': 'D', 'Е': 'E',
            'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z',  'И': 'I', 'Й': 'Y', 'К': 'K',
            'Л': 'L',  'М': 'M',  'Н': 'N',  'О': 'O', 'П': 'P', 'Р': 'R',
            'С': 'S',  'Т': 'T',  'У': 'U',  'Ф': 'F', 'Х': 'H', 'Ц': 'C',
            'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sh', 'Ъ': '',  'Ы': 'Y', 'Ь': '',
            'Э': 'E',  'Ю': 'Yu', 'Я': 'Ya'
              })

    english = ({
    "yuy": "юй",
    "Yay": "Ей",
    "yay": "ей",
    "Yuy": "Юй",
    },
    {
    "yo": "ё",
    "ch": "ч",
    "sh": "ш",
    "ya": "я",
    "yu": "ю",
    "zh": "ж",
    "Ch": "Ч",
    "Sh": "Ш",
    "Yu": "Ю",
    "Ya": "Я",
    "Zh": "Ж",
    "Yo": "Ё",
    "ph": "ф",
    "Ph": "Ф",
    },
    {

    "x": "кс",
    "w": "в",
    "q": "кю",
    "j": "дж",
    "v": "в",
    "s": "с",
    "r": "р",
    "u": "у",
    "t": "т",
    "h": "х",
    "f": "ф",
    "c": "ц",
    "y": "и",
    "g": "г",
    "a": "а",
    "b": "б",
    "z": "з",
    "d": "д",
    "e": "е",
    "k": "к",
    "l": "л",
    "i": "и",
    "o": "о",
    "p": "п",
    "m": "м",
    "n": "н",

    },
    {
    "X": "Икс",
    "W": "В",
    "Q": "Kю",
    "J": "Дж",
    "V": "В",
    "T": "Т",
    "U": "У",
    "R": "Р",
    "B": "Б",
    "C": "Ц",
    "F": "Ф",
    "H": "Х",
    "Y": "Ы",
    "E": "Э",
    "G": "Г",
    "A": "А",
    "Z": "З",
    "D": "Д",
    "E": "Е",
    "K": "К",
    "L": "Л",
    "I": "И",
    "Y": "Й",
    "O": "О",
    "P": "П",
    "M": "М",
    "N": "Н",
    "S": "С",

    })


    if len(set(s) & set(string.letters)) > 0:
        lang = "ru"
    else:
        lang = "en"


    if lang == "en":
        characters = russian

    elif lang == "ru":
        characters = english

    for part in characters:
        for k in part.keys():
            s = s.replace(k,unicode(part[k],"utf-8"))

    return s




def check_lang(s):
    ruletters = ['А','Б','В','Г','Д','Е','Ё','Ж','З','И','Й','К','Л','М','Н','О','П','Р','С','Т','У','Ф','Х','Ц','Ч','Ш','Щ','Ъ','Ы','Ь','Э', 'Ю','Я']
    ruabc = set([unicode(letter, "utf-8") for letter in ruletters]) | set([unicode(letter, "utf-8").lower() for letter in ruletters])
   
    def abc_str(str, abc):
        str = unicode(str)
        for letter in str:
            
            if letter not in abc | set(string.whitespace):
                return False
        return True
    
    
    if abc_str(s, set(string.letters)):
        lang = "en"
    elif abc_str(s, set(string.digits)):
        lang = '123'
    elif abc_str(s, ruabc):
        lang = "ru"
    else: lang = 'other'
    return lang

#print tr("галакси", 'ru', 'en')
#print translit("salomon")
#print check_lang('dolce gabbana')

#print find_substr_in_arr('salomon', ['123'], cutoff=0.3, variants=1)



