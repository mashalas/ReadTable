#!/usr/bin/python3

from pprint import pprint
from collections import OrderedDict
import datetime
import numpy as np
import statistics


NPCOLUMN_KIND__SIMPLE = "simple"
NPCOLUMN_KIND__OHE = "ohe"
NPCOLUMN_KIND__MAPPING = "mapping"

DATA_TYPE__UNKNOWN = "unknown"
DATA_TYPE__INTEGER = "integer"
DATA_TYPE__FLOAT = "float"
DATA_TYPE__TIME = "time"
DATA_TYPE__STRING = "string"

"""
x1 = [
    "abc", 
    "cde",
    [1,2,3], 
    {
        "src_name": "q1",
        "dst_name": "w2",
        "stat": {
            "begin":-1.0, 
            "end":+1.0, 
            "values":["up", "down", "flat"]
        }
    }
]
x2 = x1.copy()
x1[0] = "qaz"
pprint(x2)
exit(0)
"""

# ----- удалить комментарий -----
def remove_comment(s, comment_sequence):
    p = s.find(comment_sequence)
    if p >= 0:
        s = s[0:p]
    s = s.strip()
    return s

# ----- Попытаться преобразовать строку к дробному числу (при ошибке - None) -----
# ----- comma_to_dots: когда True - заменить запятую на точку перед конвертацией -----
def strToFloat(s, comma_to_dots = False):
    if comma_to_dots:
        s = s.replace(",", ".")
    result = None
    try:
        result = float(s)
    except:
        result = None
    return result

#x = strToFloat(",123456789", True);  print("x=", x, type(x));  exit(0)

# ----- Среднее отклонение от среднего значения (заранее вычисленного) -----
def get_avg_deviation(items, avg:float) -> float:
    deviation = 0.0
    n = 0
    for x in items:
        deviation += abs(x - avg)
        n += 1
    deviation /= n
    return deviation

# ----- Процентиль ------
def get_procentile(prc:float, items, already_sorted:bool = False, keep_out_sorted:bool = False):
    if not already_sorted:
        if keep_out_sorted:
            # наружу из фукнции выйдет сортированный массив (сортировать переданный массив)
            items.sort() 
        else:
            # сортировка не выйдет за пределы функции (создать новый массив для сортировки)
            items = sorted(items) 

    n = len(items)
    p = int(prc * n)
    if p < 0:
        p = 0
    if p >= n:
        p = n - 1
    return items[p]

# ----- На основе массива items получить список с наиболее частыми значениями списка -----
# ----- каждый элемент полученного массива - кортёж, в котором первый элемент - значение из items[], 
# второй элемент кортежа - сколько раз это значение встречается в items[] -----
def get_most_frequent(items, max_count = 0):
    uniq_dict = {}
    for x in items:
        if not x in uniq_dict:
            uniq_dict[x] = 1
        else:
            uniq_dict[x] += 1
    #print(uniq_dict)
    uniq_counting = []
    for key in uniq_dict.keys():
        uniq_counting.append({"v":key, "n": uniq_dict[key]})
    uniq_counting = sorted(uniq_counting, key=lambda d:d["n"], reverse=True)
    #print(uniq_counting)
    result = []
    for i in range(len(uniq_counting)):
        if max_count > 0 and i >= max_count:
            break
        result.append((uniq_counting[i]["v"], uniq_counting[i]["n"], ))
    return result
    #uniq_count = len(uniq_counting)
    #return uniq_count, result

"""X = [10, 8, 7, 10, 11, 7, 12, 100, 10, 7, 8, 5, 10, 6]
print(X)
Y = get_most_frequent(X, 400)
uc = len(set(X))
print("unique count:", uc)
print(Y)
exit(0)"""

# ----- Гистограмма при разбивке на barCount интервалов -----
def calcHistogram(items, barsCount, minValue = None, maxValue = None):
    if minValue == None:
        minValue = min(items)
    if maxValue == None:
        maxValue = max(items)

    # [2 5 8 11]  [ (2-5) (5-8) (8-11) ]   min=2, max=11, BarsCount=3 => barSize=(11-2)/3 = 9/3 = 3
    barSize = (maxValue - minValue) / barsCount
    result = []
    for i in range(barsCount):
        barMin = minValue + i*barSize
        barMax = barMin + barSize
        cnt = 0
        for x in items:
            if x >= barMin and x <= barMax:
                cnt += 1
        #result.append({"min": barMin, "max": barMax, "cnt": cnt})
        elem = OrderedDict()
        elem["min"] = barMin
        elem["max"] = barMax
        elem["cnt"] = cnt
        result.append(elem)
    return result

# ----- Гистограмма составляемая из символов char -----
def charsHistogram(histogram, maxCharsCount = 50, char = "X"):
    result = []
    max_cnt = histogram[0]["cnt"]
    for h in histogram:
        if h["cnt"] > max_cnt:
            max_cnt = h["cnt"]
    max_cnt = float(max_cnt)
    for h in histogram:
        #charsCount = int(float(h["cnt"]) / max_cnt * maxCharsCount)
        charsCount_float = float(h["cnt"]) / max_cnt * maxCharsCount
        charsCount = int(round(charsCount_float))
        s = char * charsCount
        result.append(s)
    return result

