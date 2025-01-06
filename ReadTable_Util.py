#!/usr/bin/python3

import datetime

DATA_TYPE__INTEGER = "i"
DATA_TYPE__FLOAT = "f"
DATA_TYPE__DATE_TIME = "t"
DATA_TYPE__BOOLEAN = "b"
DATA_TYPE__STRING = "s"
DATA_TYPE__UNKNOWN = "?"
DATA_TYPE__AUTO = "a"

TRUE_VALUES  = ["+", "yes", "true",  "on" ] # строковые значения должны быть в нижнем регистре, проверяемая строка переводится в нижний регистр
FALSE_VALUES = ["-", "no",  "false", "off"] # строковые значения должны быть в нижнем регистре, проверяемая строка переводится в нижний регистр

TRANSFORM__TO_UPPER_CASE = "ToUpperCase"
TRANSFORM__TO_LOWER_CASE = "ToLowerCase"
TRANSFORM__STRIP_SPACES = "StripSpaces"
TRANSFORM__STRIP_QUOTES = "StripQuotes"
TRANSFORM__COMMA_TO_DOTS = "CommaToDots"
TRANSFORM__REPLACE = "Replace"
TRANSFORM__FROM_AMERICAN_DATES_TO_TRADITIONAL = "FromAmericanDatesToTraditional" # mm.dd.yyyy => dd.mm.yyyy
TRANSFORM__FROM_AMERICAN_DATES_TO_ISO = "FromAmericanDatesToISO" # mm.dd.yyyy => yyyy-mm-dd
TRANSFORM__FUNCTION = "function" # обработать строку пользовательской функцией

COLUMN_KIND__SIMPLE = "simple"          # оставить число как есть
COLUMN_KIND__ONE_HOT_ENCODING = "ohe"   # One Hot Encoding
#COLUMN_KIND__MAPPING = "mapping"        # указаны строки и на какое число их заменить      использовать transformations[]
#COLUMN_KIND__LABEL_ENCODING = "label"

ACTION__ACCEPT = "accept"
ACTION__IGNORE = "ignore"


# ----- Конвертировать категориальный список в список целых или дробных значений -----
# (каждое исходное значение заменяется на некоторое число в диапазоне [start_label .. stop_label] 
# или начиная со start_label с шагом increment )
def convert_to_label_encoding(items, start_label = 0, stop_label = None, increment = None):
    items_uniq_sorted = sorted(list(set(items)))
    if type(start_label) == type(123):
        # целочисленные метки классов
        if increment == None:
            increment = 1        
    elif type(start_label) == type(123.456):
        # дробные метки классов
        if type(stop_label) == type(123.456):
            # указаны границы дробных значений в которые поместить метки классов
            # 2.0  5.0  8.0  11.0  14.0   N=5  increment=(14-2)/(5-1)=12/4=3
            fltN = float(len(items_uniq_sorted))
            increment = (stop_label - start_label) / (fltN - 1.0)
        else:
            # максимальное значение не указано - увеличивать значения с шагом increment
            if increment == None:
                increment = 1.0
    else:
        msg = "Type of start label neither int no float: " + str(type(start_label))
        raise Exception(msg)
    current_label = start_label
    mappings = {}
    for x in items_uniq_sorted:
        mappings[x] = current_label
        current_label += increment
    #print(mappings)
    items_labeled = []
    for x in items:
        items_labeled.append(mappings[x])
    return items_labeled

"""
X = [5,8,32,-1,12,4,12,-3,11,13,12,6,7,24,-3, 9,-7]
X = sorted(X)
Y = convert_to_label_encoding(X, -1.0, 2.0)
print("src:", type(X), X)
print("labeled:", type(Y), Y)
print("labels:", sorted(list(set(Y))))
exit(0)
"""

"""
def build_transformation(kind, seek = None, replace_to = None):
    one_transformation = {
        "kind": kind
    }
    if kind == TRANSFORM__REPLACE:
        one_transformation["seek"] = seek
        one_transformation["replace_to"] = replace_to
    return one_transformation
"""

def add_transformation(transformations, kind, param1 = None, param2 = None) -> None:
    if kind == TRANSFORM__REPLACE:
        transformations.append({
            "kind": TRANSFORM__REPLACE,
            "seek": param1,
            "replace_to": param2
        })
    elif kind == TRANSFORM__FUNCTION:
        transformations.append({
            "kind": TRANSFORM__FUNCTION,
            "function": param1
        })
    else:
        transformations.append(kind)


