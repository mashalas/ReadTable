#!/usr/bin/python3

import numpy as np
import datetime
from pprint import pprint
from math import sqrt # для вычисления стандартного отклонения

"""dates = [datetime.datetime(2024, 1, 1, 0, 0), datetime.datetime(2024, 1, 2, 0, 0), datetime.datetime(2024, 1, 3, 0, 0), datetime.datetime(2024, 1, 4, 0, 0), datetime.datetime(2024, 1, 5, 0, 0)]
print(dates)
mn = min(dates)
mx = max(dates)
print("mn:", mn)
print("mx:", mx)
exit(0)"""


# удалить комментарий
def remove_comment(s, comment_symbol):
    p = s.find(comment_symbol)
    #print(s, p)
    if p >= 0:
        s = s[0:p]
    s = s.strip()
    return s

# Являются ли два массива одинаковыми по содержанию
def equal_string_lists(list1, list2, case_sensitive = True):
    if len(list1) != len(list2):
        return False # массивы различаются по длине
    for i in range(len(list1)):
        s1 = list1[i]
        s2 = list2[i]
        if not case_sensitive:
            s1 = s1.lower()
            s2 = s2.lower()
        if s1 != s2:
            return False # в i-й позиции значения различаются
    return True # два идентичных массива


# ------- Получить номера столбцов по указанным именам (вместо имени может быть номер, тогда записать этот номер) -------
def get_columns_numbers(header, custum_columns, ignore_case = False):
    if custum_columns == None:
        return []
    if type(custum_columns) == type("stroka") or type(custum_columns) == type(12345):
        # передан скаляр вместо массива - превратить в массив из одного элемента
        custum_columns = [custum_columns]
    result = []
    if len(custum_columns) == 0:
        # пустой массив - все столбцы
        result = [i for i in range(len(header))]
        return result
    # указаны столбцы (номер или имя)
    for c in custum_columns:
        c_saved = c
        if type(c) == type(123):
            # указан номер столбца
            if c < 0:
                # указан номер столбца с конца
                c = len(header) + c
            if c < 0 or c >= len(header):
                raise Exception("Invalid column number {}." . format(c_saved))
            result.append(c)
        else:
            # указано имя столбца
            if ignore_case:
                c = c.lower()
            found = False
            for j in range(len(header)):
                h = header[j]
                if ignore_case:
                    h = h.lower()
                if c == h:
                    result.append(j)
                    found = True
                    break
            if not found:
                raise Exception("Column \"{}\" not found." . format(c_saved))
    return result

#A = get_columns_numbers(["sn", "DateTime", "Stoch1"], ["stoch1", 1, "Sn"], False)
#print(A)
#exit(0)


# ----- Найти позицию строки seek в массиве items (-1 - если не найдено) -----
def seek_by_name(seek: str, items, ignore_case:bool = False):
    if ignore_case:
        seek = seek.lower()
    for i in range(len(items)):
        s = items[i]
        if ignore_case:
            s = s.lower()
        if seek == s:
            return i
    return -1


def add_simple_specification(src_column_name: str, dst_column_name:str, header, specs_list, ignore_case:bool  = False):
    src_column_index = seek_by_name(src_column_name, header, ignore_case)
    if src_column_index < 0:
        #print(ignore_case, header)
        msg = "Column [{}] not found." . format(src_column_name)
        raise Exception(msg)
    if dst_column_name == "":
        # если целевое имя столбца не указано - установить его таким же, как имя исходного столбца
        dst_column_name = src_column_name
    specs_list.append({
        "kind": "simple",
        "src_column_index": src_column_index,
        "src_column_name": src_column_name,
        "dst_column_name": dst_column_name
    })


def add_ohe_specification(src_column_name: str, specification: str, header, specs_list, ignore_case:bool = False):
    src_column_index = seek_by_name(src_column_name, header, ignore_case)
    if src_column_index < 0:
        msg = "Column [{}] not found." . format(src_column_name)
        raise Exception(msg)
    splits1 = specification.split(";")
    for s1 in splits1:
        #dst_column_index += 1
        #print(s1)
        p = s1.find("=")
        if p > 0:
            #suffix = s1[p+1:len(s1)]
            dst_column_name = s1[p+1:len(s1)]
            s1 = s1[0:p]
        else:
            #suffix = s1
            dst_column_name = src_column_name + "=" + s1
        src_values = s1.split(",")
        specs_list.append({
            "kind": "ohe",
            "src_column_index": src_column_index,
            "src_column_name": src_column_name,
            #"dst_column_name": src_column_name + "=" + suffix,
            "dst_column_name": dst_column_name,
            "src_values": src_values
        })