"""
X = [
    2.0751807571421494,
    1.0391028584276123,
    -1.6558126466519922,
    -2.572104560492662,
    -1.832003875258554,
    0.5862320960932519,
    0.08546626872509777,
    0.26758993956038407,
    -0.027422134234278164,
    1.542746340925399,
    -0.036116125211141284,
    0.25920118891616484,
    -0.4845548325412525,
    -0.1978893237790782,
    -1.7054633048468613,
    1.165640674176765,
    -0.2800543198900789,
    0.9528562680881849,
    0.18192888785686775,
    -1.3276614896327792
]
print(X)
hist = calcHistogram(X, 7, min(X), max(X))
pprint(hist)
char_hist = charsHistogram(hist, 100)
pprint(char_hist)
exit(0)
"""

# ----- Получить самую длинную строку в массиве -----
def getLongestString(items):
    longestString = items[0]
    max_len = len(longestString)
    for s in items:
        if len(s) > max_len:
            longestString = s
            max_len = len(longestString)
    return longestString

#X = ["qq", "www", "1234", "eee", "4567"]
#print(getLongestString(X))
#exit(0)

# ----- Подсчёт статистик для перечислимых типов данных (целое, строка, время) -----
def calcEnumeratedStatistics(items, stat_dict, most_frequent_count = 10) -> None:
    stat_dict["unique_count"] = len(set(items))
    stat_dict["most_frequent"] = get_most_frequent(items, most_frequent_count)

# ----- Подсчёт статистик для числовых типов данных (целое, дробное) -----
def calcNumericStatistics(items, stat_dict) -> None:
    stat_dict["min"] = min(items)
    stat_dict["max"] = max(items)
    stat_dict["avg"] = statistics.mean(items)
    stat_dict["stdev"] = statistics.stdev(items)
    #stat_dict["avgdev"] = get_avg_deviation(items, stat_dict["avg"])

#x1 = 100.5
#s1 = str(x1)
#s1 = "{:.2f}" . format(x1)
#print(s1)
#exit(0)
    

# ----- Подсчёт процентилей для массива (числа или время) -----
def calcProcentiles(items, stat_dict, procentiles = [0.1, 0.25, 0.5, 0.75, 0.9]) -> None:
    items_sorted = sorted(items)
    stat_dict["procentiles"] = OrderedDict()
    for prc in procentiles:
        #prc_name = "prc#" + str(prc)
        #stat_dict[prc_name] = get_procentile(prc, items_sorted, already_sorted=True)
        prc_name = "prc#{:.2f}" . format(prc)
        stat_dict["procentiles"][prc_name] = get_procentile(prc, items_sorted, already_sorted=True)


# ------- Попытаться преобразовать строку в дату/время; вернуть дату или None, если конвертирование не удалось -------
def strToTime(s):
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
        
    if len(s) >= 21 and not s[19].isdigit() :
        # микросекунды
        i = 20
        micros_str = ""
        while i < len(s) and i < 26:
            if s[i].isdigit():
                micros_str += s[i]
                i += 1

        n1 = len(micros_str)
        #print("micros_str:", micros_str, "  n1:", n1)
        # удалить ведущие нули
        leading_zeros_count = 0
        while len(micros_str) > 0 and micros_str[0] == "0":
            leading_zeros_count += 1
            micros_str = micros_str[1:len(micros_str)]
                
        try:
            micros = int(micros_str)
            #micros = float("0." + micros_str)
            n2 = 6 - n1
            for i in range(n2):
                micros *= 10
            #print("micros:", micros)
        except:
            return None

    #print(year, month, day, hour, minute, second)
    try:
        result = datetime.datetime(year, month, day, hour, minute, second, micros)
    except:
        return None
    return result

# ------- На какой тип данных похожа строка переданная в s -------
# ----- вернуть приведённое к определённому типу значение и название типа данных -----
def detectDataTypeForString(s:str, comma_to_dots:bool) -> str:
    try:
        # является ли переданный параметр целым числом
        x = int(s)
        return DATA_TYPE__INTEGER
    except:
        pass

    # является ли переданный параметр дробным числом (возможно, запятая вместо точки)
    x = strToFloat(s, comma_to_dots)
    if x != None:
        return DATA_TYPE__FLOAT

    # является ли переданный параметр датой/временем в форматах dd.mm.yyyy hh:mm:ss или yyyy-mm-dd hh:mm:ss
    x = strToTime(s)
    if x != None:
        return DATA_TYPE__TIME

    # оставить переданный параметр строкой
    return DATA_TYPE__STRING