# ----- Из американского формата даты, где сначала идёт месяц потом день перевести в нормальный (dd.mm.yyyy) или в iso-формат (yyyy-mm-dd) -----
def from_american_date(s, to_traditional = True):
    # mm.dd.yyyy
    # 0123456789
    if len(s) < 10:
        # недостаточно символов, чтобы быть датой в формае mm.dd.yyyy
        return s
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
    ):
        month = s[0:2]
        day = s[3:5]
        year = s[6:10]
        other = s[10:len(s)]
        if to_traditional:
            s = day + "." + month + "." + year + other
        else:
            s = year + "-" + month + "-" + day + other
    return s

#s1 = "12.31.2024"; s2 = from_american_date(s1, True); print(s2); exit(0)   
#s1 = "12.31.2024"; s2 = from_american_date(s1, False); print(s2); exit(0)

# ----- Применить к строке трансформации -----
def apply_transformations(s:str, transformations) -> str:
    for tr in transformations:
        if type(tr) == type("abc"):
            # трансформация, которая либо включена, либо отключена
            if tr == TRANSFORM__COMMA_TO_DOTS:
                s = s.replace(",", ".")
            elif tr == TRANSFORM__STRIP_SPACES:
                s = s.strip()
            elif tr == TRANSFORM__STRIP_QUOTES:
                if len(s) > 0 and s[0] in ['"', "'"]:
                    s = s[1:len(s)]
                if len(s) > 0 and s[-1] in ['"', "'"]:
                    s = s[0:len(s)-1]
            elif tr == TRANSFORM__TO_UPPER_CASE:
                s = s.upper()
            elif tr == TRANSFORM__TO_LOWER_CASE:
                s = s.lower()
            elif tr == TRANSFORM__FROM_AMERICAN_DATES_TO_TRADITIONAL:
                s = from_american_date(s, True)
            elif tr == TRANSFORM__FROM_AMERICAN_DATES_TO_ISO:
                s = from_american_date(s, False)
        elif type(tr) == type({}):
            # трансформация, которая задана в виде словаря
            if tr["kind"] == TRANSFORM__REPLACE:
                s = s.replace(tr["seek"], tr["replace_to"])
            elif tr["kind"] == TRANSFORM__FUNCTION:
                s = tr["function"](s)
    return s


# ----- удалить однострочный комментарий -----
def remove_comment(s:str, comment_sequence:str) -> str:
    p = s.find(comment_sequence)
    if p >= 0:
        s = s[0:p]
    s = s.strip()
    return s


"""
def get_columns_numbers(columns, header, ignore_case:bool = False):
    columns_numbers = []
    if len(columns) == 0:
        # если не указаны столбцы - прочитать все столбцы файла
        columns_numbers = [j for j in range(len(header))]
        return columns_numbers
    for c in columns:
        found = False
        if type(c) == type(123):
            # вместо имени столбца указан его номер
            if c < 0:
                # указан номер столбца с конца (-1=последний столбец, -2=предпоследний столбец и т.д.)
                c = len(header) + c
            columns_numbers.append(c)
            found = True
        elif type(c) == type("abc"):
            # указано имя столбца из файла
            for j in range(len(header)):
                if ignore_case:
                    if c.lower() == header[j].lower():
                        columns_numbers.append(j)
                        found = True
                        break
                else:
                    if c == header[j]:
                        columns_numbers.append(j)
                        found = True
                        break
        if not found:
            msg = 'Cannot find column "{}" in [{}]' . format(c, ", ".join(header))
            raise Exception(msg)
    return columns_numbers
"""

# ----- Дату/время привести к дробному значению в интервале -----
def date_to_float(cur_date, min_date, max_date, min_float, max_float):
    min_max_dates_interval_seconds = (max_date - min_date).total_seconds()
    min_cur_dates_interval_seconds = (cur_date - min_date).total_seconds()
    x = min_cur_dates_interval_seconds / min_max_dates_interval_seconds
    floats_distance = max_float - min_float
    y = x * floats_distance + min_float
    return y


# ----- Попытаться преобразовать строку в логическому значению (когда ни одно из значений не подходит - None) ---
def str_to_boolean(s):
    s_lower = s.lower()
    if s_lower in TRUE_VALUES:
        return True
    if s_lower in FALSE_VALUES:
        return False
    return None

def str_to_int(s):
    try:
        x = int(s)
    except:
        return None
    return x

def str_to_float(s):
    try:
        x = float(s)
    except:
        return None
    return x

