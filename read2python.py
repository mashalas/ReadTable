#!/usr/bin/python3

#import datetime
import util


"""
DATA_TYPE__STRING = "s"
DATA_TYPE__INTEGER = "i"
DATA_TYPE__FLOAT = "f"
DATA_TYPE__BOOLEAN = "b"
DATA_TYPE__DATE_TIME = "dt"
TRUE_VALUES  = ("1", "yes", "true",  "on",  "enable",  "enabled",  "+", "ok")
FALSE_VALUES = ("0", "no",  "false", "off", "disable", "disabled", "-")
"""

#s1 = " ab\t"
#s2 = s1
#s2 = s1.strip()
#print("[{}]" . format(s2))
#exit(0)



def read_columns(
        files, 
        columns = [], # имена или номера столбцов
        separator:str = "\t", # символ-разделитель
        header_only:bool = False, # прочитать только заголовок и завершить чтение файла
        target_types:str = util.DATA_TYPE__AUTO, # в какой тип данных конвертировать (целое, дробное, логическое или оставить строкой)
        skip_first_lines:int = 0, # пропустить первые N строк файла
        rows_max_count__per_file:int = 0, # прочитать из каждого файла не более N строк с данными
        rows_max_count__total:int = 0, # прочитать суммарно из всех файлов не более N строк с данными
        multiseparators_as_one:bool = False, # несколько символов-разделителей интерпретировать как один
        comma_to_dots:bool = False, # заменить запятые на точки (полезно при конвертировании в дробные числа записей сохранённых из экселя)
        strip_spaces:bool = False, # удалить начальные и завершающие пробелы и табуляции в прочитанных значениях
        named_arrays:bool = False, # прочитать данные не в двумерный массив, а в одномерные массивы являющиеся значениями словаря {"field1":[1,2,3] , "field2":[5,6,7]}
        exception_on_wrong_data_type:bool = False, # гененировать исключение при невозможности конвертировать строковое значение в указанный в target_types[] тип данных
        #characters_case_conversion:str = "", # u/U - преобразовать значения в верхний регистр, l/L - преобразовать значения в нижний регистр
        transformations = {} # словаь трансформаций, в котором ключ - исходная строка из файла, значение - на что заменить эту строку или u/U/upper - преобразовать в верхний регистр, l/L/lower - преобразовать в нижний регистр.
):
    if type(files) == type("abc"):
        # если указан один файл - преобразовать этот параметр в массив из одного элемента
        files = [files]
    if type(target_types) == type("abc"):
        # если указан один тип данных, преобразовать этот параметр в массив из одного элемента,
        # позже этот массив может быть расширен до количества столбцов
        target_types = [target_types]

    if named_arrays:
        A = {}
    else:
        A = []
    stop_reading_files = False
    for filename in files:
        if stop_reading_files:
            break
        lines_count = 0
        header = []
        columns_indexes = []
        processed_data_rows_from_the_file = 0
        with open(filename, "rt") as f:
            for s in f:
                lines_count += 1
                if skip_first_lines > 0 and lines_count <= skip_first_lines:
                    continue
                s = s.lstrip()
                while len(s) > 0 and s[-1] in ["\r", "\n"]:
                    # убрать завершающие переводы строк/возвраты каретки
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
                            columns_indexes.append(c)
                        else:
                            # указано имя столбца
                            for j in range(len(header)):
                                if header[j] == c:
                                    columns_indexes.append(j)
                                    break
                        if named_arrays:
                            # если результат - словарь массивов, то добавить заготовку для массива, если заготовка с этим именем ещё не существует
                            cn = header[ columns_indexes[ len(columns_indexes)-1 ] ]
                            if cn not in A:
                                A[cn] = []
                    # расширить массив с целевыми типами данных до количества столбцов
                    # если список столбцов не был указан, чтобы прочитать все столбцы, то до текущего момента было неизвестно количество столбцов
                    while len(target_types) < len(columns):
                        target_types.append(target_types[-1])
                    continue
                # +++ читается строка с данными +++
                row = []
                for ci in columns_indexes:
                    one_value_src = parts[ci]
                    if strip_spaces:
                        one_value_src = one_value_src.strip() # удалить пробелы и табуляции в начале и конце значения
                    if len(transformations) > 0:
                        # указаны трансформации
                        for key in transformations.keys():
                            if key in ("u", "U", "upper"):
                                if transformations[key]:
                                    one_value_src = one_value_src.upper()
                            elif key in ("l", "L", "lower"):
                                if transformations[key]:
                                    one_value_src = one_value_src.lower()
                            elif key == one_value_src:
                                one_value_src = transformations[key]
                                break
                    one_value_dst = util.convert_string_to_data_type(
                        one_value_src,
                        target_data_type = target_types[len(row)],
                        exception_on_wrong_data_type = exception_on_wrong_data_type,
                        comma_to_dots = comma_to_dots
                    )
                    row.append(one_value_dst)
                    if named_arrays:
                        column_name = header[ci]
                        A[column_name].append(one_value_dst)
                    else:
                        A.append(row)
                processed_data_rows_from_the_file += 1
                if rows_max_count__per_file > 0 and processed_data_rows_from_the_file >= rows_max_count__per_file:
                    # прекратить чтение только текущего файла
                    break
                if rows_max_count__total > 0 and len(A) >= rows_max_count__total:
                    stop_reading_files = True # прекратить чтение и остальных файлов
                    break
    
    # если есть столбцы с автоматическим определением типа данных, то сконвертировать данные в этом столбце в тот тип данных,
    # который определится для этого столбца
    for j in range(len(target_types)):
        tt = target_types[j]
        if tt == util.DATA_TYPE__AUTO:
            if named_arrays:
                #column_name = header[j]
                once_column_index = columns_indexes[j]
                column_name = header[once_column_index]
                detected_data_type = util.detect_data_type_for_array(A[column_name], comma_to_dots)
                if detected_data_type != util.DATA_TYPE__STRING:
                    util.convert_array_to_data_type(A[column_name], detected_data_type, comma_to_dots)
            else:
                tmp_vector = util.extract_from_table(A, j)
                detected_data_type = util.detect_data_type_for_array(tmp_vector, comma_to_dots)
                if detected_data_type != util.DATA_TYPE__STRING:
                    util.convert_array_to_data_type(tmp_vector, detected_data_type, comma_to_dots)
                    util.store_to_table(A, j, tmp_vector)
                tmp_vector = None
    return A


if __name__ == "__main__":
    from pprint import pprint
    filename = "/mnt/lindata/sources/python/ml/ReadTable/iris.csv"
    A = read_columns(
        filename,
        multiseparators_as_one = True,
        separator = ",",
        named_arrays = False
    )
    pprint(A)
    
    # +++ OHE-test +++
    #Y = util.one_hot_encoding(A["class"], util.get_unique_values(A["class"])) # when named_arrays = True

    tmp_vector = util.extract_from_table(A, 4)
    Y = util.one_hot_encoding(tmp_vector, util.get_unique_values(tmp_vector))

    pprint(Y)