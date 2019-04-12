from enum import Enum

class Sco(Enum):
    ADD_COLUMN      = 1
    DROP_COLUMN     = 2
    RENAME_COLUMN   = 3
    ADD_TABLE       = 4
    DROP_TABLE      = 5
    RENAME_TABLE    = 6

class SchemaChange():
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __str__(self):
        return self.operator.name + ", " + self.operand

    def get_operator(self):
        return self.operator

    def get_operand(self):
        return self.operand

class SchemaChangeSequence():
    def __init__(self, changes = []):
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

    def add_all(self, *changes):
        self.changes.extend(changes)