def str_to_date_time(s):
    result = None
    dtp = str_to_date_time_parts(s)
    if dtp:
        result = datetime.datetime(
            dtp["year"],
            dtp["month"],
            dtp["day"],
            dtp["hour"],
            dtp["minute"],
            dtp["second"],
            dtp["micros"]
        )
    return result

# ----- Разобрать строку с датой на компоненты даты и вернуть их в виде массива -----
def str_to_date_time_parts(s, american_format = False):
    if len(s) < 10:
        # слишком мало символов, чтобы быть датой
        return False
    
    year, month, day = None, None, None

    # dd.mm.yyyy
    # 0123456789
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
    ):
        # формат nn?nn?nnnn соблюдён
        if american_format:
            month = s[0:2]
            day = s[3:5]
            year = s[6:10]
        else:
            day = s[0:2]
            month = s[3:5]
            year = s[6:10]
        try:
            d = datetime.datetime(int(year), int(month), int(day))
        except:
            # не удалось конвертировать в дату
            year, month, day = None, None, None
    # yyyy-mm-dd
    # 0123456789
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
    ):
        # формат nnnn?nn?nn соблюдён
        year = s[0:4]
        month = s[5:7]
        day = s[8:10]
        try:
            d = datetime.datetime(int(year), int(month), int(day))
        except:
            # не удалось конвертировать в дату
            year, month, day = None, None, None
    
    if year == None or month == None or day == None:
        # не удалось выделить год/месяц/день
        return False
    
    try:
        year = int(year)
    except:
        return False
    try:
        month = int(month)
    except:
        return False
    try:
        day = int(day)
    except:
        return False
    
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
            return False
        if hour < 0 or hour > 23:
            return False
    if len(s) >= 16:
        try:
            minute = int(s[14:16])
        except:
            return False
        if minute < 0 or minute > 59:
            return False
    if len(s) >= 19:
        try:
            second = int(s[17:19])
        except:
            return False
        if second < 0 or second > 59:
            return False
        
    # dd.mm.yyyy hh:mm:ss.micros
    # 01234567890123456789012345
    if len(s) >= 21 and not s[19].isdigit() and s[20].isdigit():
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
            return False
        if micros < 0:
            return False

    try:
        d = datetime.datetime(year, month, day, hour, minute, second, micros)
    except:
        return False

    
    date_time_parts = {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second,
        "micros": micros
    }
    return date_time_parts


# ----- Извлечь вектор-столбец из двумерного массива -----
def extract_column_from_matrix(matrix, column_number):
    result = []
    for i in range(len(T)):
        result.append(matrix[i][column_number])
    return result


# ----- Обновить в двумерном массиве значения столбца -----
def update_column_in_matrix(matrix, column_number, vector):
    for i in range(len(vector)):
        matrix[i][column_number] = vector[i]


# ----- Подсчитать сколько раз повторяется каждое значение в массиве -----
# Вернуть двумерный массив, в котором первое измерение - значение из переданного исходного массива,
# второе измерение - сколько раз это значение встречается в исходном массиве
# Возможно, ограничение по количеству элементов словаря, чтобы возвращать наиболее частые значения при most_frequent == True
# или наиболее редкие значения при most_frequent == Fase
def get_frequencies(items, return_count = 0, most_frequent = True):
    freqs_dict = {}
    for x in items:
        if x not in freqs_dict:
            freqs_dict[x] = 1
        else:
            freqs_dict[x] += 1
    freqs_list = []
    for key in freqs_dict.keys():
        freqs_list.append([key, freqs_dict[key]])
    freqs_list.sort(key = lambda x:x[1], reverse = most_frequent)
    if return_count > 0:
        tmp = []
        for row in freqs_list:
            if len(tmp) < return_count:
                tmp.append(row)
        freqs_list = tmp.copy()
    return freqs_list


#print(datetime.datetime.now()); exit(0)

if __name__ == "__main__":
    from pprint import pprint
    #print(str_to_boolean("nOo"))
    #dparts = str_to_date_time_parts("03.09.2024 17:07:59.0012"); pprint(dparts)
    #items = "edceadebcedbecde"; freqs = get_frequencies(items, 3); pprint(freqs)
    x = date_to_float(
        datetime.datetime.now(),
        #datetime.datetime(2024, 12, 31, 23, 50, 10),
        #datetime.datetime(1970, 1, 1),
        datetime.datetime(2024, 1, 1),
        datetime.datetime(2024, 12, 31, 23, 59, 59),
        1,
        366
    )
    print(x)