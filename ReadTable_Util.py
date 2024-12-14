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
TRANSFORM__COMMA_TO_DOTS = "CommaToDots"
TRANSFORM__FROM_AMERICAN_DATES_TO_NORMAL = "FromAmericanDatesToNormal" # mm.dd.yyyy => dd.mm.yyyy
TRANSFORM__FROM_AMERICAN_DATES_TO_ISO = "FromAmericanDatesToISO" # mm.dd.yyyy => yyyy-mm-dd


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
    items = "edceadebcedbecde"; freqs = get_frequencies(items, 3); pprint(freqs)
