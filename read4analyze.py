#!/usr/bin/python3

from collections import OrderedDict
import statistics
import util

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
            "data_type": util.DATA_TYPE__STRING,
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
        if c["data_type"] == util.DATA_TYPE__INTEGER:
            calcNumericStatistics(   items, c["stat"])
            calcProcentiles(         items, c["stat"], c["procentiles"])
            calcEnumeratedStatistics(items, c["stat"], c["most_frequent_count"])
            if c["histogramBarsCount"] > 0:
                c["stat"]["histogram"]       = calcHistogram(items, c["histogramBarsCount"])
                c["stat"]["histogram_chars"] = charsHistogram(c["stat"]["histogram"], self.histogramMaxCharsCount, self.histogramChar)
        elif c["data_type"] == util.DATA_TYPE__FLOAT:
            calcNumericStatistics(   items, c["stat"])
            calcProcentiles(         items, c["stat"], c["procentiles"])
            if c["histogramBarsCount"] > 0:
                c["stat"]["histogram"]       = calcHistogram(items, c["histogramBarsCount"])
                c["stat"]["histogram_chars"] = charsHistogram(c["stat"]["histogram"], self.histogramMaxCharsCount, self.histogramChar)
        elif c["data_type"] == util.DATA_TYPE__DATE_TIME:
            c["stat"]["min"] = min(items)
            c["stat"]["max"] = max(items)
            calcProcentiles(         items, c["stat"], c["procentiles"])
            calcEnumeratedStatistics(items, c["stat"], c["most_frequent_count"])
            if c["histogramBarsCount"] > 0:
                c["stat"]["histogram"]       = calcHistogram(items, c["histogramBarsCount"])
                c["stat"]["histogram_chars"] = charsHistogram(c["stat"]["histogram"], self.histogramMaxCharsCount, self.histogramChar)
        elif c["data_type"] == util.DATA_TYPE__STRING:
            c["stat"]["longest"] = util.get_the_longest_string(items)
            c["stat"]["longest_length"] = len(c["stat"]["longest"])
            calcEnumeratedStatistics(items, c["stat"], c["most_frequent_count"])

# --- end of class _RT_AnalysisContainer ---

