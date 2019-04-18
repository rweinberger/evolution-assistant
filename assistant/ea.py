# coding: utf-8
from git import Repo
from functools import reduce
import glob
import os
import csv

from assistant.sco import Sco, SchemaChange, SchemaChangeSequence

class EvolutionAssistant():
    def __init__(self, module, repo_dir, code_dir, schema_dir, query_files, commit_hash, map_table, verbose):
        self.module = module
        self.code_dir = code_dir
        self.schema_dir = schema_dir
        self.query_files = query_files
        self.map_table_file = map_table
        self.verbose = verbose

        self.repo = Repo(repo_dir)
        self.version_date = self.repo.commit(commit_hash).committed_date
        self.repo.git.checkout("-f", commit_hash)

        self.init_map_table(map_table)
        # self.map_table
        # self.table_to_vars

        ADD = self.simple_add
        SCHEMA = self.schema_maintenance
        MAP = self.map_maintenance
        MAP_T = self.table_wrapper(MAP)
        APPLICATION = self.application_maintenance
        APPLICATION_T = self.table_wrapper(APPLICATION)
        QUERY = self.query_maintenance
        QUERY_T = self.table_wrapper(QUERY)

        # maps SCOs to the functions that must be used to calculate their impact
        self.impact_map = {
            Sco.ADD_COLUMN :    [ ADD ],
            Sco.DROP_COLUMN:    [ SCHEMA, MAP, APPLICATION, QUERY ],
            Sco.RENAME_COLUMN:  [ SCHEMA, MAP, QUERY ],
            Sco.ADD_TABLE:      [ ADD ],
            Sco.DROP_TABLE:     [ SCHEMA, MAP_T, APPLICATION_T, QUERY_T ],
            Sco.RENAME_TABLE:   [ SCHEMA, MAP_T, QUERY ]
        }

    def table_wrapper(self, f):
        def wrapped(table_name):
            schema_vars = self.table_to_vars[table_name]
            maintenance = 0
            aggregate_lines = {}
            for v in schema_vars:
                res = f(v)
                maintenance += res[0]
                lines = res[1]
                for fn in lines:
                    lines_list = lines[fn]
                    if fn in aggregate_lines:
                        aggregate_lines[fn].extend(lines_list)
                    else:
                        aggregate_lines[fn] = lines_list[:]
            return (maintenance, aggregate_lines)
        wrapped.__name__ = f.__name__ + "_t"
        return wrapped

    def validate_row(self, start, end):
        start_date = self.repo.commit(start.strip()).committed_date
        end_date = self.repo.commit(end.strip()).committed_date
        return start_date <= self.version_date and self.version_date <= end_date

    def init_map_table(self, f):
        schema_var_to_row = {}
        schema_table_to_vars = {}
        with open(f, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            i = 1
            for row in reader:
                if i == 1:
                    i += 1
                    continue
                start_hash = row[0]
                end_hash = row[1]
                if self.validate_row(start_hash, end_hash):
                    schema_var = row[-1].lower()
                    table_name = row[-2].lower()
                    row_data = [i] + row[:len(row)]
                    if schema_var in schema_var_to_row:
                        schema_var_to_row[schema_var].append(row_data)
                    else:
                        schema_var_to_row[schema_var] = [row_data]

                    if table_name in schema_table_to_vars:
                        schema_table_to_vars[table_name].append(schema_var)
                    else:
                        schema_table_to_vars[table_name] = [schema_var]
                i += 1
        self.table_to_vars = schema_table_to_vars
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
                        if (len(lineNums) > 0):
                            print("\t\t" + fn + " lines " + str(lineNums))
            print("Partial impact " + str(sc_impact))
            print('----------------')
            impact += sc_impact
        return impact

# MODULE = 'freight'
# REPO_DIR = '../../b2w-checkout-legado'
# CODE_DIR = REPO_DIR + '/B2wCheckoutWeb/src/main/java/com/b2winc/checkout/'
# SCHEMA_DIR = REPO_DIR + '/Scripts/SCRIPTS_BD/'
# QUERY_FILES = { 'FreightRepository.java', 'CarrierRepository.java' }
# COMMIT_HASH = 'd2569a1e418f35ef117cad4d40b1ac2e2ef4f084'
# MAP_TABLE = '../map_table.csv'

if __name__ == "__main__":
    pass
    # ea = EvolutionAssistant(MODULE,
    #                         REPO_DIR,
    #                         CODE_DIR,
    #                         SCHEMA_DIR,
    #                         QUERY_FILES,
    #                         COMMIT_HASH,
    #                         MAP_TABLE,
    #                         2 )

    # sc1 = SchemaChange(Sco.ADD_COLUMN, "new_column")
    # sc2 = SchemaChange(Sco.DROP_TABLE, "national_freight")
    # sc3 = SchemaChange(Sco.DROP_COLUMN, "contract_type")
    # sc4 = SchemaChange(Sco.RENAME_TABLE, "national_freight")
    # sc5 = SchemaChange(Sco.RENAME_COLUMN, "contract_type")
    # seq = SchemaChangeSequence()
    # seq.add_all(sc1, sc2, sc3, sc4, sc5)
    # print("total impact " + str(ea.get_impact(seq)))

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
    