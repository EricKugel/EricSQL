from clauses import *
from functions import *

import pandas as pd

from table import Table

from engine import flatten_tokens

function_factory = lambda f: eval("".join(map(str.capitalize, f[0].value.split(" "))))(f[1:])

class Statement():
    def __init__(self, tokens):
        self.tokens = tokens
        self.clauses = []

class Select(Statement):
    def execute(self, database):
        from_clause = None
        for clause in self.clauses:
            if isinstance(clause, From):
                from_clause = clause
                break
        else:
            raise Exception("Select statements require From clauses")

        table = from_clause.get_table(database)

        if self.tokens[0].type == "function":
            function_outputs = []
            for i in range(len(self.tokens) // 2):
                if self.tokens[i * 2].type != "function":
                    raise Exception("Columns and aggregate functions can't be mixed without a GROUP BY clause")

                func = function_factory(self.tokens[i * 2:i * 2 + 2])
                function_outputs.append(func.execute(table))
            return function_outputs if len(function_outputs) > 1 else function_outputs[0]

        columns = self.tokens[0]
        if self.tokens[0].type == "operator" and columns.value == "*":
            selected_columns = table.columns
        else:
            selected_columns = list(map(lambda t: t.value, flatten_tokens(self.tokens)))
            selected_columns = table.search_for_columns(selected_columns)

        selected_schema = []
        for scheme in table.schema:
            if scheme[0] in selected_columns:
                selected_schema.append(scheme)
        
        return Table.create_from_table("result", selected_schema, table.data[selected_columns])

class SelectDistinct(Statement):
    def execute(self, database):
        new_statement = Select(self.tokens)
        new_statement.clauses = self.clauses
        result = new_statement.execute(database)
        return Table.create_from_table("result", schema = result.schema, data = result.data.drop_duplicates())
    
class InsertInto(Statement):
    def execute(self, database):
        table = database.get_table(self.tokens[0].value)

        columns = table.columns
        if len(self.tokens) > 1:
            columns = list(map(lambda t: t.value, flatten_tokens(self.tokens[1:])))
            columns = table.search_for_columns(columns)

        values_clause = None
        for clause in self.clauses:
            if isinstance(clause, Values):
                values_clause = clause
                break
        else:
            raise Exception("INSERT INTO statements require a Values clause")
        
        rows = values_clause.get_rows(columns)

        new_df = pd.DataFrame(rows, columns=columns)
        table.data = pd.concat((table.data, new_df))