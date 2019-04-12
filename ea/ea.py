# coding: utf-8
from git import Repo
import glob
import os
import csv

import settings
from sco import Sco, SchemaChange, SchemaChangeSequence

class EvolutionAssistant():
    def __init__(self, module, repo_dir, code_dir, schema_dir, query_files, commit_hash, map_table, verbose):
        self.module = module
        self.code_dir = code_dir
        self.schema_dir = schema_dir
        self.query_files = query_files
        self.map_table_file = map_table
        self.verbose = verbose
        self.init_map_table(map_table)

        git = Repo(repo_dir).git()
        git.checkout("-f", commit_hash)

        ADD = self.simple_add
        SCHEMA = self.schema_maintenance
        MAP = self.map_maintenance
        APPLICATION = self.application_maintenance
        QUERY = self.query_maintenance

        # maps SCOs to the functions that must be used to calculate their impact
        self.impact_map = {
            Sco.ADD_COLUMN :    [ ADD ],
            Sco.DROP_COLUMN:    [ SCHEMA, MAP, APPLICATION, QUERY ],
            Sco.RENAME_COLUMN:  [ SCHEMA, MAP, APPLICATION, QUERY ],
            Sco.ADD_TABLE:      [ ADD ],
            Sco.DROP_TABLE:     [ SCHEMA, MAP, APPLICATION, QUERY ],
            Sco.RENAME_TABLE:   [ SCHEMA, MAP, APPLICATION, QUERY ]
        }

    def init_map_table(self, f):
        schema_var_to_row = {}
        with open(f, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            i = 0
            for row in reader:
                schema_var = row[-1].lower()
                row_data = [i] + row[:len(row)]
                if schema_var in schema_var_to_row:
                    schema_var_to_row[schema_var].append(row_data)
                else:
                    schema_var_to_row[schema_var] = [row_data]
                i += 1
        self.map_table = schema_var_to_row
    
    def get_classpath(self, classname):
        base_dir = self.code_dir + self.module
        classes = glob.glob(base_dir + '/**/*.java', recursive = True)
        for c in classes:
            if c.endswith(classname):
                return c
        raise ValueError("class not found!")

    def get_affected_lines(self, file_path, var):
        var = var.lower()
        f_rd = open(file_path, 'r')
        line_num = 1
        lines = []
        line = f_rd.readline()

        while line:
            if line.lower().find(var) != -1:
                lines.append((line_num, line))
            line_num += 1
            line = f_rd.readline()

        f_rd.close()
        return lines
    
    def get_affected_schemas(self, var):
        schema_files = glob.glob(self.schema_dir + '*create.sql', recursive = True)
        file_to_lines = {}
        for s in schema_files:
            lines = self.get_affected_lines(s, var)
            if lines:
                file_to_lines[s] = lines
        return file_to_lines

    def schema_maintenance(self, var):
        affected_schemas = self.get_affected_schemas(var)
        impact = 0
        for s in affected_schemas:
            lines = affected_schemas[s]
            impact += len(lines)
        return (impact, affected_schemas)

    def map_maintenance(self, var):
        map_entry = self.map_table[var]
        lines = []
        for entry in map_entry:
            line_num = entry[0]
            line = entry[1:]
            lines.append((line_num, line))
        return (len(map_entry), { self.map_table_file : lines })

    def application_maintenance(self, var):
        maps = self.map_table[var]

        affected_classes_and_variables = [[m[3], m[4]] for m in maps]
        for i in range(len(affected_classes_and_variables)):
            classname = affected_classes_and_variables[i][0]
            affected_classes_and_variables[i][0] = self.get_classpath(classname)

        res = {}
        maintenance = 0
        for [classpath, appvar] in affected_classes_and_variables:
            lines = self.get_affected_lines(classpath, appvar)
            maintenance += len(lines)
            res[classpath] = lines
        return (maintenance, res)

    def query_maintenance(self, var):
        res = {}
        maintenance = 0
        for q in self.query_files:
            classpath = self.get_classpath(q)
            lines = self.get_affected_lines(classpath, var)
            maintenance += len(lines)
            res[classpath] = lines
        return (maintenance, res)

    def simple_add(self, var):
        return (1, {})

    def get_impact(self, sequence):
        print('----------------')
        impact = 0
        for sc in sequence:
            print(str(sc))
            sc_impact = 0
            operator = sc.get_operator()
            var = sc.get_operand()
            maintenance_funcs = self.impact_map[operator]
            for f in maintenance_funcs:
                partial_result = f(var)
                partial_impact = partial_result[0]
                sc_impact += partial_impact
                if self.verbose > 0:
                    print("\t+ " + str(partial_impact) + " " + f.__name__)
                if self.verbose > 1:
                    file_dict = partial_result[1]
                    for fn in file_dict:
                        lineNums = [e[0] for e in file_dict[fn]]
                        print("\t\t" + fn + " lines " + str(lineNums))
            print("Partial impact " + str(sc_impact))
            print('----------------')
            impact += sc_impact
        return impact

if __name__ == "__main__":
    ea = EvolutionAssistant(settings.MODULE,
                            settings.REPO_DIR,
                            settings.CODE_DIR,
                            settings.SCHEMA_DIR,
                            settings.QUERY_FILES,
                            settings.COMMIT_HASH,
                            settings.MAP_TABLE,
                            2 )

    sc1 = SchemaChange(Sco.ADD_COLUMN, "new_column")
    sc2 = SchemaChange(Sco.RENAME_COLUMN, "carrier_cnpj")
    sc3 = SchemaChange(Sco.DROP_COLUMN, "contract_type")
    seq = SchemaChangeSequence()
    seq.add_all(sc1, sc2, sc3)
    print("total impact " + str(ea.get_impact(seq)))

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
    