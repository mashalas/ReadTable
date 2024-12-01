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


# ----- удалить комментарий -----
def remove_comment(s, comment_sequence) -> str:
    p = s.find(comment_sequence)
    if p >= 0:
        s = s[0:p]
    s = s.strip()
    return s


# ----- Однократная замена запятой на точку (1,2345 => 1.2345) -----
def comma_to_dot_once(s:str) -> str:
    count = s.count(",")
    if count == 1:
        s = s.replace(",", ".")

"""
# ----- Попытаться преобразовать строку к дробному числу (при ошибке - None) -----
# ----- comma_to_dots: когда True - заменить запятую на точку перед конвертацией -----
def str_to_float(s):
    s = comma_to_dot_once(s)
    result = None
    try:
        result = float(s)
    except:
        result = None
    return result
"""

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

# ----- Из даты в американском формате (mm.dd.yyyy) перевести в норальный формат даты (dd.mm.yyyy) -----
def from_american_dates(s, to_iso_format:bool = False):
    if len(s) < 10:
        # слишком мало символов, чтобы быть датой
        return s
    year = None
    month = None
    day = None
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
        month = s[0:2]
        day = s[3:5]
        year = s[6:10]
        try:
            d = datetime.datetime(int(year), int(month), int(day))
        except:
            # не удалось конвертировать в дату
            year = None
            month = None
            day = None
    result = s
    if year != None and month != None and day != None:
        if to_iso_format:
            result = year + "-" + month + "-" + day + s[10:len(s)]
        else:
            result = day + "." + month + "." + year + s[10:len(s)]
    else:
        # не является строкой в формате nn?nn?nnnn или по выделенным компонентам не удалось сформировать корректную дату
        result = s
    return result

#print(from_american_dates("16.21.1980 12:50", True)); exit(0)

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
def detect_data_type_for_string(s:str) -> str:
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
    try:
        x = float(s)
        return DATA_TYPE__FLOAT
    except:
        pass

    # является ди переданная строка датой/временем в форматах dd.mm.yyyy hh:mm:ss или yyyy-mm-dd hh:mm:ss
    x = str_to_time(s)
    if x != None:
        return DATA_TYPE__DATE_TIME
    
    # оставить переданный параметр строкой
    return DATA_TYPE__STRING


# ----- Для одномерного массива строк  определить тип данных, к которому относятся значения этого массива -----
def detect_data_type_for_array(data):
    result = DATA_TYPE__UNKNOWN
    for s in data:
        current = detect_data_type_for_string(s)
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

# ----- Конвертировать строку в указанный тип данных -----
def convert_string_to_data_type(s:str, target_data_type:str, exception_on_wrong_data_type:bool):
    result = None
    if target_data_type == DATA_TYPE__INTEGER:
        try:
            result = int(s)
        except:
            if exception_on_wrong_data_type:
                result = int(s)
            else:
                result = None
    elif target_data_type == DATA_TYPE__FLOAT:
        try:
            result = float(s)
        except:
            if exception_on_wrong_data_type:
                result = float(s)
            else:
                result = None
    elif target_data_type == DATA_TYPE__BOOLEAN:
        if s.lower() in TRUE_VALUES:
            result = True
        elif s.lower() in FALSE_VALUES:
            result = False
        else:
            # строка не присутствует ни в массив TRUE_VALUES[], ни в массиве FALSE_VALUES[]
            if exception_on_wrong_data_type:
                raise ValueError("Cannot convert '{}' neither to True nor False" . format(s))
            else:
                result = None
    elif target_data_type == DATA_TYPE__DATE_TIME:
        result = str_to_time(s)
        if result == None:
            if exception_on_wrong_data_type:
                raise ValueError("Cannot convert '{} to date/time data-type" . format(s))
    elif target_data_type == DATA_TYPE__STRING:
        result = str(s)
    else:
        result = s
    return result


def convert_array_to_data_type(items, target_data_type):
    if target_data_type != DATA_TYPE__STRING:
        for i in range(len(items)):
            items[i] = convert_string_to_data_type(
                items[i], 
                target_data_type = target_data_type,
                exception_on_wrong_data_type = False
            )