def add_map_specification(src_column_name:str, specification:str, dst_column_name:str, header, specs_list, ignore_case:bool = False):
    src_column_index = seek_by_name(src_column_name, header, ignore_case)
    if src_column_index < 0:
        msg = "Column [{}] not found." . format(src_column_name)
        raise Exception(msg)
    splits1 = specification.split(";")
    mappings = {}
    for s1 in splits1:
        p = s1.find("=")
        value = s1[p+1:len(s1)]
        s1 = s1[0:p]
        keys = s1.split(",")
        for k in keys:
            mappings[k] = value
    specs_list.append({
        "kind": "map",
        "src_column_index": src_column_index,
        "src_column_name": src_column_name,
        "dst_column_name": dst_column_name,
        "mappings": mappings
    })


def split_with_escaping(s:str, delimiter:str):
    result = []
    if len(delimiter) == 0:
        result.append(s)
        return result
    #
    # ab\::cd::efg => [ab::cd, efg]
    # 012345678901 {10}
    delimiter_len = len(delimiter)
    elem = ""
    i = 0
    while i < len(s):
        p1 = i
        p2 = p1 + delimiter_len
        delimiter_candidate = s[p1:p2]
        #print(delimiter_candidate)
        if delimiter_candidate == delimiter:
            #print("delimiter found")
            delimiter_found = True
            if len(elem) > 0:
                if elem[-1] == "\\":
                    delimiter_found = False
                    elem = elem[0:len(elem)-1]
                    #print("not delimiter")
            if delimiter_found:
                if elem != "" or len(result) > 0: # чтобы не добавлять пустой первый элемент
                    result.append(elem)
                elem = ""
                i += delimiter_len
                continue
        elem += s[i]
        i += 1
    if len(elem) > 0:
        result.append(elem)
    return result

#s = "ab\::cd::efg"; d = "::"
#s = "ab:cd\:efg:123"; d = ":"
#s = ":::ab:::cd\:::efg:::123"; d = ":::"
#s = ":::ab:::cd\:::efg:::123:::"; d = ":::"
#parts = split_with_escaping(s, d)
#print(parts)
#exit(0)

def parse_columns_specifications(str_specifications_list, header, ignore_case:bool = False):
    result = []
    for one_str_spec in str_specifications_list:
        #parts = one_str_spec.split(":")
        parts = split_with_escaping(one_str_spec, ":")
        #print(parts); exit(0)
        if len(parts) >= 3:
            src_column_name = parts[0]
            transformation = parts[1].lower()
            specification = parts[2]
            
            # указана не просто имя столбца из файла, но и некоторое действие с этим столбцом (OneHotEncoding, Mapping, Simple); первый элемент parts[] - имя столбца из файла
            if transformation == "ohe":
                add_ohe_specification(src_column_name, specification, header, result, ignore_case)
            elif transformation == "map":
                if len(parts) > 3:
                    dst_column_name = parts[3]
                else:
                    dst_column_name = src_column_name
                add_map_specification(src_column_name, specification, dst_column_name, header, result, ignore_case)
            elif transformation == "simple":
                add_simple_specification(src_column_name, specification, header, result, ignore_case)
            else:
                msg = "Wrong transformation [{}]" . format(specification)
                raise Exception(msg)
        else:
            # указано только имя столбца
            add_simple_specification(parts[0], "", header, result, ignore_case)
    return result

