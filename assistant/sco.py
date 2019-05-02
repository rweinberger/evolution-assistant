from enum import Enum

class Sco(Enum):
    ADD_COLUMN          = "ADD_COLUMN"
    DROP_COLUMN         = "DROP_COLUMN"
    RENAME_COLUMN       = "RENAME_COLUMN"
    ADD_TABLE           = "ADD_TABLE"
    DROP_TABLE          = "DROP_TABLE"
    RENAME_TABLE        = "RENAME_TABLE"
    CHANGE_DATA_TYPE    = "CHANGE_DATA_TYPE"

class SchemaChange():
    def __init__(self, operator, table, operand):
        self.operator = operator
        self.table = table
        self.operand = operand

    def __str__(self):
        if type(self.operator) is str:
            return self.operator + ", " + self.operand
        else:
            return self.operator.name + ", " + self.operand

    def get_operator(self):
        return Sco(self.operator) if type(self.operator) is str else self.operator

    def get_table(self):
        return self.table.upper()

    def get_operand(self):
        return self.operand.lower()

class SchemaChangeSequence():
    def __init__(self):
        self.changes = []

    def __len__(self):
        return len(self.changes)

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

    def add_all(self, *changes):
        self.changes.extend(changes)