# ----- Определить тип данных (целое, дробное, время, строка) -----
def detectDataTypeForList(items, comma_to_dots:bool) -> str:
    if len(items) == 0:
        # нет данных в массиве
        return DATA_TYPE__UNKNOWN
    detectedDataType = DATA_TYPE__UNKNOWN
    for x in items:
        currentDataType = detectDataTypeForString(x, comma_to_dots)
        if detectedDataType == DATA_TYPE__UNKNOWN:
            # первый элемент списка
            detectedDataType = currentDataType
            if detectedDataType == DATA_TYPE__STRING:
                # если строка - дальше не проверять, так и останется строка
                break
        else:
            # последующие элементы, сравнить с типом определённым для предшествующих элементов
            if currentDataType != detectedDataType:
                # для нового элемента тип данных отличается от предыдущих
                if currentDataType == DATA_TYPE__INTEGER:
                    # новый элемент - целое число
                    if detectedDataType == DATA_TYPE__FLOAT:
                        currentDataType = DATA_TYPE__FLOAT
                    elif detectedDataType == DATA_TYPE__TIME:
                        detectedDataType = DATA_TYPE__STRING
                elif currentDataType == DATA_TYPE__FLOAT:
                    # новый элемент - дробное число
                    if detectedDataType == DATA_TYPE__INTEGER:
                        detectedDataType = DATA_TYPE__FLOAT
                    elif detectedDataType == DATA_TYPE__TIME:
                        detectedDataType = DATA_TYPE__STRING
                elif currentDataType == DATA_TYPE__TIME:
                    # новый элемент - время
                    if detectedDataType == DATA_TYPE__INTEGER:
                        detectedDataType = DATA_TYPE__STRING
                    elif detectedDataType == DATA_TYPE__FLOAT:
                        detectedDataType = DATA_TYPE__STRING
                elif currentDataType == DATA_TYPE__STRING:
                    detectedDataType = DATA_TYPE__STRING
                if detectedDataType == DATA_TYPE__STRING:
                    # столбец останется строкой
                    break
    return detectedDataType

def convertListToDataType(items, targetDataType:str, comma_to_dots:bool) -> None:
    itemsCount = len(items)
    if targetDataType == DATA_TYPE__INTEGER:
        for i in range(itemsCount):
            items[i] = int(items[i])
    elif targetDataType == DATA_TYPE__FLOAT:
        for i in range(itemsCount):
            items[i] = strToFloat(items[i], comma_to_dots)
    elif targetDataType == DATA_TYPE__TIME:
        for i in range(itemsCount):
            items[i] = strToTime(items[i])
    elif targetDataType == DATA_TYPE__STRING:
        # для строк не планируется выполнять конвертацию, т.к. изначально данные записываются в виде строки,
        # но на всякий случай пусть будет заложена возможность конвертации
        for i in range(itemsCount):
            items[i] = str(items[i])



class _RT_NPContainer:

    def __init__(self) -> None:
        #self.name = name
        self.columns = []
        self.data = None
        self.used_rows_count = -1
        self.reserved_rows_count = -1
        self.OHE_when_matched = 1.0
        self.OHE_when_missed = 0.0
        self.checkPartsFunction = None

    """def _addColumn(self, kind, src_name, dst_name, advanced = None):
        columnDefinition = {
            "kind": kind,
            "src_name": src_name,
            "dst_name": dst_name,
            "src_number": None
        }
        if kind == NPCOLUMN_KIND__OHE:
            columnDefinition["values"] = advanced
        if kind == NPCOLUMN_KIND__MAPPING:
            columnDefinition["mappings"] = advanced
        self.columns.append(columnDefinition)"""

    """def _addNPColumn(self, container, kind, src_name, dst_name, advanced = None):
        if not container in self.NPs.keys():
            self.NPs[container] = {
                "columns": [],
                "NPData": None,
                "used_rows_count": -1,
                "reserved_rows_count": -1,
                "check_line": None,
                "check_parts": None
            }
        self.NPs[container]["columns"].append({
            "kind": kind,
            "src_name": src_name,
            "dst_name": dst_name,
            "src_number": None
        })
        n = len(self.NPs[container]["columns"]) - 1
        if kind == NPCOLUMN_KIND__OHE and advanced != None:
            self.NPs[container]["columns"][n]["values"] = advanced
        if kind == NPCOLUMN_KIND__MAPPING and advanced != None:
            self.NPs[container]["columns"][n]["mappings"] = advanced
    """ 

    def addColumn_Numeric(self, src_name, dst_name = ""):
        if dst_name == "":
            dst_name = src_name
        #self._addColumn(NPCOLUMN_KIND__SIMPLE, src_name, dst_name)
        self.columns.append({
            "kind": NPCOLUMN_KIND__SIMPLE,
            "src_name": src_name,
            "dst_name": dst_name,
            "src_number": None
        })

    def addColumn_OHE(self, src_name, dst_name, values):
        if dst_name == "":
            dst_name = src_name
        #self._addColumn(NPCOLUMN_KIND__OHE, src_name, dst_name, values)
        self.columns.append({
            "kind": NPCOLUMN_KIND__OHE,
            "src_name": src_name,
            "dst_name": dst_name,
            "src_number": None,
            "values": values
        })

    def addColumn_Mapping(self, src_name, dst_name, mappings, unmapped = 0.0):
        if dst_name == "":
            dst_name = src_name
        #self._addColumn(NPCOLUMN_KIND__MAPPING, src_name, dst_name, mappings)
        self.columns.append({
            "kind": NPCOLUMN_KIND__MAPPING,
            "src_name": src_name,
            "dst_name": dst_name,
            "src_number": None,
            "mappings": mappings,
            "unmapped": unmapped
        })

    # ----- Выделить память для numpy-массива (rows_count - количество строк) -----
    # ----- numpy-массив в неиницализированных элементах содержит нули (выделение памяти функцией np.zeros) -----
    def allocateMemory(self, rows_count, dtype=np.float64):
        self.reserved_rows_count = rows_count
        self.used_rows_count = 0
        columns_count = len(self.columns)
        self.data = np.zeros((rows_count, columns_count), dtype=dtype)

    # ----- Удалить неиспользованные столбцы numpy-массива -----
    def trimUnusedRows(self):
        columns_count = len(self.columns)
        self.data.resize((self.used_rows_count, columns_count), refcheck=False)

    # ----- Добавить строку в numpy-массив -----
    def addRow(self, parts, ignore_case = False, comma_to_dots = False):
        if self.used_rows_count == self.reserved_rows_count:
            # таблица заполнена полностью, увеличить количество строк в таблице
            self.reserved_rows_count = 1 + int(self.reserved_rows_count * 1.5)
            self.data.resize((self.reserved_rows_count, len(self.columns)), refcheck = False)
            #print("reserved_rows_count:", self.reserved_rows_count)
        i = self.used_rows_count
        for j in range(len(self.columns)):
            c = self.columns[j]
            s = parts[ c["src_number"] ]
            if c["kind"] == NPCOLUMN_KIND__SIMPLE:
                # +++ kind=simple - дробное число как есть (но, возможно, с заменой запятой на точку) +++
                if comma_to_dots:
                    s = s.replace(",", ".")
                self.data[i][j] = float(s)
            elif c["kind"] == NPCOLUMN_KIND__OHE:
                # +++ kind=OHE - только в одном из столбцов будет установлено значение +++
                if ignore_case:
                    s = s.lower()
                for possible_value in c["values"]:
                    if ignore_case:
                        possible_value = possible_value.lower()
                    if s == possible_value:
                        self.data[i][j] = self.OHE_when_matched
                    else:
                        self.data[i][j] = self.OHE_when_missed
            elif c["kind"] == NPCOLUMN_KIND__MAPPING:
                # +++ kind=mapping - заменить одно значение на другое (строку заменить на дробное число) +++
                found = False
                if ignore_case:
                    s = s.lower()
                    for key in c["mappings"].keys():
                        if s == key.lower():
                            self.data[i][j] = c["mappings"][key]
                            found = True
                            break
                else:
                    if s in c["mappings"]:
                        found = True
                        self.data[i][j] = c["mappings"][s]
                if not found and c["unmapped"] != None:
                    self.data[i][j] = c["unmapped"]
        self.used_rows_count += 1

    def dumpData(self, filename, delimiter, digits_after_dot = 8):
        with open(filename, "wt") as f:
            rows_count = len(self.data)
            columns_count = len(self.columns)
            f.write("SN")
            for j in range(columns_count):
                f.write(delimiter + self.columns[j]["dst_name"])
            f.write("\n")
            for i in range(rows_count):
                f.write(str(i) + ")")
                for j in range(columns_count):
                    f.write(delimiter + "{:.3f}" . format(self.data[i][j]))
                f.write("\n")

