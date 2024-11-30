#!/usr/bin/python3

import datetime


DATA_TYPE__INTEGER = "i"
DATA_TYPE__FLOAT = "f"
DATA_TYPE__DATE_TIME = "t"
DATA_TYPE__BOOLEAN = "b"
DATA_TYPE__STRING = "s"
DATA_TYPE__UNKNOWN = "?"

TRUE_VALUES  = ["1", "+", "yes", "true", "on"]
FALSE_VALUES = ["0", "-", "no",  "false", "off"]

# ----- удалить комментарий -----
def remove_comment(s, comment_sequence):
    p = s.find(comment_sequence)
    if p >= 0:
        s = s[0:p]
    s = s.strip()
    return s

# ----- Попытаться преобразовать строку к дробному числу (при ошибке - None) -----
# ----- comma_to_dots: когда True - заменить запятую на точку перед конвертацией -----
def str_to_float(s, comma_to_dots = False):
    if comma_to_dots:
        s = s.replace(",", ".")
    result = None
    try:
        result = float(s)
    except:
        result = None
    return result


# ----- Попытаться преобразовать строку в логическому значению (когда ни одно из значений не подходит - None) ---
def str_to_boolean(s):
    s = s.lower()
    if s in TRUE_VALUES:
        return True
    if s in FALSE_VALUES:
        return False
    return None


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

# ----- Получить самую длинную строку в массиве -----
def get_the_longest_string(items) -> str:
    the_longest_string = items[0]
    max_len = len(the_longest_string)
    for s in items:
        if len(s) > max_len:
            the_longest_string = s
            max_len = len(the_longest_string)
    return the_longest_string

#X = ["qq", "www", "12345", "eee", "4567"]
#print(get_the_longest_string(X))
#exit(0)

# ------- Попытаться преобразовать строку в дату/время; вернуть дату или None, если конвертирование не удалось -------
def str_to_time(s):
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
        # не подходит ни один из форматов даты: dd.mm.yyyy yyyy-mm-dd
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
def detect_data_type_for_string(s:str, comma_to_dots:bool) -> str:
    # является ди переданная строка логическим значением
    x = str_to_boolean(s)
    if x != None:
        return DATA_TYPE__BOOLEAN

    # является ди переданная строка целым числом
    try:
        x = int(s)
        return DATA_TYPE__INTEGER
    except:
        pass

    # является ди переданная строка дробным числом (возможно, запятая вместо точки)
    x = str_to_float(s, comma_to_dots)
    if x != None:
        return DATA_TYPE__FLOAT

    # является ди переданная строка датой/временем в форматах dd.mm.yyyy hh:mm:ss или yyyy-mm-dd hh:mm:ss
    x = str_to_time(s)
    if x != None:
        return DATA_TYPE__DATE_TIME
    
    # оставить переданный параметр строкой
    return DATA_TYPE__STRING


def detect_data_type(data, column_name_or_number = None, comma_to_dots = False):
    # входные данные могут быть:
    #  * одномерный массив
    #  * двумерный массив, в котором каждый элемент - строка, в этом случае требуется указания номера анализируемого столбца
    #  * словарь, в котором значения ключей - одномерные массивы, в этом случае требуется указания имени анализируемого столбца

    result = DATA_TYPE__UNKNOWN
    if type(column_name_or_number) == type("abc"):
        # указано имя столбца
        result = detect_data_type(data[column_name_or_number])
    elif type(column_name_or_number) == type(123):
        # указан номер столбца
        vector = []
        for row in data:
            vector.append(row[column_name_or_number])
        result = detect_data_type(vector)
        vector = None
    else:
        # считаем, что передан одномерный массив строк
        for s in data:
            current = detect_data_type_for_string(s, comma_to_dots)
            if result == DATA_TYPE__UNKNOWN:
                # первый элемент
                result = current
            elif result == DATA_TYPE__INTEGER:
                # пока тип данных определён как целое число
                if current == DATA_TYPE__FLOAT:
                    result = DATA_TYPE__FLOAT
                if current in [DATA_TYPE__DATE_TIME, DATA_TYPE__BOOLEAN, DATA_TYPE__STRING]:
                    result = DATA_TYPE__STRING
            elif result == DATA_TYPE__FLOAT:
                # пока тип данных определён как дробное число
                if current in [DATA_TYPE__DATE_TIME, DATA_TYPE__BOOLEAN, DATA_TYPE__STRING]:
                    result = DATA_TYPE__STRING
            elif result == DATA_TYPE__DATE_TIME:
                # пока тип данных определён как дата/время
                if current != DATA_TYPE__DATE_TIME:
                    result = DATA_TYPE__STRING
            elif result == DATA_TYPE__BOOLEAN:
                # пока тип данных определён как логическое значение
                if current != DATA_TYPE__BOOLEAN:
                    result = DATA_TYPE__STRING
            if result == DATA_TYPE__STRING:
                break
    return result



if __name__ == "__main__":
    #s1 = "hello #@! world"; s2 = remove_comment(s1, "#@!"); print(s2)
    #s1 = "123,456"; x1 = str_to_float(s1, True); print(x1)
    #x = str_to_float(",123456789", True,);  print("x=", x, type(x));  exit(0)
    #items = [5, 3, 8, 12, 7]; prc = get_procentile(0.75, items,); print(prc)
    #items = ["5", "6", "7.1", "2024.11.30"]; data_type = detect_data_type(items); print(data_type)
    #items = ["2024.11.30", "2024.12.01", "2024.12.02", "2024.11.30"]; data_type = detect_data_type(items); print(data_type)
    items = ["1", "0", "0", "1", "1"]; data_type = detect_data_type(items); print(data_type)
    pass
