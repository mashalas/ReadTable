#!/usr/bin/python3

import numpy as np

CONTAINER_KIND__PYTHON_LIST = "python_list"
CONTAINER_KIND__NUMPY = "numpy"
CONTAINER_KIND__ANALYZE = "analyze"

NPCOLUMN_KIND__SIMPLE = "s"
NPCOLUMN_KIND__OHE = "ohe"
NPCOLUMN_KIND__MAPPING = "m"

DATA_TYPE__INTEGER = "i"
DATA_TYPE__FLOAT = "f"
DATA_TYPE__DATE_TIME = "t"
DATA_TYPE__BOOLEAN = "b"
DATA_TYPE__STRING = "s"

TRUE_VALUES  = ["yes", "on", "+"]
FALSE_VALUES = ["no", "off", "-"]

def detectDataTypeForString(s):
    pass

def detectDataTypeForList(items):
    pass

class _AbstractContainer:
    def __init__(self, name, columns = []) -> None:
        self.name = name
        self.data = None
        self.columns = columns.copy()
        pass


    def addColumn(self, column):
        self.columns.append(column)

    def addRow(self, parts):
        pass        



class PythonListContainer(_AbstractContainer):
    def __init__(self, name, columns = []) -> None:
        super().__init__(name, columns)



class NumpyContainer(_AbstractContainer):
    def __init__(
            self,
            name,
            columns = [],
            dtype = np.float32

        ) -> None:
        super().__init__(name, columns)
        self.dtype = dtype
        self.default_rows_count = 1024
        self.rows_increment_multiplicator = 1.5
        self.reserved_rows_count = 0
        self.used_rows_count = 0

    
    # ----- Выделить память для numpy-массива -----
    def allocateMemory(self):
        columns_count = len(self.columns)
        self.reserved_rows_count = self.default_rows_count
        self.used_rows_count = 0
        self.data = np.zeros((self.reserved_rows_count, columns_count), dtype = self.dtype)


    # ----- Удалить неиспользованные столбцы numpy-массива -----
    def trimUnusedRows(self):
        columns_count = len(self.columns)
        self.data.resize((self.used_rows_count, columns_count), refcheck=False)


    # ----- Добавить строку в numpy-массив -----
    def addRow(self, parts):
        if self.used_rows_count == self.reserved_rows_count:
            # таблица заполнена полностью, увеличить количество строк в таблице
            self.reserved_rows_count = max(1, int(self.reserved_rows_count * self.rows_increment_multiplicator))
            self.data.resize((self.reserved_rows_count, len(self.columns)), refcheck = False)
            #print("reserved_rows_count:", self.reserved_rows_count)
        i = self.used_rows_count
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
        self.used_rows_count += 1



class AnalyzeContainer(_AbstractContainer):
    def __init__(self, name, columns = []) -> None:
        super().__init__(name, columns)



class ReadTable():
    def __init__(self) -> None:
        self.containers = []
        self.header = []
        self.containers_names = {}


    def _addContainer(
            self,
            kind,
            name,
            columns = [],
            _np_dtype = np.float32
        ):
        for c in self.containers:
            if c.name == name:
                return "Container with name [{}] already exists." . format(name)
        if type(columns) == type("abc") or type(columns) == type(123):
            columns = [columns]
        if kind == CONTAINER_KIND__PYTHON_LIST:
            self.containers.append(PythonListContainer(name, columns))
        elif kind == CONTAINER_KIND__NUMPY:
            self.containers.append(NumpyContainer(name, columns, _np_dtype))
        elif kind == CONTAINER_KIND__ANALYZE:
            self.containers.append(AnalyzeContainer(name, columns))
        else:
            return "Unknown container kind [{}]." . format(kind)
        self.containers_names[name] = len(self.containers) - 1
        return ""


    def addConainer_PythonList(self, name, columns = []):
        err = self._addContainer(CONTAINER_KIND__PYTHON_LIST, name, columns)
        if err != "":
            raise Exception(err)
        return self.containers_names[name]


    def addContainer_Numpy(self, name, columns = [], dtype = np.float32):
        err = self._addContainer(CONTAINER_KIND__NUMPY, name, columns, _np_dtype = dtype)
        if err != "":
            raise Exception(err)
        return self.containers_names[name]


    def addContainer_Analyze(self, name, columns = []):
        err = self._addContainer(CONTAINER_KIND__ANALYZE, name, columns)
        if err != "":
            raise Exception(err)
        return self.containers_names[name]
    

    def addColumn(self, containerNameOrNumber, column):
        if type(containerNameOrNumber) == type(123):
            containerNumber = containerNameOrNumber
        else:
            containerNumber = self.containers_names[containerNameOrNumber]
        self.containers[containerNumber].addColumn(column)


    def read(
            self,
            files,
            skip_first_N_lines = 0,
            transformations = [],
            files_encoding = "utf-8"
    ):
        if type(files) == type("abc"):
            files = [files]
        for one_file in files:
            print("---", one_file, "---")
            with open(one_file, "rt", encoding=files_encoding) as f:
                for s in f:
                    print(s)
        for cn in self.containers:
            if isinstance(cn, PythonListContainer):
                pass
            elif isinstance(cn, NumpyContainer):
                cn.trimUnusedRows()
            elif isinstance(cn, AnalyzeContainer):
                pass
            

    def method1(self):
        #print(self.__c)
        print("qqq", isinstance(self.containers[0], NumpyContainer))




def test1():
    rt = ReadTable()
    rt.addConainer_PythonList("pl1", ["sepal_width", "sepal_length"])
    rt.addConainer_PythonList("pl2", "petal_length")
    rt.addConainer_PythonList("pl1a")
    rt.addColumn("pl2", 0)
    
    print(rt.containers)
    print(rt.containers[0].columns)
    print(rt.containers[1].columns)
    rt.method1()

#print(max(0, 1)); exit(0)

if __name__ == "__main__":
    test1()