# --- end of class _RT_NPContainer ---

class _RT_AnalysisContainer:

    def __init__(self) -> None:
        self.columns = []
        self.data = {}
        self.histogramMaxCharsCount = 50 # сколько символов в длину строчка визуализирующая максимальное значение гистограммы
        self.histogramChar = "X"

    def addColumn(
        self,
        src_name,
        most_frequent_count = 10,
        procentiles = [0.1, 0.25, 0.5, 0.75, 0.9],
        histogramBarsCount = 11, # 0 - не строить гистограмму для этого столбца
    ):
        self.columns.append({
            "src_name": src_name,
            "src_number": None,
            "data_type": DATA_TYPE__STRING,
            "most_frequent_count": most_frequent_count,
            "procentiles": procentiles,
            "histogramBarsCount": histogramBarsCount,
            "stat": None # статистика ещё не подсчитывалась; будет создан OrderedDict со статистиками
        })
        self.data[src_name] = []

    # ----- Добавить строку данных для последующего анализа -----
    def addRow(self, parts):
        for c in self.columns:
            self.data[ c["src_name"] ].append( parts[ c["src_number"] ] )
            #columnName = c["src_name"]
            #columnNumber = c["src_number"]
            #self.data[columnName].append(parts[columnNumber])

    # ----- Произвести анализ прочитанных данных -----
    def Analyze(self, columns, comma_to_dots:bool):
        for c in self.columns:
            if len(columns) != 0:
                if c["src_name"] not in columns:
                    # указаны анализируемые столбцы и текущий столбец не присутствует в списке анализируемых - пропустить этот столбец
                    continue
            new_data_type = detectDataTypeForList(self.data[ c["src_name"] ], comma_to_dots)
            if new_data_type != c["data_type"]:
                c["data_type"] = new_data_type
                convertListToDataType(self.data[ c["src_name"] ], new_data_type, comma_to_dots)
            self.countStatistics(c, self.data[ c["src_name"] ])

    # ----- Подсчёт статистик соответствующих типу данных -----
    def countStatistics(self, c, items):
        #for c in self.items.keys():
        #for i in range(len(self.columns)):
        c["stat"] = OrderedDict()
        c["stat"]["count"] = len(items)
        if c["data_type"] == DATA_TYPE__INTEGER:
            calcNumericStatistics(   items, c["stat"])
            calcProcentiles(         items, c["stat"], c["procentiles"])
            calcEnumeratedStatistics(items, c["stat"], c["most_frequent_count"])
            if c["histogramBarsCount"] > 0:
                c["stat"]["histogram"]       = calcHistogram(items, c["histogramBarsCount"])
                c["stat"]["histogram_chars"] = charsHistogram(c["stat"]["histogram"], self.histogramMaxCharsCount, self.histogramChar)
        elif c["data_type"] == DATA_TYPE__FLOAT:
            calcNumericStatistics(   items, c["stat"])
            calcProcentiles(         items, c["stat"], c["procentiles"])
            if c["histogramBarsCount"] > 0:
                c["stat"]["histogram"]       = calcHistogram(items, c["histogramBarsCount"])
                c["stat"]["histogram_chars"] = charsHistogram(c["stat"]["histogram"], self.histogramMaxCharsCount, self.histogramChar)
        elif c["data_type"] == DATA_TYPE__TIME:
            c["stat"]["min"] = min(items)
            c["stat"]["max"] = max(items)
            calcProcentiles(         items, c["stat"], c["procentiles"])
            calcEnumeratedStatistics(items, c["stat"], c["most_frequent_count"])
            if c["histogramBarsCount"] > 0:
                c["stat"]["histogram"]       = calcHistogram(items, c["histogramBarsCount"])
                c["stat"]["histogram_chars"] = charsHistogram(c["stat"]["histogram"], self.histogramMaxCharsCount, self.histogramChar)
        elif c["data_type"] == DATA_TYPE__STRING:
            c["stat"]["longest"] = getLongestString(items)
            c["stat"]["longest_length"] = len(c["stat"]["longest"])
            calcEnumeratedStatistics(items, c["stat"], c["most_frequent_count"])


