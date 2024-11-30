#!/usr/bin/python3

from pprint import pprint
from collections import OrderedDict
import datetime
import numpy as np
import statistics
import util


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
            items[i] = util.str_to_float(items[i], comma_to_dots)
    elif targetDataType == DATA_TYPE__TIME:
        for i in range(itemsCount):
            items[i] = util.str_to_float(items[i])
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
            c["stat"]["longest"] = util.get_the_longest_string(items)
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
                s = util.remove_comment(s_raw, self.comment)
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

