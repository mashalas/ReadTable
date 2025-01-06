#!/usr/bin/python3

import datetime
import ReadTable_Util

ON_ERROR__EXCEPTION = "e"   # при некорректных данных генерировать исключение и завершать работу
ON_ERROR__WARNING = "w"     # при некорректных данных сообщить об этом и продолжить работу
ON_ERROR__CONTINUE = "c"    # при некорректных данных тихо проигнорировать строку и продолжить работу
ON_ERROR__BREAK = "b"       # при некорректных данных прекратить чтение файла
ON_ERROR__OVERWRITE = "o"
ON_ERROR__IGNORE = "i"




class ReadTable_Reader():
    def __init__(self) -> None:
        self.header = []


    def read(
            self,
            filename,                       # имя файла, который надо прочитать
            separator = ",",                # символ-разделитель между столбцами
            multiseparators_as_one = False, # воспринимать несколько идущих подряд разделителей как один
            comment_sequence = "#",         # символ обозначающий начало однострочного комментария
            comment_at_begin_only = False,  # комментарий может быть только первым непробельным символом; если последовательность символов обозначающая комментарий в середине строки - это не комментарий
            datasets = {},                  # именованные наборы данных (List, NumpyArray, Tensor for TensorFlow и др.)
            append = False,                 # добавить записи из текущего файла к прочитанным ранее записям, иначе очистить
            skip_first_N_lines = 0,         # если > 0 - пропустить первые N строк файла
            data_lines_max_count = 0,       # если > 0 - прочитать не более N строк с данными
            header_only = False,            # прочитать только заголовок
            ignore_case_in_header = False,  # игнорировать регистр при сопоставлении перечисленных столбцов в параметр columns[] с именами столбцов в файле
            transformations = [],           # список трансформаций применяемых ко всеми элементами строк файла (удалить пробелы, верхний/нижний регистр, замены)
            on_wrong_columns_count = ON_ERROR__EXCEPTION,   # как обработать ситуацию, когда в файле количество строк с данными не совпадает с количеством столбцов
            verbose = False,                # выводить на экран прочитанные строки и полученные массивы значений
            encoding = "utf-8"              # кодировка файла
    ):
        if verbose:
            print('\t----- begin reading file: "{}" -----' . format(filename))
        with open(filename, "rt", encoding = encoding) as f:
            self.header.clear()
            data = None
            raw_line_number = 0
            data_lines_count = 0
            column_numbers = None
            for s_raw in f:
                raw_line_number += 1
                if skip_first_N_lines > 0:
                    if raw_line_number <= skip_first_N_lines:
                        if verbose:
                            print("skip line #" + str(raw_line_number))
                        continue
                while len(s_raw) > 0 and (s_raw[-1] in ["\n", "\r"]):
                    # удалить в конце прочитанной строки символы перехода на новую строку и возврата каретки
                    s_raw = s_raw[0:len(s_raw)-1]
                if verbose:
                    print("")
                    print("line:", raw_line_number, sep="\t")
                    print("s_raw:", s_raw, sep="\t")
                if len(s_raw) == 0:
                    continue
                if len(comment_sequence) > 0:
                    # определена последовательность обозначающая комментарий
                    if comment_at_begin_only:
                        # комментарий может быть только первым непробельным символом
                        s_tmp = s_raw.lstrip()
                        if s_tmp.startswith(comment_sequence):
                            s = ""
                    else:
                        # комментарий может располагаться в любом месте строки
                        s = ReadTable_Util.remove_comment(s_raw, comment_sequence)
                else:
                    # последовательность символов обозначающая комментарий не определена
                    s = s_raw
                if multiseparators_as_one:
                    # заменить множественные идущие подряд разделители на один
                    while s.find(separator + separator) >= 0:
                        s = s.replace(separator + separator, separator)
                if verbose:
                    print("s:", s, sep="\t")
                if len(s) == 0:
                    # после удаления комментариев получена пустая строка
                    continue
                parts = s.split(separator)
                if verbose:
                    print("parts:", parts, sep="\t")
                if len(parts) == 0:
                    continue
                #print(parts)
                if len(self.header) == 0:
                    # +++ читается заголовок +++
                    self.header = parts.copy()
                    #print("H:", self.header)
                    if header_only:
                        return self.header
                    for ds_key in datasets.keys():
                        datasets[ds_key].detect_columns_numbers(self.header, ignore_case_in_header)
                        if not append:
                            datasets[ds_key].reset()
                    continue
                # +++ читается строка с данными +++
                if len(transformations) > 0:
                    # указаны трансформации над всеми элементами строк файла
                    for j in range(len(parts)):
                        parts[j] = ReadTable_Util.apply_transformations(parts[j], transformations)
                    if verbose:
                        print("transformed parts:", parts, sep="\t")
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
                for ds_key in datasets.keys():
                    for c in datasets[ds_key].columns:
                        # трансформации применяемые к отдельным столбцам
                        parts[c["src_number"]] = ReadTable_Util.apply_transformations( parts[c["src_number"]], c["transformations"] )
                    datasets[ds_key].add_row(parts)
                data_lines_count += 1
                if data_lines_max_count > 0:
                    if data_lines_count >= data_lines_max_count:
                        if verbose:
                            print("data_lines_count = " + str(data_lines_count))
                        break
        if verbose:
            print('\t----- complete reading file: "{}" -----' . format(filename))
        for ds_key in datasets.keys():
            datasets[ds_key].postreading()
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
    from pprint import pprint
    pprint(data)