# --- end of class _RT_AnalysisContainer ---

class ReadTable:

    def __init__(self, delimiter = ",", comment = "#", ignore_case = False, comma_to_dots = False) -> None:
        self.delimiter = delimiter
        self.comment = comment
        self.ignore_case = ignore_case  # игнорировать регистр при сравнении строк
        self.comma_to_dots = comma_to_dots  # заменять запятые на точки (полезно при получении данных из экселя)
        self.NPs = {} # словарь, в котором ключ - имя (X, Y, XTtest, YTrain, ...; значение - объект класса _RT_NPContainer)
        self.A = _RT_AnalysisContainer()
        self.checkStringFunction = None
        self.checkPartsFunction = None
        self.ignore_wrong_columns = False # игнорировать ли строки, где неправильное количество столбцов или вызывать исключение
        self.default_np_datatype = np.float64
        self.default_np_rows_count = 1024
        #self.A = {
        #    "columns": [],
        #    "items": {}        
        #}
        #self.items = {}
        #self.AnalyzeColumns = {}
        #self.AnalyzeItems = {}

    def addNPContainer(self, name):
        if not name in self.NPs:
            self.NPs[name] = _RT_NPContainer()

    def copyColumns(self, src_name, dst_name):
        if not src_name in self.NPs:
            msg = "Cannot find source NP-container [{}]" . format(src_name)
            raise Exception(msg)
        if not dst_name in self.NPs:
            self.NPs[dst_name] = _RT_NPContainer()
            #for c in self.NPs[src_name].columns:
        self.NPs[dst_name].columns = self.NPs[src_name].columns.copy()
        #pprint(self.NPs[dst_name].columns)

    def getContainersList(self):
        return self.NPs.keys()

    def printAnalyzedColumns(self):
        for key in self.A.keys():
            print("-------------- " + key + " (" + self.A[key]["data_type"] + ")" + "----------------")
            pprint(self.A[key]["stat"])
            print("-------------------------------------------")

    def resetSrcNumbers(self, columns):
        for c in columns:
            c["src_number"] = -1

    def setSrcNumbers(self, columns):
        for c in columns:
            src_name = c["src_name"]
            if self.ignore_case:
                src_name = src_name.lower()
            for j in range(len(self.header)):
                h = self.header[j]
                if self.ignore_case:
                    h = h.lower()
                if src_name == h:
                    c["src_number"] = j
                    break
        # проверить, что для всех столбцов определён номер столбца в исходном файле
        for c in columns:
            if c["src_number"] < 0:
                msg = "Cannot find column [{}]." . format(c["src_name"])
                raise Exception(msg)


    def read(
        self,
        filename,
        header_only = False,
        analyze_all_columns = False,
        encoding = "utf-8"
    ):
        self.header = []
        for key in self.NPs.keys():
            self.resetSrcNumbers(self.NPs[key].columns)
            if self.NPs[key].data == None:
                # память для numpy-массива ещё не выделялась
                self.NPs[key].allocateMemory(self.default_np_rows_count, dtype=self.default_np_datatype)
        self.resetSrcNumbers(self.A.columns)
        raw_line_number = 0
        with open(filename, "rt", encoding=encoding) as f:
            for s_raw in f:
                raw_line_number += 1
                #s_raw = s_raw.rstrip() # удалить перевод строки (\r, \n)
                while len(s_raw) > 0 and s_raw[-1] in ["\r", "\n"]:
                    # удалить переводы строк
                    s_raw = s_raw[0:len(s_raw)-1]
                s = remove_comment(s_raw, self.comment)
                if self.checkStringFunction != None:
                    # указана пользовательская функция для предварительной обработки строки из файла
                    s = self.checkStringFunction(s)
                if len(s) == 0:
                    continue
                parts = s.split(self.delimiter)
                if self.checkPartsFunction != None:
                    # указана пользовательская функция для предварительной обработки поделённой на элементы строки из файла
                    self.checkPartsFunction(parts)
                if len(parts) == 0:
                    continue

                #print(raw_line_number, s, "\t|||\t", parts)
                if len(self.header) == 0:
                    # +++ читается заголовок +++
                    self.header = parts.copy()
                    #print("H:", self.header)
                    if header_only:
                        return
                    for key in self.NPs.keys():
                        self.setSrcNumbers(self.NPs[key].columns)
                    if len(self.A.columns) == 0 and analyze_all_columns:
                        for h in self.header:
                            self.A.addColumn(h)
                    self.setSrcNumbers(self.A.columns)
                    continue
                # +++ читается строка с данными +++
                if len(parts) != len(self.header):
                    if self.ignore_wrong_columns:
                        # пропускать строки с неправильным количеством столбцов
                        continue
                    else:
                        # строки с неправильным количеством столбцов генерируют ошибку
                        msg = "Wrong columns count ({}) for line #{} [{}]" . format(len(parts), raw_line_number, s_raw)
                        raise Exception(msg)
                for key in self.NPs.keys():
                    if self.NPs[key].checkPartsFunction == None:
                        # не указаа функция трансформации поделённой на элементы строки
                        self.NPs[key].addRow(parts, self.ignore_case, self.comma_to_dots)
                    else:
                        # выполнить трансформацию для массива элементов, если массив останется не пустым, тогда добавлять в текущий numpy-массив
                        parts_cp = parts.copy()
                        self.NPs[key].checkPartsFunction(parts_cp)
                        if len(parts_cp) > 0:
                            self.NPs[key].addRow(parts_cp, self.ignore_case, self.comma_to_dots)
                if len(self.A.columns) > 0:
                    self.A.addRow(parts)

        for key in self.NPs.keys():
            self.NPs[key].trimUnusedRows()
    # --- end of read-function ---
            
    def Analyze(self, columns = []):
        self.A.Analyze(columns, self.comma_to_dots)
                    