"""
header = ["height", "Width", "size", "Trend", "Stoch:13x5x3"]
#str_spec = ["width"]
#str_spec = ["width", "height"]
#str_spec = ["width:simple:wdt"]
#str_spec = ["trend:OHE:sell,down=TrendDown;flat;buy,up"]
#str_spec = ["trend:map:sell,down=-1;flat=0;buy,up,bear=1"]
#str_spec = ["trend:map:sell,down=-1;flat=0;buy,up,bear=1:TrendSign"]
#str_spec = ["trend:map:sell,down=-1;flat=0;buy,up,bear=1:trn"]
str_spec = ["stoch\:13x5x3:OHE:q=StochQ;w,W=StochW;e"]
spec = parse_columns_specifications(str_spec, header, True)
print("------------------- header:", header, " -------------------")
pprint(spec)
exit(0)
"""

"""def func1():
    return 123, "abc", 456.789

xi, s1, xf = func1()
print(xi, s1, xf); exit(0)"""

#print("abc123"[1].isdigit()); exit(0)

# ------- Попытаться преобразовать строку в дату/время; вернуть дату или None, если конвертирование не удалось -------
def string_to_time(s):
    # !!! добавить генерацию ошибки, если конвертирование не удалось
    #                     123456
    # dd.mm.yyyy hh:mm:ss.micros
    # yyyy-mm-dd hh:mm:ss.micros
    # 01234567890123456789012345
    if len(s) < 10:
        # слишком мало символов, чтобы быть датой
        return None
    year = None
    month = None
    day = None
    if (
        s[0].isdigit() and
        s[1].isdigit() and
        not(s[2].isdigit()) and
        s[3].isdigit() and
        s[4].isdigit() and
        not(s[5].isdigit()) and
        s[6].isdigit() and
        s[7].isdigit() and
        s[8].isdigit() and
        s[9].isdigit() and
        1 == 1
    ) :
        # dd.mm.yyyy hh:mm:ss
        # 0123456789012345678
        try:
            day = int(s[0:2])
            month = int(s[3:5])
            year = int(s[6:10])
        except:
            return None
    elif (
        s[0].isdigit() and
        s[1].isdigit() and
        s[2].isdigit() and
        s[3].isdigit() and
        not(s[4].isdigit()) and
        s[5].isdigit() and
        s[6].isdigit() and
        not(s[7].isdigit()) and
        s[8].isdigit() and
        s[9].isdigit() and
        1 == 1
    ) :
        # yyyy-mm-dd hh:mm:ss
        # 0123456789012345678
        try:
            year = int(s[0:4])
            month = int(s[5:7])
            day = int(s[8:10])
        except:
            return None
    else:
        return None
    hour = 0
    minute = 0
    second = 0
    micros = 0
    # dd.mm.yyyy hh:mm:ss
    # 0123456789012345678
    if len(s) >= 13:
        try:
            hour = int(s[11:13])
        except:
            return None
    if len(s) >= 16:
        try:
            minute = int(s[14:16])
        except:
            return None
    if len(s) >= 19:
        try:
            second = int(s[17:19])
        except:
            return None
        
    if len(s) >= 21:
        i = 20
        micros_str = ""
        while i < len(s) and i < 26:
            if s[i].isdigit():
                micros_str += s[i]
                i += 1

        # удалить ведущие нули
        leading_zeros_count = 0
        while len(micros_str) > 0 and micros_str[0] == "0":
            leading_zeros_count += 1
            micros_str = micros_str[1:len(micros_str)]
                
        try:
            micros = int(micros_str)
            #micros = float("0." + micros_str)
        except:
            return None

    #print(year, month, day, hour, minute, second)
    try:
        result = datetime.datetime(year, month, day, hour, minute, second, micros)
    except:
        return None
    return result


s = "29.02.2024 00:07:03.0012";
#s = "2029.02.29"
d = string_to_time(s)
print(d)
#d = datetime.datetime(2024, 4, 19, 16, 39, 41, 0012); print(d)
exit(0)

# ------ Среднее значение для массива целых или дробных чисел -------
def get_avg(items) -> float:
    sum = 0.0
    for x in items:
        sum += x
    avg = sum / len(items)
    return avg

# ------ Стандартное отклонение для массива целых или дробных чисел -------
def get_std_dev(items, avg) -> float:
    st = 0.0
    for x in items:
        st += (x - avg)*(x - avg)
    st /= len(items)
    st = sqrt(st)
    return st

