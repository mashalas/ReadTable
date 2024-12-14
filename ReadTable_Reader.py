#!/usr/bin/python3

import datetime
from pprint import pprint

ON_ERROR__EXCEPTION = "e"   # при некорректных данных генерировать исключение и завершать работу
ON_ERROR__WARNING = "w"     # при некорректных данных сообщить об этом и продолжить работу
ON_ERROR__CONTINUE = "c"    # при некорректных данных тихо проигнорировать строку и продолжить работу
ON_ERROR__BREAK = "b"       # при некорректных данных прекратить чтение файла
ON_ERROR__OVERWRITE = "o"
ON_ERROR__IGNORE = "i"


# ----- удалить комментарий -----
def remove_comment(s:str, comment_sequence:str) -> str:
    p = s.find(comment_sequence)
    if p >= 0:
        s = s[0:p]
    s = s.strip()
    return s

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


class ReadTable():
    def __init__(self) -> None:
        self.header = []


    def read(
            self,
            filename,                       # имя файла, который надо прочитать
            separator = ",",                # символ-разделитель между столбцами
            multiseparators_as_one = False, # воспринимать несколько идущих подряд разделителей как один
            comment_sequence = ";",         # символ обозначающий начало однострочного комментария
            comment_at_begin_only = False,  # комментарий может быть только первым непробельным символом
            columns = None,                 # если массив - вернуть словарь, в котором ключ - указанное имя столбца, значение - массив строк со значениями столбца; если None - ничего не возвращать
            containers = {},                # именованные контейнеры для формирования специальных наборов данных (List, NumpyArray, Tensor for TensorFlow и др.)
            skip_first_N_lines = 0,         # если > 0 - пропустить первые N строк файла
            data_lines_max_count = 0,       # если > 0 - прочитать не более N строк с данными
            strip_spaces = False,           # удалять пробельные символы в извлечённых значениях
            header_only = False,            # прочитать только заголовок
            ignore_case_in_header = False,  # игнорировать регистр при сопоставлении перечисленных столбцов в параметр columns[] с именами столбцов в файле
            transformations = [],
            on_wrong_columns_count = ON_ERROR__EXCEPTION,
            verbose = False,                # выводить на экран прочитанные строки и полученные массивы значений
            encoding = "utf-8"              # кодировка файла
    ):
        if verbose:
            print('\t----- begin reading file: "{}" -----' . format(filename))
        with open(filename, "rt", encoding = encoding) as f:
            self.header.clear()
            data = None
            raw_line_number = 0
            column_numbers = None
            for s_raw in f:
                raw_line_number += 1
                while len(s_raw) > 0 and (s_raw[-1] in ["\n", "\r"]):
                    # удалить в конце прочитанной строки символы перехода на новую строку и возврата каретки
                    s_raw = s_raw[0:len(s_raw)-1]
                if verbose:
                    print("")
                    print("line:\t", raw_line_number, sep="")
                    print("s_raw:\t", s_raw, sep="")
                if len(s_raw) == 0:
                    continue
                if len(comment_sequence) > 0:
                    # определена последовательность обозначающая комментарий
                    if comment_at_begin_only:
                        # комментарий может быть только первым непробельным символом
                        s = s_raw.lstrip()
                        if s.startswith(comment_sequence):
                            s = ""
                    else:
                        # комментарий может располагаться в любом месте строки
                        s = remove_comment(s_raw, comment_sequence)
                #print("s_raw=[{}] s=[{}]" . format(s_raw, s))
                if verbose:
                    print("s:\t", s, sep="")
                if len(s) == 0:
                    # после удаления комментариев получена пустая строка
                    continue
                parts = s.split(separator)
                if verbose:
                    print("parts:\t", parts, sep="")
                if len(parts) == 0:
                    continue
                if strip_spaces:
                    # удалить пробелы в элементах строки файла
                    for j in range(len(parts)):
                        parts[j] = parts[j].strip()
                #print(parts)
                if len(self.header) == 0:
                    # +++ читается заголовок +++
                    self.header = parts.copy()
                    #print("H:", self.header)
                    if header_only:
                        return self.header
                    if columns != None:
                        column_numbers = get_columns_numbers(columns, self.header, ignore_case_in_header)
                        data = {}
                        for cn in column_numbers:
                            data[self.header[cn]] = []
                    #print(column_numbers); exit(0)
                    continue
                # +++ читается строка с данными +++
                if len(parts) != len(self.header):
                    # количество элементов в строке файла не совпадает с количеством столбцов этого файла
                    msg = "At line #{} columns count={} <> size of header={}" . format(raw_line_number, len(parts), len(self.header))
                    if on_wrong_columns_count == ON_ERROR__EXCEPTION:
                        raise Exception(msg)
                    elif on_wrong_columns_count == ON_ERROR__WARNING:
                        print("WARNING! " + msg)
                        continue
                    elif on_wrong_columns_count == ON_ERROR__CONTINUE:
                        continue
                    elif on_wrong_columns_count == ON_ERROR__BREAK:
                        print("STOP READING! " + msg)
                        break
                if data != None:
                    for cn in column_numbers:
                        data[self.header[cn]].append(parts[cn])
        if verbose:
            print('\t----- complete reading file: "{}" -----' . format(filename))
        return data


if __name__ == "__main__":
    rt = ReadTable()
    filename = "/mnt/lindata/sources/python/ml/ReadTable/file1.txt"
    separator = "\t"
    encoding = "cp1251"
    data = rt.read(
        filename,
        separator=separator,
        comment_sequence=";",
        comment_at_begin_only=True,
        columns=["pClose", "DateTime"],
        ignore_case_in_header=True,
        strip_spaces=True,
        verbose=False,
        encoding=encoding
    )
    pprint(data)