# --- end of class ReadTable ---

"""s1 = "  abc 123  "
s2 = s1.rstrip()
print("[{}]" . format(s2))
exit(0  )"""

def checkString1(s:str) -> str:
    seek_str = "2022,11,"
    replace_to = "2010-11-"
    p1 = s.find(seek_str)
    if p1 >= 0:
        p2 = p1 + len(seek_str)
        s1 = s[0:p1]
        s2 = s[p2:len(s)]
        s = s1 + replace_to + s2
    return s

# ----- На основе года определить, являются ли данные для обучения или для проверки -----
def isTestData(s:str) -> bool:
    return s[0:4] == "2024"

#print(isTestData("2022.01")); print(isTestData("2023.01")); print(isTestData("2024.01")); print(isTestData("2025.01")); exit(0)

# ----- Оставить в массиве данные, если в нём данные для обучения -----
def checkParts_Train(parts):
    forTesting = isTestData(parts[3])
    if forTesting:
        parts.clear()
    else:
        pass

# ----- Оставить в массиве данные, если в нём данные для проверки -----
def checkParts_Test(parts):
    forTesting = isTestData(parts[3])
    if forTesting:
        pass
    else:
        parts.clear()


#s1 = "qqw2022,11,31abc"
#s2 = checkString1(s1)
#print(s2)
#exit(0)

def real1():
    filename = "C:\\Users\\masha\\AppData\\Roaming\\MetaQuotes\\Terminal\\9EB2973C469D24060397BB5158EA73A5\\MQL5\\Files\\NNExport1_H1_incr=1x24x5_smth=3x1(5).xls"
    rt = ReadTable("\t", ";")
    rt.read(filename, encoding="cp1251", analyze_all_columns=True)
    rt.Analyze()
    print("--- A ---")
    pprint(rt.A.columns)
    print("--- end of A ---")
    exit(0)

