#!/usr/bin/python3

import numpy as np
from pprint import pprint
import util

NPCOLUMN_KIND__SIMPLE = "simple"
NPCOLUMN_KIND__OHE = "ohe"
NPCOLUMN_KIND__MAPPING = "mapping"


class _NPContainer:

    def __init__(self) -> None:
        self.columns = []
        self.data = None
        self.stored_rows_count = -1
        self.reserved_rows_count = -1
        self.OHE_when_matched = 1.0
        self.OHE_when_missed = 0.0
        self.checkPartsFunction = None


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
        self.stored_rows_count = 0
        columns_count = len(self.columns)
        self.data = np.zeros((rows_count, columns_count), dtype=dtype)

    # ----- Удалить неиспользованные столбцы numpy-массива -----
    def trimUnusedRows(self):
        columns_count = len(self.columns)
        self.data.resize((self.stored_rows_count, columns_count), refcheck=False)

    # ----- Добавить строку в numpy-массив -----
    def addRow(self, parts, ignore_case = False, comma_to_dots = False):
        if self.stored_rows_count == self.reserved_rows_count:
            # таблица заполнена полностью, увеличить количество строк в таблице
            self.reserved_rows_count = 1 + int(self.reserved_rows_count * 1.5)
            self.data.resize((self.reserved_rows_count, len(self.columns)), refcheck = False)
            #print("reserved_rows_count:", self.reserved_rows_count)
        i = self.stored_rows_count
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
        self.stored_rows_count += 1

    def dumpData(self, filename, separator, digits_after_dot = 8):
        with open(filename, "wt") as f:
            rows_count = len(self.data)
            columns_count = len(self.columns)
            f.write("SN")
            for j in range(columns_count):
                f.write(separator + self.columns[j]["dst_name"])
            f.write("\n")
            for i in range(rows_count):
                f.write(str(i) + ")")
                for j in range(columns_count):
                    float_template = "{:." + str(digits_after_dot) + "f}"
                    f.write( separator + float_template.format(self.data[i][j]) )
                f.write("\n")

# --- end of class _RT_NPContainer ---

class Read2Numpy:

    def __init__(self, separator = ",", comment = "#", ignore_case = False, comma_to_dots = False) -> None:
        self.separator = separator
        self.comment = comment
        self.ignore_case = ignore_case  # игнорировать регистр при сравнении строк
        self.comma_to_dots = comma_to_dots  # заменять запятые на точки (полезно при получении данных из экселя)
        self.NPs = {} # словарь, в котором ключ - имя (X, Y, XTest, YTrain, ...; значение - объект класса _NPContainer)
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
            self.NPs[name] = _NPContainer()

    def copyColumns(self, src_name, dst_name):
        if not src_name in self.NPs:
            msg = "Cannot find source NP-container [{}]" . format(src_name)
            raise Exception(msg)
        if not dst_name in self.NPs:
            self.NPs[dst_name] = _NPContainer()
            #for c in self.NPs[src_name].columns:
        self.NPs[dst_name].columns = self.NPs[src_name].columns.copy()
        #pprint(self.NPs[dst_name].columns)

    def getContainersList(self):
        return self.NPs.keys()

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
                parts = s.split(self.separator)
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
            
# --- end of class ReadTable ---


if __name__ == "__main__":
    pass

    """
    f = open("/tmp/file1.txt", "wt")
    x = 3/7
    print(x)
    digits_after_dot = 25
    # err f.write("x = {:." + str(digits_after_dot) + "f}" . format(x) + "\n")
    float_template = "{:." + str(digits_after_dot) + "f}"
    f.write("x = " + float_template.format(x) + "\n")
    # err f.write("x = " + '{:.' + str(digits_after_dot) + 'f}'.format(x) + "\n")
    f.close()
    """