# ------ Сколько раз значение встречается в массиве -------
def count_value_in_array(seek, items):
    cnt = 0
    for x in items:
        if x == seek:
            cnt += 1
    return cnt

# ------------------------------- class ReadTable ------------------------------
class ReadTable:
    delimiter:str = "\t"
    #comment_sequence: str = "#"
    comment_symbol: str = "#"
    header = [] # названия столбцов
    header__ignore_case: bool = False # игнорировать различие в регистре при сопоставлении указанных пользователем названий столбцов с названиями столбцов в файле
    transform__ignore_case: bool = False # игнорировать различие в регистре при сопоставлении пользовательских значений трансформаций OHE и Map
    ignore_bad: bool = False # при несовпадении количества столбцов с размером заголовка продолжать чтение файла (True) или вызвать исключение (False)
    notify_on_bad: bool = False # выдавать сообщение при обнаружении некорректных строк
    comma_to_dots: bool = False # заменять запятые на точки в дробных числах
    procentiles = [0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.98, 0.99]
    unique_max_count: int = 10
    multidelimiters_to_one: bool = False # заменять несколько разделителей столбцов на один
    print_warnings: bool = False

    NP__DEFAULT_ROWS_COUNT: int = 3 # сколько строк изначально выделяется в numpy-массиве
    np__x_reserved_count:int = 0
    np__y_reserved_count:int = 0
    np__x_fact_count:int = 0
    np__y_fact_count:int = 0
    #np__data_rows_count: int = 0 # фактически используемое количество строк в numpy-массиве
    #np__reserved_rows_count: int = 0 # сколько строк зарезирвировано в numpy-массиве
    np__reservation_increment = 1.618 # на сколько увеличить количество зарезервированных строк в numpy-массиве
    np__dtype = np.float64 # тип данных numpy-массивов X и Y

    XNames = []
    YNames = []
    #fields = {}
    A = None # analyze
    X = None
    Y = None
    #Data = None

    OHE_MATCH = 1.0
    OHE_MISS = 0.0

    DATA_TYPE__INTEGER = "i"
    DATA_TYPE__FLOAT = "f"
    DATA_TYPE__TIME = "t"
    DATA_TYPE__STRING = "s"
    DATA_TYPE__UNKNOWN = "?"


    def __init__(self, delimiter: str = "\t", comment_symbol: str = '#'):
        self.delimiter = delimiter
        self.comment_symbol = comment_symbol
        self.reset()

    def reset(self):
        self.header.clear()
        self.np__data_rows_count = 0
        self.np__reserved_rows_count = 0
        #self.fields = {}
        self.A = None
        self.X = None
        self.Y = None
        #self.Data = None
        #self.reset_errors()


    def get_float(self, s: str) -> float:
        if self.comma_to_dots:
            s = s.replace(",", ".")
        return float(s)


    # ----- Добавить в numpy-массив значения из массива items[] содержащем значения некоторой строки читаемого файла -----
    def add_to_numpy(self, columns_specification, items, NPArray, fact_rows_count) -> None:
        for dst_column_index in range(len(columns_specification)):
            spec = columns_specification[dst_column_index]
            src_column_index = spec["src_column_index"]
            kind = spec["kind"]
            value = items[src_column_index]
            if kind == "map":
                NPArray[fact_rows_count][dst_column_index] = spec["mappings"][value]
            elif kind == "ohe":
                if value in spec["src_values"]:
                    NPArray[fact_rows_count][dst_column_index] = self.OHE_MATCH
                else:
                    NPArray[fact_rows_count][dst_column_index] = self.OHE_MISS
            else:
                NPArray[fact_rows_count][dst_column_index] = self.get_float(items[src_column_index])


    # ----- Добавить записи как есть в словарь -----
    def add_to_analyze(self, AnalyzeColumnsNumbs, items, A):
        for ci in AnalyzeColumnsNumbs:
            cn = self.header[ci]
            value = items[ci]
            A[cn]["items"].append(value)


    # ------- На какой тип данных похожа строка переданная в value -------
    def detect_data_type(self, value, comma_to_dots = False):
        try:
            # является ли value целым числом
            x = int(value)
            return x, self.DATA_TYPE__INTEGER
        except:
            pass

        try:
            # является ли value дробным числом
            value_tmp = value
            if comma_to_dots:
                value_tmp = value
            x = float(value_tmp)
            return x, self.DATA_TYPE__FLOAT
        except:
            pass

        # является ли value датой/временем в форматах dd.mm.yyyy hh:mm:ss или yyyy-mm-dd hh:mm:ss
        x = string_to_time(value)
        if x != None:
            return x, self.DATA_TYPE__TIME

        # оставить value строкой
        return value, self.DATA_TYPE__STRING


    # ------- Для анализируемых столбцов определить тип данных и сконвертировать прочитанные записи в соответствующий тип данных (изначально читаются как строка) ------
    def analyze__data_types(self, A):
        for cn in A.keys():
            #print(cn)
            for i in range(len(A[cn]["items"])):
                value = A[cn]["items"][i]
                value, data_type = self.detect_data_type(value, self.comma_to_dots)
                #print(cn, i, value, data_type)
                # Типы данных: целое, дробное, дата/время, строка
                if A[cn]["data_type"] == self.DATA_TYPE__UNKNOWN:
                    # +++++ это первая строка, тип данных ещё не был определён +++++
                    A[cn]["data_type"] = data_type
                    if data_type == self.DATA_TYPE__STRING:
                        # если для текущего столбца тип данных строка - то дальше никакой конвертации выполнять не надо
                        break
                    else:
                        A[cn]["items"][i] = value
                elif data_type != A[cn]["data_type"]:
                    convert_to = None
                    # +++++ тип данных для столбца уже определён, но новая строка имеет другой тип данных +++++
                    if A[cn]["data_type"] == self.DATA_TYPE__INTEGER:
                        # +++ для предыдущих строк тип данных был определён как целое число +++
                        if data_type == self.DATA_TYPE__FLOAT:
                            # новый тип данных - дробное число
                            convert_to = self.DATA_TYPE__FLOAT
                        else:
                            # целое -> строка (даже если определилось как дата/время)
                            convert_to = self.DATA_TYPE__STRING
                    elif A[cn]["data_type"] == self.DATA_TYPE__FLOAT:
                        # +++ для предыдущих строк тип данных был определён как дробное число +++
                        if data_type == self.DATA_TYPE__INTEGER:
                            # среди дробных чисел встретилось одно без дробной части - привести его к дробному
                            data_type = self.DATA_TYPE__FLOAT
                            value = float(value)
                        if data_type != A[cn]["data_type"]:
                            # типы данных различаются - конвертировать в строку
                            convert_to = self.DATA_TYPE__STRING
                    elif A[cn]["data_type"] == self.DATA_TYPE__TIME:
                        # +++ для предыдущих строк тип данных был определён как дата/время +++
                        if data_type != A[cn]["data_type"]:
                            # типы данных различаются - конвертировать в строку
                            convert_to = self.DATA_TYPE__STRING
                    elif A[cn]["data_type"] == self.DATA_TYPE__STRING:
                        # +++ для предыдущих строк тип данных был определён как строка - ничего не менять +++
                        pass

                    if convert_to == self.DATA_TYPE__FLOAT:
                        A[cn]["data_type"] = self.DATA_TYPE__FLOAT
                        for j in range(i):
                            A[cn]["items"][j] = float(A[cn]["items"][j])
                    if convert_to == self.DATA_TYPE__STRING:
                        A[cn]["data_type"] = self.DATA_TYPE__FLOAT
                        for j in range(i):
                            A[cn]["items"][j] = str(A[cn]["items"][j])

                if data_type == A[cn]["data_type"] and data_type != self.DATA_TYPE__STRING:                    
                    A[cn]["items"][i] = value
        #pprint(A); exit(0)


    def analyze__count_statistics(self, A):
        #print(A)
        for cn in A.keys():
            #print(cn)
            A[cn]["stat"] = {}
            if A[cn]["data_type"] == self.DATA_TYPE__INTEGER or A[cn]["data_type"] == self.DATA_TYPE__FLOAT:
                # +++ столбец с целыми или дробными числами +++
                A[cn]["stat"]["avg"] = get_avg(A[cn]["items"])
                A[cn]["stat"]["std_dev"] = get_std_dev(A[cn]["items"], A[cn]["stat"]["avg"])
            if A[cn]["data_type"] == self.DATA_TYPE__INTEGER or A[cn]["data_type"] == self.DATA_TYPE__FLOAT or A[cn]["data_type"] == self.DATA_TYPE__TIME:
                A[cn]["stat"]["min"] = min(A[cn]["items"])
                A[cn]["stat"]["max"] = max(A[cn]["items"])
            if A[cn]["data_type"] == self.DATA_TYPE__INTEGER or A[cn]["data_type"] == self.DATA_TYPE__TIME or A[cn]["data_type"] == self.DATA_TYPE__STRING:
                unique_items = list(set(self.A[cn]["items"]))
                #print(unique_items)
                A[cn]["stat"]["unique_count"] = len(unique_items)
                #A[cn]["stat"]["unique_values"] = {}
                unique_stat = []
                for u in unique_items:
                    cnt = count_value_in_array(u, A[cn]["items"])
                    #unique_stat[u] = cnt
                    unique_stat.append({"value": u, "cnt": cnt})
                #print(unique_stat);
                unique_stat_sorted = sorted(unique_stat, key = lambda d: d["cnt"], reverse=True)
                #print(unique_stat_sorted);
                A[cn]["stat"]["unique_frequency_top"] = []
                for elem in unique_stat_sorted:
                    A[cn]["stat"]["unique_frequency_top"].append(elem)
                    #A[cn]["stat"]["unique_frequency_top"][elem["value"]] = elem["cnt"]
                    if self.unique_max_count > 0 and len(A[cn]["stat"]["unique_frequency_top"]) >= self.unique_max_count:
                        break

    def print_stat(self, columns = [], ignore_case: bool = False):
        if type(columns) == type("stroka"):
            # передан один столбец в виде строки - сконвертирвать в массив из одного элемента
            columns = [columns]
        if ignore_case and len(columns) > 0:
            for i in range(len(columns)):
                columns[i] = columns[i].lower()
        for cn in self.A.keys():
            #print(cn)
            if len(columns) > 0:
                # перечислены имена столбцов для которых нужно вывести статистику
                cn_seek = cn
                if ignore_case:
                    cn_seek = cn_seek.lower()
                if not cn_seek in columns:
                    # текущий столбец не находится в списке столбцов для которых нужно вывести статистику
                    continue
            # +++ вывести статистику для столбца с именем cn +++
            print("------- Statistic for column \"{}\" -------" . format(cn))
            data_type = "unknown"
            if self.A[cn]["data_type"] == self.DATA_TYPE__INTEGER:
                data_type = "integer"
            elif self.A[cn]["data_type"] == self.DATA_TYPE__FLOAT:
                data_type = "float"
            elif self.A[cn]["data_type"] == self.DATA_TYPE__TIME:
                data_type = "date/time"
            elif self.A[cn]["data_type"] == self.DATA_TYPE__STRING:
                data_type = "string"
            print("  data_type:", data_type)
            if self.A[cn]["data_type"] == self.DATA_TYPE__INTEGER or self.A[cn]["data_type"] == self.DATA_TYPE__FLOAT or self.A[cn]["data_type"] == self.DATA_TYPE__TIME:
                print("  min:", self.A[cn]["stat"]["min"])
                print("  max:", self.A[cn]["stat"]["max"])
            if self.A[cn]["data_type"] == self.DATA_TYPE__INTEGER or self.A[cn]["data_type"] == self.DATA_TYPE__FLOAT:
                print("  avg:", self.A[cn]["stat"]["avg"])
                print("  std_dev:", self.A[cn]["stat"]["std_dev"])
            if self.A[cn]["data_type"] == self.DATA_TYPE__INTEGER or self.A[cn]["data_type"] == self.DATA_TYPE__TIME or self.A[cn]["data_type"] == self.DATA_TYPE__STRING:
                print("  unique count:", self.A[cn]["stat"]["unique_count"])
                #for key in self.A[cn]["stat"]["unique_frequency_top"]
                for i in range(len(self.A[cn]["stat"]["unique_frequency_top"])):
                    msg = "    "
                    msg += str(i+1) + ")"
                    msg += " " + str(self.A[cn]["stat"]["unique_frequency_top"][i]["value"])
                    msg += ": " + str(self.A[cn]["stat"]["unique_frequency_top"][i]["cnt"])
                    print(msg)

            print("")
    

    def _read(
            self,
            files_list,
            header_only = False, # только прочитать заголовок и сразу завершить работу
            AnalyzeColumns = None, # проанализировать эти столбцы (среднее, разброс для числе, количество для строк и т.д.)
            XColumns = None, 
            YColumns = None

    ) -> None:
        for filename in files_list:
            print("-----", filename, "-----")
            f = open(filename, "rt")
            self.header.clear()
            AColumnsNumbs = None
            XColumnsSpecs = None
            YColumnsSpecs = None
            file_line_number = 0
            for s in f:
                file_line_number += 1
                s = s.strip()
                if s[0] == self.comment_symbol:
                    continue # если первыми символом символ комментария - пропустить строку
                #s = remove_comment(s, self.comment_sequence)
                #if len(s) == 0:
                #    continue # пустая строка

                parts = s.split(self.delimiter)
                if len(parts) == 0:
                    continue

                #print(s, parts)

                if len(self.header) == 0:
                    # +++ для текущего файла заголовок ещё не был прочитан +++
                    self.header = parts.copy()
                    if header_only:
                        return

                    if AnalyzeColumns != None:
                        AnalyzeColumnsNumbs = get_columns_numbers(self.header, AnalyzeColumns, self.header__ignore_case)
                        #print(AnalyzeColumnsNumbs); exit(0)
                        self.A = {}
                        for ci in AnalyzeColumnsNumbs:
                            cn = self.header[ci]
                            self.A[cn] = {
                                "data_type": self.DATA_TYPE__UNKNOWN,
                                "items": []
                            }
                        #print(self.A); exit(0)
                    if XColumns != None:
                        XColumnsSpecs = parse_columns_specifications(XColumns, self.header, self.header__ignore_case)
                        self.XNames.clear()
                        for spec in XColumnsSpecs:
                            self.XNames.append(spec["dst_column_name"])
                        if self.X == None:
                            self.X = np.zeros((self.NP__DEFAULT_ROWS_COUNT, len(XColumnsSpecs)), dtype=self.np__dtype)
                            self.np__x_reserved_count = self.NP__DEFAULT_ROWS_COUNT
                    if YColumns != None:
                        YColumnsSpecs = parse_columns_specifications(YColumns, self.header, self.header__ignore_case)
                        self.YNames.clear()
                        for spec in YColumnsSpecs:
                            self.YNames.append(spec["dst_column_name"])
                        if self.Y == None:
                            self.Y = np.zeros((self.NP__DEFAULT_ROWS_COUNT, len(YColumnsSpecs)), dtype=self.np__dtype)
                            self.np__y_reserved_count = self.NP__DEFAULT_ROWS_COUNT
                    # завершили обработку строки с заголовком
                    continue
                # +++ заголовок текущего файла уже был прочитан, читается строка с данными +++
                if len(parts) != len(self.header):
                    # различается количество столбцов в строке с данными и в заголовке файла
                    msg = "For line #{} number of columns={} <> size of header={}" . format(file_line_number, len(parts), len(self.header))
                    if self.ignore_bad:
                        # игнорировать строки с ошибками
                        if self.print_warnings:
                            print("WARNING!", msg)
                        continue
                    else:
                        # останавливаться при возникновении ошибки
                        raise Exception(msg)

                # количество столбцов с данными совпадает с количеством столбцов в заголовке
                if AnalyzeColumns != None:
                    # анализ данных, но сами данные тоже добавляются
                    self.add_to_analyze(AnalyzeColumnsNumbs, parts, self.A)
                if XColumns != None:
                    # добавить строку в numpy-массив X[]
                    self.add_to_numpy(XColumnsSpecs, parts, self.X, self.np__x_fact_count)
                    self.np__x_fact_count += 1
                    if self.np__x_fact_count == self.np__x_reserved_count:
                        self.np__x_reserved_count = int(self.np__reservation_increment * self.np__x_reserved_count)
                        self.X.resize((self.np__x_reserved_count, len(XColumnsSpecs)), refcheck=False)
                if YColumns != None:
                    # добавить строку в numpy-массив Y[]
                    self.add_to_numpy(YColumnsSpecs, parts, self.Y, self.np__y_fact_count)
                    self.np__y_fact_count += 1
                    if self.np__y_fact_count == self.np__y_reserved_count:
                        self.np__y_reserved_count = int(self.np__reservation_increment * self.np__y_reserved_count)
                        self.Y.resize((self.np__y_reserved_count, len(YColumnsSpecs)), refcheck=False)

                


            f.close()

            #print("header:", self.header)
            #print("XColumnsNumbers:", XColumnsNumbers)
            #print("YColumnsNumbers:", YColumnsNumbers)
        if XColumns != None:
            if self.np__x_fact_count != self.np__x_reserved_count:
                # прочитано строк меньше, чем зарезервировано в памяти
                self.X.resize((self.np__x_fact_count, len(XColumnsSpecs)), refcheck=False)
                pass
        if YColumns != None:
            if self.np__y_fact_count != self.np__y_reserved_count:
                # прочитано строк меньше, чем зарезервировано в памяти
                self.Y.resize((self.np__y_fact_count, len(YColumnsSpecs)), refcheck=False)
                pass
        if AnalyzeColumns != None:
            self.analyze__data_types(self.A)
            self.analyze__count_statistics(self.A)

    def get_header(self, filename):
        files_list = [filename]
        self._read(files_list, header_only=True)
        return self.header.copy()
    

    def rename_X_column(self, old_name:str, new_new:str) -> None:
        self._rename_column("x", old_name, new_new)

    def rename_Y_column(self, old_name:str, new_new:str) -> None:
        self._rename_column("y", old_name, new_new)

    def _rename_column(self, table_name: str, old_name: str, new_name: str) -> None:
        if self.header__ignore_case:
            old_name = old_name.lower()
        if table_name.lower() == "x":
            for i in range(len(self.XNames)):
                c = self.XNames[i]
                if self.header__ignore_case:
                    c = c.lower()
                if c == old_name:
                    self.XNames[i] = new_name
        elif table_name.lower() == "y":
            for i in range(len(self.YNames)):
                c = self.YNames[i]
                if self.header__ignore_case:
                    c = c.lower()
                if c == old_name:
                    self.YNames[i] = new_name