def real2():
    filename = "C:\\Users\\masha\\AppData\\Roaming\\MetaQuotes\\Terminal\\9EB2973C469D24060397BB5158EA73A5\\MQL5\\Files\\NNExport1_H1_incr=1x24x5_smth=3x1(5).xls"
    rt = ReadTable("\t", ";")
    rt.addNPContainer("X")

    rt.NPs["X"].addColumn_Numeric("Small#1")
    rt.NPs["X"].addColumn_Numeric("Small#2")
    rt.NPs["X"].addColumn_Numeric("Small#3")
    rt.NPs["X"].addColumn_Numeric("Small#5")
    rt.NPs["X"].addColumn_Numeric("Small#8")
    rt.NPs["X"].addColumn_Numeric("Small#13")
    rt.NPs["X"].addColumn_Numeric("Small#21")
    rt.NPs["X"].addColumn_Numeric("Small#34")
    rt.NPs["X"].addColumn_Numeric("Small#55")
    rt.NPs["X"].addColumn_Numeric("Small#89")
    rt.NPs["X"].addColumn_Numeric("Small#144")
    
    rt.NPs["X"].addColumn_Numeric("Main#1")
    rt.NPs["X"].addColumn_Numeric("Main#2")
    rt.NPs["X"].addColumn_Numeric("Main#3")
    rt.NPs["X"].addColumn_Numeric("Main#5")
    rt.NPs["X"].addColumn_Numeric("Main#8")
    rt.NPs["X"].addColumn_Numeric("Main#13")
    rt.NPs["X"].addColumn_Numeric("Main#21")
    rt.NPs["X"].addColumn_Numeric("Main#34")
    rt.NPs["X"].addColumn_Numeric("Main#55")
    rt.NPs["X"].addColumn_Numeric("Main#89")
    rt.NPs["X"].addColumn_Numeric("Main#144")
    
    rt.NPs["X"].addColumn_Numeric("Big#1")
    rt.NPs["X"].addColumn_Numeric("Big#2")
    rt.NPs["X"].addColumn_Numeric("Big#3")
    rt.NPs["X"].addColumn_Numeric("Big#5")
    rt.NPs["X"].addColumn_Numeric("Big#8")
    rt.NPs["X"].addColumn_Numeric("Big#13")
    rt.NPs["X"].addColumn_Numeric("Big#21")
    rt.NPs["X"].addColumn_Numeric("Big#34")
    rt.NPs["X"].addColumn_Numeric("Big#55")
    rt.NPs["X"].addColumn_Numeric("Big#89")
    rt.NPs["X"].addColumn_Numeric("Big#144")

    rt.read(filename, encoding="cp1251", analyze_all_columns=True)
    pprint(rt.NPs["X"].data)
    exit(0)

def real3(filename = "C:\\Users\\masha\\AppData\\Roaming\\MetaQuotes\\Terminal\\9EB2973C469D24060397BB5158EA73A5\\MQL5\\Files\\NNExport1_H1_1x3-24x2-5x1-1_AUDCAD.xls"):
    rt = ReadTable("\t", ";", comma_to_dots=True)
    #rt.checkStringFunction = checkString1
    # +++ X +++
    rt.addNPContainer("X_train")

    rt.NPs["X_train"].addColumn_Numeric("Small#1")
    rt.NPs["X_train"].addColumn_Numeric("Small#2")
    rt.NPs["X_train"].addColumn_Numeric("Small#3")
    rt.NPs["X_train"].addColumn_Numeric("Small#5")
    rt.NPs["X_train"].addColumn_Numeric("Small#8")
    rt.NPs["X_train"].addColumn_Numeric("Small#13")
    rt.NPs["X_train"].addColumn_Numeric("Small#21")
    rt.NPs["X_train"].addColumn_Numeric("Small#34")
    rt.NPs["X_train"].addColumn_Numeric("Small#55")
    rt.NPs["X_train"].addColumn_Numeric("Small#89")
    rt.NPs["X_train"].addColumn_Numeric("Small#144")
    
    rt.NPs["X_train"].addColumn_Numeric("Main#1")
    rt.NPs["X_train"].addColumn_Numeric("Main#2")
    rt.NPs["X_train"].addColumn_Numeric("Main#3")
    rt.NPs["X_train"].addColumn_Numeric("Main#5")
    rt.NPs["X_train"].addColumn_Numeric("Main#8")
    rt.NPs["X_train"].addColumn_Numeric("Main#13")
    rt.NPs["X_train"].addColumn_Numeric("Main#21")
    rt.NPs["X_train"].addColumn_Numeric("Main#34")
    rt.NPs["X_train"].addColumn_Numeric("Main#55")
    rt.NPs["X_train"].addColumn_Numeric("Main#89")
    rt.NPs["X_train"].addColumn_Numeric("Main#144")
    
    rt.NPs["X_train"].addColumn_Numeric("Big#1")
    rt.NPs["X_train"].addColumn_Numeric("Big#2")
    rt.NPs["X_train"].addColumn_Numeric("Big#3")
    rt.NPs["X_train"].addColumn_Numeric("Big#5")
    rt.NPs["X_train"].addColumn_Numeric("Big#8")
    rt.NPs["X_train"].addColumn_Numeric("Big#13")
    rt.NPs["X_train"].addColumn_Numeric("Big#21")
    rt.NPs["X_train"].addColumn_Numeric("Big#34")
    rt.NPs["X_train"].addColumn_Numeric("Big#55")
    rt.NPs["X_train"].addColumn_Numeric("Big#89")
    rt.NPs["X_train"].addColumn_Numeric("Big#144")

    rt.copyColumns("X_train", "X_test")
    rt.NPs["X_train"].checkPartsFunction = checkParts_Train
    rt.NPs["X_test"].checkPartsFunction = checkParts_Test

    # +++ Y +++
    rt.addNPContainer("Y_train")
    rt.NPs["Y_train"].addColumn_OHE("TrendSign", "TrendUp", ["BUY"])
    rt.NPs["Y_train"].addColumn_OHE("TrendSign", "TrendFlat", ["NONE"])
    rt.NPs["Y_train"].addColumn_OHE("TrendSign", "TrendDown", ["SELL"])
    rt.copyColumns("Y_train", "Y_test")
    rt.NPs["Y_train"].checkPartsFunction = checkParts_Train
    rt.NPs["Y_test"].checkPartsFunction = checkParts_Test

    #rt.read(filename, analyze_all_columns=True); rt.Analyze(); pprint(rt.A.columns)
    rt.read(filename)
    #rt.NPs["Y_train"].dumpData("c:\\python\\y_train.tsv", "\t")
    #rt.NPs["Y_test"].dumpData("c:\\python\\y_test.tsv", "\t")

    # +++ sklearn +++
    from sklearn.neural_network import MLPClassifier
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split

    X_train = rt.NPs["X_train"].data
    Y_train = rt.NPs["Y_train"].data
    X_test = rt.NPs["X_test"].data
    Y_test = rt.NPs["Y_test"].data
    #X, y = make_classification(n_samples=100, random_state=1)
    #X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=1)

    # activation{‘identity’, ‘logistic’, ‘tanh’, ‘relu’}, default=’relu’
    # solver{‘lbfgs’, ‘sgd’, ‘adam’}, default=’adam’
    clf = MLPClassifier(
        hidden_layer_sizes = (50, ),
        random_state = 1,
        max_iter = 5000,
        activation = "tanh",
        solver = "adam",
        verbose = True
    )
    clf.fit(X_train, Y_train)

    r1 = clf.predict_proba(X_test)
    print(r1)

    r2 = clf.predict(X_test)
    print(r2)
    
    r3 = clf.score(X_test, Y_test)
    print(r3)
    #clf.predict_proba(X_test[:1])
    #clf.predict(X_test[:5, :])
    #array([1, 0, 1, 0, 1])
    #clf.score(X_test, y_test)
    #0.8...

    import pickle
    p = open("c:\\python\\1.pickle", "wb")
    pickle.dump(clf, p)
    p.close()
    # save the model 
    #filename = 'linear_model.sav'
    #pickle.dump(regressor, open(filename, 'wb')) 

    exit(0)