# ----- Преобразовать одномерный массив A[] в двумерный с N столбцами, где N - количество классов в classes[] -----
# каждый элемент classes[] - список значений соответствующих одному классу
def one_hot_encoding(A, classes, case_sensitive:bool = True):
    # classes - [ 
    #   ["Iris-setosa", "setosa"], 
    #   ["Iris-versicolor", "versicolor"], 
    #   ["Iris-virginica", "virginica"] ]
    # ]
    if not(case_sensitive):
        # если без учёта регистра, то перевести все классы в нижний регистр
        classes_lower = [x.lower() for x in classes]
    result = []
    for i in range(len(A)):
        ohe_row = [0 for j in range(len(classes))]
        for j in range(len(classes)):
            if case_sensitive:
                # с учётом регистра
                if A[i] in classes[j]:
                    ohe_row[j] = 1.0
                    break
            else:
                # без учёта регистра
                if A[i].lower() in classes_lower[j]:
                    ohe_row[j] = 1.0
                    break
        result.append(ohe_row)
    return result

#Y = ["aa", "bb", "aa", "cc"]
#classes = ["Aa", "Bb"]
#Y_ohe = one_hot_encoding(Y, classes, False)
#print(Y_ohe)
#exit(0)

# ----- Извлечь вектор-столбец из двумерного массива -----
def extract_from_table(T, column_number):
    result = []
    for i in range(len(T)):
        result.append(T[i][column_number])
    return result


# ----- Обновить в двумерном массиве значения столбца -----
def store_to_table(T, column_number, vector):
    for i in range(len(vector)):
        T[i][column_number] = vector[i]


# ----- Получить список уникальных значений в массиве -----
def get_unique_values(T, column_number = None):
    if column_number == None:
        # считаем, что передан одномерный массив
        return list(set(T))
    else:
        tmp_vector = extract_from_table(T, column_number)
        return list(set(tmp_vector))
    
# ----- Добавить в один двумерный массив элементы другого двумерного массива (количество столбцов должно совпадать) -----
def extend_double_dimensioned_array(append_to, append_from) -> None:
    for i in range(len(append_from)):
        row = []
        for j in range(len(append_from[i])):
            row.append(append_from[i][j])
        append_to.append(row)


#s1 = "abc"; s2 = str(s1); print(s2); exit(0)
#x1 = convert_string_to_data_type("True", DATA_TYPE__BOOLEAN, True); print(x1); exit(0)
#x1 = convert_string_to_data_type("15.15.2024", DATA_TYPE__DATE_TIME, True); print(x1); exit(0)
        
"""
def use_mem(size):
    import random
    A = []
    for i in range(size):
        A.append(random.randint(-1000, +1000))
    print(len(A))
    A = None
    print("free")
"""

if __name__ == "__main__":
    #s1 = "hello #@! world"; s2 = remove_comment(s1, "#@!"); print(s2)
    #s1 = "123,456"; x1 = str_to_float(s1, True); print(x1)
    #x = str_to_float(",123456789", True,);  print("x=", x, type(x));  exit(0)
    #items = [5, 3, 8, 12, 7]; prc = get_procentile(0.75, items,); print(prc)
    #items = ["5", "6", "7.1", "2024.11.30"]; data_type = detect_data_type(items); print(data_type)
    #items = ["2024.11.30", "2024.12.01", "2024.12.02", "2024.11.30"]; data_type = detect_data_type(items); print(data_type)
    #items = ["1", "0", "2", "1", "1.2"]; data_type = detect_data_type_for_array(items); print(data_type)
    #A1 = [ [1,2,3], [4,5,6] ]; A2 = [ [6,7,8], [9, 10, 11] ]; extend_double_dimensioned_array(A1, A2); print(A1)
    #use_mem(1024*1024*1024)
    import pathlib; WorkDir = pathlib.Path(__file__).resolve(strict=True).parent; print(WorkDir)
    pass
