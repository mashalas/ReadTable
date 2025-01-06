#!/usr/bin/python3

import ReadTable_Util
import ReadTable_AbstractDataset
import numpy as np

"""
Для указания типа данных при преобразовании строки в массив NumPy можно использовать функцию numpy.fromstring(). 23 Она создаёт одномерный массив из текстовых данных в строке. 3

Синтаксис функции: numpy.fromstring(строка, dtype=float, count=-1, sep=‘ ‘). 3

Параметры:

строка — строка, содержащая данные; 3
dtype — тип данных массива (необязательно); 3
count — количество элементов для чтения (необязательно); 3
sep — строка, разделяющая числа в данных (необязательно). 3
По умолчанию тип данных — float.

s1 = "123.456"
x1 = np.fromstring(s1, dtype=np.float64, sep='~')[0]
print(x1)
exit(0)
"""

class ReadTable_numpy(ReadTable_AbstractDataset.ReadTable_AbstractDataset):
    
    def __init__(self, dtype) -> None:
        super().__init__()
        #self.data = None
        self.initial_rows_count = 1024
        self.dtype = dtype
        self.reserved_rows_count = 0
        self.used_rows_count = 0



    def reset(self):
        self.reserved_rows_count = self.initial_rows_count
        self.used_rows_count = 0
        columns_count = len(self.columns)
        self.data = np.zeros((self.reserved_rows_count, columns_count), dtype=self.dtype)


    # ----- Добавить строку в numpy-массив -----
    def add_row(self, parts):
        super().add_row(parts)
        if self.used_rows_count == self.reserved_rows_count:
            # таблица заполнена полностью, увеличить количество строк в таблице
            self.reserved_rows_count = 2 * self.reserved_rows_count
            if self.used_rows_count == self.reserved_rows_count:
                self.reserved_rows_count + 1
            self.data.resize((self.reserved_rows_count, len(self.columns)), refcheck = False)
            #print("reserved_rows_count:", self.reserved_rows_count)
        i = self.used_rows_count
        for j in range(len(self.columns)):
            c = self.columns[j]
            s = parts[ c["src_number"] ]
            if c["kind"] == ReadTable_Util.COLUMN_KIND__SIMPLE:
                # +++ kind=simple - дробное число как есть +++
                self.data[i][j] = float(s)
            elif c["kind"] == ReadTable_Util.COLUMN_KIND__ONE_HOT_ENCODING:
                # +++ kind=OHE - только в одном из столбцов будет установлено 1.0, в остальных останется 0.0 +++
                for possible_value in c["OHE_values"]:
                    if s == possible_value:
                        self.data[i][j] = self.OHE_when_matched
                    else:
                        self.data[i][j] = self.OHE_when_missed
        self.used_rows_count += 1
        

    def postreading(self):
        columns_count = len(self.columns)
        self.data.resize((self.used_rows_count, columns_count), refcheck=False)