def use1():
    import pickle
    #p = open("c:\\python\\1.pickle", "rb")
    # load the model 
    filename = "c:\\python\\1.pickle"
    load_model = pickle.load(open(filename, 'rb'))

    y_pred = load_model.predict(X_test) 
    print('root mean squared error : ', np.sqrt( metrics.mean_squared_error(y_test, y_pred)))
    
if __name__ == "__main__":
    #real1()
    #real2()
    real3()
    rt = ReadTable("\t", ";", True)

    print("--- X ---")
    rt.addNPContainer("X")
    rt.NPs["X"].addColumn_Numeric("PClose", "ClsPrc")
    rt.NPs["X"].addColumn_Numeric("Stoch:13x5x3", "Stoch")
    rt.NPs["X"].addColumn_Mapping("dow", "dowNumb", {
        "mon": 1,
        "tue": 2,
        "web": 3,
        "thu": 4,
        "fri": 5,
        "sat": 6,
        "sun": 7
    })
    pprint(rt.NPs["X"].columns)

    print("--- Y ---")
    rt.addNPContainer("Y")
    rt.NPs["Y"].addColumn_OHE("Trend", "TrendUp", ["+1", "buy", "up"])
    rt.NPs["Y"].addColumn_OHE("Trend", "TrendFlat", ["0", "flat"])
    rt.NPs["Y"].addColumn_OHE("Trend", "TrendDown", ["-1", "sell", "down"])
    pprint(rt.NPs["Y"].columns)

    #print("--- A ---")
    #rt.A.addColumn("POpen")
    #rt.A.addColumn("PClose", procentiles=[])
    #pprint(rt.A.columns)

    rt.read("file1.txt", encoding="iso8859", analyze_all_columns=True)

    print("--- XData ---")
    pprint(rt.NPs["X"].data)

    print("--- AData ---")
    pprint(rt.A.data)

    rt.Analyze()
    print("--- A ---")
    pprint(rt.A.columns)
    print("--- end of A ---")

    exit(0)

    rt.addNPColumn_Numeric("X", "POpen", "POpen")
    rt.addNPColumn_Numeric("X", "PClose", "PClose")
    rt.addNPColumn_Mapping("X", "dow", "dowNumb", {
        "mon": 1,
        "tue": 2,
        "web": 3,
        "thu": 4,
        "fri": 5,
        "sat": 6,
        "sun": 7
    })

    rt.addNPColumn_OHE("Y", "Trend", "TrendUp", ["+1", "buy", "up"])
    rt.addNPColumn_OHE("Y", "Trend", "TrendFlat", ["0", "flat"])
    rt.addNPColumn_OHE("Y", "Trend", "TrendDown", ["-1", "sell", "down"])

    rt.analyzeColumn("POpen")
    rt.analyzeColumn("PClose")

    rt.read("file1.txt")

    print("--- XColumns: ---")
    #pprint(rt.NPs["X"].columns)
    pprint(rt.NPs["X"]["columns"])
    print("--- YColumns: ---")
    #pprint(rt.NPs["Y"].columns)
    pprint(rt.NPs["Y"]["columns"])
    print("--- AColumns: ---")
    pprint(rt.A)
    #rt.printAnalyzedColumns()