def np_test1():
    rows_count = 5
    columns_count = 2
    A = np.zeros((rows_count, columns_count), dtype=np.float32)
    sn = 0
    for i in range(rows_count):
        for j in range(columns_count):
            sn += 1
            A[i][j] = sn
    A.resize((rows_count+1, columns_count), refcheck=False)
    print(A)

if __name__ == "__main__":
    #np_test1(); exit(0)

    #rt1 = ReadTable("\t", "#")
    rt1 = ReadTable()
    rt1.header__ignore_case = True
    rt1.comma_to_dots = True
    files_list = ["G:\\sources\\python\\ml\\_modules\\ReadTable3\\file1.txt"]
    XColumns = ["stoch\:13x5x3", "pclose"]
    YColumns = ["Trend:OHE:sell,bear,down;flat;buy,bull,up"]

    # header = rt1.get_header(files_list[0]); print("header:", header); exit(0)

    rt1._read(files_list, XColumns=XColumns, YColumns=YColumns)

    #print(rt1)
    print("X:", rt1.X)
    print("Y:", rt1.Y)
    print("XNames:", rt1.XNames)
    print("YNames:", rt1.YNames)

    rt1.rename_Y_column("Trend=sell,bear,down", "TrendDown")
    rt1.rename_Y_column("Trend=flat", "TrendFlat")
    rt1.rename_Y_column("Trend=buy,bull,up", "TrendUp")
    print("YNames:", rt1.YNames)

    print("header:", rt1.header)
    rt1._read(files_list, AnalyzeColumns=["DateTime", "PClose", "stoch:13x5x3", "Trend"])
    #pprint(rt1.A)
    rt1.print_stat("Trend")

    #print("XColumnsSpecs:", rt1.XColumnsSpecs)