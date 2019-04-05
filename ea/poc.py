# coding: utf-8
from git import Repo
from enum import Enum
import glob
import os
import csv
import settings

class Sco(Enum):
    ADD_COLUMN      = 1
    DROP_COLUMN     = 2
    RENAME_COLUMN   = 3
    ADD_TABLE       = 4
    DROP_TABLE      = 5
    RENAME_TABLE    = 6

class SchemaChange():
    def __init__(self, operator, *operands):
        self.operator = operator
        self.operands = operands

    def __str__(self):
        s = "operator: " + self.operator.name
        if len(self.operands) != 0:
            s += ", args: "
            for o in self.operands:
                s += o + " "
        return s

    def get_operator(self):
        return self.operator

    def get_perands(self):
        return self.operands

class SchemaChangeSequence():
    def __init__(self, changes):
        self.changes = changes

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i < len(self.changes):
            change = self.changes[self.i]
            self.i += 1
            return change
        else:
            raise StopIteration

    def add(self, change):
        self.changes.append(change)

    def add_all(self, changes):
        self.changes.extend(changes)

class EvolutionAssistant():
    def __init__(self, module, repo_dir, src_code_dir, schema_dir, map_table_csv):
        self.module = module
        self.repo_dir = repo_dir
        self.src_code_dir = src_code_dir
        self.schema_dir = schema_dir
        self.init_map_table(map_table_csv)

    def init_map_table(self, f):
        schema_var_to_row = {}
        with open(f, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            i = 0
            for row in reader:
                schema_var = row[-1]
                row_data = [i] + row[:len(row)]
                if schema_var in schema_var_to_row:
                    schema_var_to_row[schema_var].append(row_data)
                else:
                    schema_var_to_row[schema_var] = [row_data]
                i += 1
        self.map_table = schema_var_to_row
    
    def get_classpath(self, classname):
        base_dir = self.src_code_dir + self.module
        classes = glob.glob(base_dir + '/**/*.java', recursive = True)
        for c in classes:
            if c.endswith(classname):
                return c
        raise ValueError("class not found!")

    def get_affected_lines(self, file_path, var):
        var = var.lower()
        f_rd = open(file_path, 'r')
        line_num = 1
        line_nums = []
        line = f_rd.readline()

        while line:
            if line.lower().find(var) != -1:
                line_nums.append(line_num)
            line_num += 1
            line = f_rd.readline()

        f_rd.close()
        return line_nums
    
    def get_affected_schemas(self, var):
        schema_files = glob.glob(self.schema_dir + '*create.sql', recursive = True)
        file_to_lines = {}
        for s in schema_files:
            lines = self.get_affected_lines(s, var)
            if lines:
                file_to_lines[s] = lines
        return file_to_lines

    def get_schema_maintenance(self, var):
        return len(self.get_affected_schemas(var))

    def get_map_maintenance(self, var):
        return len(self.map_table[var])

    def get_application_maintenance(self, var):
        maps = self.map_table[var]
        affected_classes_and_variables = [[m[3], m[4]] for m in maps]
        for i in range(len(affected_classes_and_variables)):
            classname = affected_classes_and_variables[i][0]
            affected_classes_and_variables[i][0] = self.get_classpath(classname)

        maintenance = 0
        for [classpath, appvar] in affected_classes_and_variables:
            maintenance += len(self.get_affected_lines(classpath, appvar))
        return maintenance

if __name__ == "__main__":
    ea = EvolutionAssistant(settings.MODULE, 
                            settings.REPO_DIR,
                            settings.SRC_CODE_DIR,
                            settings.SCHEMA_DIR,
                            settings.MAP_TABLE )

    sco = Sco.ADD_COLUMN # the SCO to analyze
    var = 'logistic_contract' # variable on which the SCO operates
    maintenance = 'UNKNOWN_SCO'

    if sco == Sco.ADD_COLUMN:
        print("schema maintenance", ea.get_schema_maintenance(var))
        print("map maintenance", ea.get_map_maintenance(var))
        print("application maintenance", ea.get_application_maintenance(var))
    # elif sco == Sco.DROP_COLUMN:
    #     pass
    # elif sco == Sco.RENAME_COLUMN:
    #     pass
    # elif sco == Sco.ADD_TABLE:
    #     pass
    # elif sco == Sco.DROP_TABLE:
    #     pass
    # elif sco == Sco.RENAME_TABLE:
    #     pass
    sc1 = SchemaChange(Sco.ADD_COLUMN, "hello")
    sc2 = SchemaChange(Sco.RENAME_TABLE, "table", "chair")
    sc3 = SchemaChange(Sco.DROP_COLUMN, "bye")
    changes = [sc1, sc2]
    seq = SchemaChangeSequence(changes)
    seq.add(sc3)
    for s in seq:
        print(s)

'''
git stuff

git = Repo(repo_dir).git()
# Reversion to the wanted commit
git.checkout("-f","5d9cb0c3b6834c14425b8f5d8f9f5575521e756b")
# Get the whole log for one specific class
log = git.log("--all","HEAD","--full-history","--","**/FreightCostFactorRepository.java")
a=git.show("-s","--format=%cd","414043c7633d597f2650cde9aa3a18c86af074c9")
b=git.show("-s","--format=%cd","844928d3f1be62639d986e7074e5b1eec20ca137")
'''
    