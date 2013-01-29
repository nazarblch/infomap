# -*- coding: utf-8 -*-
import codecs

#------------------чтение и запись файлов-----------------------------------------------------------
    
def r_lst_of_str(file_path): # считать файл построчно
    _input = codecs.open(file_path, encoding='utf-8')
    return [word for word in _input.read().split('\n') if word!=""]
    _input.close()

def r_set_of_word(file_path): # получить из файла множество слов
    lists_in_list=[i.split() for i in r_lst_of_str(file_path)]
    return set([word for l in lists_in_list for word in l])

def w_lst(lst, file_path):
    _output=codecs.open(file_path, mode='w', encoding='utf-8')
    for i in lst:
        _output.write(i+'\n')
    _output.close()
    return True

def w_str(string, file_path):
    _output=codecs.open(file_path, mode='w', encoding='utf-8')
    _output.write(string)
    _output.close()
    return True