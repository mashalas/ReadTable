#!/usr/bin/python3


import datetime


DATA_TYPE__STRING = "s"
DATA_TYPE__INTEGER = "i"
DATA_TYPE__FLOAT = "f"
DATA_TYPE__BOOLEAN = "b"
DATA_TYPE__DATE_TIME = "dt"
TRUE_VALUES  = ("1", "yes", "true",  "on",  "enable",  "enabled",  "+", "ok")
FALSE_VALUES = ("0", "no",  "false", "off", "disable", "disabled", "-")

def str_to_date_time(s):
    #yyyy-mm-dd hh:mm:ss
    #0123456789012345678 {19}
    if len(s) < 10:
        return None
    year = 0
    month = 0
    day = 0
    hour = 0
    minute = 0
    second = 0
    if len(s) >= 10:
        year_str = s[0:4]
        try:
            year = int(year_str)
        except Exception:
            return None
        
        month_str = s[5:7]
        try:
            month = int(month_str)
        except Exception:
            return None

        day_str = s[8:10]
        try:
            day = int(day_str)
        except Exception:
            return None
        
        if len(s) >= 13:
            hour_str = s[11:13]
            try:
                hour = int(hour_str)
            except Exception:
                return None

        if len(s) >= 16:
            minute_str = s[14:16]
            try:
                minute = int(minute_str)
            except Exception:
                return None

        if len(s) >= 19:
            second_str = s[17:19]
            try:
                second = int(second_str)
            except Exception:
                return None
    try:
        Result = datetime.datetime(year, month, day, hour, minute, second)
    except Exception:
        return None
    return Result   


def read_columns(
        files, 
        columns = [], # имена или номера столбцов
        separator = "\t", # символ-разделитель
        header_only = False, # прочитать только заголовок и завершить чтене файла
        multiseparators_as_one = False, # несколько символов-разделителей интерпретировать как один
        target_types = DATA_TYPE__STRING, # в какой тип данных конвертировать (целое, дробное, логическое или оставить строкой)
        skip_first_lines = 0, # пропустить первые N строк файла
        comma_to_dots = False, # заменить запятые на точки (полезно при конвертировании в дробные числа записей сохранённых из экселя)
        rows_max_count__per_file = 0, # прочитать из каждого файла не более N строк с данными
        rows_max_count__total = 0, # прочитать суммарно из всех файлов не более N строк с данными
        convert = {}
):
    if type(files) == type("abc"):
        # если указан один файл - преобразовать этот параметр в массив из одного элемента
        files = [files]
    if type(target_types) == type("abc"):
        # если указан один тип данных, преобразовать этот параметр в массив из одного элемента,
        # позже этот массив может быть расширен до количества столбцов
        target_types = [target_types]

    A = []
    stop_reading_files = False
    for filename in files:
        if stop_reading_files:
            break
        lines_count = 0
        header = []
        columns_numbers = []
        processed_data_rows_from_the_file = 0
        with open(filename, "rt") as f:
            for s in f:
                lines_count += 1
                if skip_first_lines > 0 and lines_count <= skip_first_lines:
                    continue
                s = s.lstrip()
                while len(s) > 0 and s[-1] in ["\r", "\n"]:
                    s = s[0:len(s)-1]
                if len(s) == 0:
                    continue # пустая строка или только пробельные символы
                if s[0] == "#":
                    continue # комментарий
                if multiseparators_as_one:
                    # заменить множественные символы-разделители на один
                    while s.find(separator + separator) >= 0:
                        s = s.replace(separator + separator, separator)
                parts = s.split(separator)
                if len(header) == 0:
                    # читается строка с заголовком
                    header = parts.copy()
                    if header_only:
                        return header
                    if len(columns) == 0:
                        # читать все столбцы
                        columns = header.copy()
                    for c in columns:
                        if type(c) == type(123):
                            # указан номер столбца
                            if c < 0:
                                # указан номер столбца с конца
                                c = len(header) + c
                            columns_numbers.append(c)
                        else:
                            # указано имя столбца
                            for j in range(len(header)):
                                if header[j] == c:
                                    columns_numbers.append(j)
                                    break                
                    # расширить массив с целевыми типами данных до количества столбцов
                    # если список столбцов не был указан, чтобы прочитать все столбцы, то до текущего момента было неизвестно количество столбцов
                    while len(target_types) < len(columns):
                        target_types.append(target_types[-1])

                    continue
                # читается строка с данными
                row = []
                for cn in columns_numbers:
                    one_value_src = parts[cn]
                    if len(convert) > 0:
                        # указаны трансформации
                        for key in convert.keys():
                            if one_value_src == key:
                                one_value_src = convert[key]
                                break
                    if target_types[len(row)] == DATA_TYPE__INTEGER:
                        #one_value_dst = int(one_value_src) # str -> int; 3.14159 вызовет ошибку
                        if comma_to_dots:
                            if type(one_value_src) == type("abc"):
                                one_value_src = one_value_src.replace(",", ".")
                        one_value_dst = int(round(float(one_value_src))) # str -> float -> round -> int ; 3.14159 -> 3
                    elif target_types[len(row)] == DATA_TYPE__FLOAT:
                        if comma_to_dots:
                            if type(one_value_src) == type("abc"):
                                one_value_src = one_value_src.replace(",", ".")
                        one_value_dst = float(one_value_src)
                    elif target_types[len(row)] == DATA_TYPE__BOOLEAN:
                        one_value_src = one_value_src.lower()
                        if one_value_src in TRUE_VALUES:
                            one_value_dst = True
                        elif one_value_src in FALSE_VALUES:
                            one_value_dst = False
                        else:
                            one_value_dst = None
                    elif target_types[len(row)] == DATA_TYPE__DATE_TIME:
                        one_value_dst = str_to_date_time(one_value_src)
                    else:
                        # целевой тип данных - строка, значение остаётся без изменений
                        one_value_dst = one_value_src
                    row.append(one_value_dst)
                if len(row) == 1:
                    # если один столбец, то добавлять скаляр, а не массив значений (в результате будет одномерный, а не двумерный массив)
                    row = row[0]
                A.append(row)
                processed_data_rows_from_the_file += 1
                if rows_max_count__per_file > 0 and processed_data_rows_from_the_file >= rows_max_count__per_file:
                    # прекратить чтение только текущего файла
                    break
                if rows_max_count__total > 0 and len(A) >= rows_max_count__total:
                    stop_reading_files = True # прекратить чтение и остальных файлов
                    break

    return A


def OneHotEncoding(A, transformations):
    # transformations - [ ["Iris-setosa", "setosa"], ["Iris-versicolor", "versicolor"], ["Iris-virginica", "virginica"] ]]
    for i in range(len(A)):
        y_row = [0 for j in range(len(transformations))]
        for j in range(len(transformations)):
            if A[i] in transformations[j]:
                y_row[j] = 1.0
                break
        A[i] = y_row
    return A

