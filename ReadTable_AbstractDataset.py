#!/usr/bin/python3

import ReadTable_Util

from abc import ABC, abstractmethod

class ReadTable_AbstractDataset(ABC):
    def __init__(self) -> None:
        self.data = None
        self.columns = []
        self.criterias = []
        self.accept = True # если есть критерии принятия/игнорирования, то выполняются дополнительные проверки

        self.OHE_when_matched = 1.0
        self.OHE_when_missed = 0.0

    @abstractmethod
    def reset(self):
        self.data = None


    def add_accept_criteria(self, criteria, ignore_case:bool = False, for_column:str = "") -> None:
        self.criterias.append({
            "action": ReadTable_Util.ACTION__ACCEPT,
            "criteria": criteria,
            "ignore_case": ignore_case,
            "for_column": for_column
        })

    def add_ignore_criteria(self, criteria, ignore_case:bool = False, for_column:str = ""):
        self.criterias.append({
            "action": ReadTable_Util.ACTION__IGNORE,
            "criteria": criteria,
            "ignore_case": ignore_case,
            "for_column": for_column
        })

    def accept_or_ignore(self, s):
        accept_criterias_count = 0
        ignore_criterias_count = 0
        accept_matches_count = 0
        ignore_matches_count = 0
        
        for cr in self.criterias:
            if cr["action"] == ReadTable_Util.ACTION__ACCEPT:
                accept_criterias_count += 1
                if type(cr["criteria"]) == type("abc"):
                    if s.find()
            elif cr["action"] == ReadTable_Util.ACTION__IGNORE:
                ignore_criterias_count += 1
            pass
        if accept_criterias_count == 0:
            result = ReadTable_Util.ACTION__ACCEPT
        else:
            if accept_matches_count > 0:
                result = ReadTable_Util.ACTION__ACCEPT
            else:
                result = ReadTable_Util.ACTION__IGNORE
        if ignore_matches_count > 0:
            result = ReadTable_Util.ACTION__IGNORE
        return result


    def add_column(
            self,
            column_name_in_file,
            column_name_in_dataset = "",
            kind = ReadTable_Util.COLUMN_KIND__SIMPLE,
            transformations = [],
            OHE_values = []
    ):
        if kind == ReadTable_Util.COLUMN_KIND__ONE_HOT_ENCODING:
            if OHE_values == type("abc"):
                # указано одно значение, при котором устанавливать 1.0 в данном столбце при использовании OneHotEncoding - 
                # - переделать в массив из одного элемента
                OHE_values = [OHE_values]
            if len(OHE_values) == 0:
                msg = "Values for OneHotEncoding not specified"
                raise Exception(msg)
            if column_name_in_dataset == "":
                column_name_in_dataset = column_name_in_file + "=" + ",".join(OHE_values)
            
        else:
            if column_name_in_dataset == "":
                column_name_in_dataset = column_name_in_file
        self.columns.append({
            "src_name":         column_name_in_file,
            "dst_name":         column_name_in_dataset,
            "src_number":       -1,
            "kind":             kind,
            "transformations":  transformations,
            "OHE_values":       OHE_values
        })

    def detect_columns_numbers(self, header, ignore_case:bool = False) -> None:
        if len(self.columns) == 0:
            # если не указаны столбцы - прочитать все столбцы файла (названия столбцов уже содержатся в header, тип столбцов - simple)
            for j in range(len(header)):
                self.add_column(header[j], header[j], ReadTable_Util.COLUMN_KIND__SIMPLE)
                self.columns[j]["src_number"] = j
            return
        for c in self.columns:
            found = False
            src = c["src_name"]
            if type(src) == type(123):
                # вместо имени столбца указан его номер
                if src < 0:
                    # указан номер столбца с конца (-1=последний столбец, -2=предпоследний столбец и т.д.)
                    src = len(header) + src
                c["src_number"] = src
                found = True
            elif type(src) == type("abc"):
                # указано имя столбца из файла
                for j in range(len(header)):
                    if ignore_case:
                        if src.lower() == header[j].lower():
                            c["src_number"] = j
                            found = True
                            break
                    else:
                        if src == header[j]:
                            c["src_number"] = j
                            found = True
                            break
            if not found:
                msg = 'Cannot find column "{}" in [{}]' . format(src, ", ".join(header))
                raise Exception(msg)
            

    def dump(self, filename, separator = "\t", encoding = "utf-8", columns = []):
        # в абстрактном классе выгружается только заголовок
        # в классах-потомках открывать файл на дозапись (mode = "at")
        with open(filename, "wt", encoding=encoding) as f:
            dumped_columns_count = 0
            for j in range(len(self.columns)):
                if dumped_columns_count > 0:
                    f.write(separator)
                if len(columns) == 0 or self.columns["dst_name"] in columns:
                    f.write(self.columns["dst_name"])
                    dumped_columns_count += 1
            f.write("\n")  
    


    #def set_columns_numbers(self, header, ignore_case:bool = False):
    #    tmp_columns = []
    #    for c in self.columns:
    #        tmp_columns.append(c["name"])
    #    self.columns_numbers = ReadTable_Reader.get_columns_numbers(tmp_columns, header, ignore_case)
        
        

    def rename_column(self, old_name, new_name):
        for i in range(len(self.columns)):
            if self.columns[i]["name"] == old_name:
                self.columns[i]["name"] = new_name
                return True
        return False
    

    def delete_column(self, name):
        found_count = 0
        for i in range(len(self.columns)):
            if self.columns[i]["name"] == name:
                del self.columns[i]
                found_count += 1
        return found_count > 0

    @abstractmethod
    def add_row(self, parts):
        pass
        #row = []
        #for cn in self.columns_numbers:
        #    row.append(parts[cn])
        #self.data.append(row)


    def postreading():
        pass

