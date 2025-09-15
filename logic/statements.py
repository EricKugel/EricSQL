from logic.clauses import *
from logic.functions import *

import pandas as pd

from logic.table import Table

import logic.helpers
import logic.engine

function_factory = lambda f: eval("".join(map(str.capitalize, f[0].value.split(" "))))(f[1:])

class Statement():
    def __init__(self, tokens):
        self.tokens = tokens
        self.clauses = []

    def find_clause(self, clause_type, optional=False):
        for clause in self.clauses:
            if isinstance(clause, clause_type):
                return clause
        if not optional:
            raise Exception(f"{self.__class__.__name__} statements require a {clause_type.__name__} clause")
        return None

class Select(Statement):
    def execute(self, database):
        from_clause = self.find_clause(From)
        where_clause = self.find_clause(Where, optional=True)
        table = from_clause.get_table(database)

        if self.tokens[0].type == "operator" and self.tokens[0].value == "*":
            if where_clause:
                return Table.create_from_table("result", table.columns, table.data[:][where_clause.find(table)])
            return Table.create_from_table("result", table.columns, table.data[:])

        aggregate = logic.engine.check_for_aggregate(self.tokens)
        columns = logic.helpers.separate_by_commas(self.tokens)
        if aggregate:
            for column in columns:
                if not logic.engine.check_for_aggregate(column):
                    # TODO Check for GROUP BY
                    raise Exception("Columns and aggregate functions can't be mixed without a GROUP BY clause")
                
        aliases = []
        for i, column in enumerate(columns):
            alias_and_cut = logic.helpers.check_for_alias(column, table)
            if alias_and_cut:
                alias, cut = alias_and_cut
                aliases.append(alias)
                if cut:
                    columns[i] = column[:-2]
            else:
                aliases.append(f"column{i}")
            
        output_functions = [logic.engine.create_function(column, table, aggregate) for column in columns]

        if aggregate:
            data = [[output_function({}) for output_function in output_functions]]
        else:
            data = []
            for _, row in table.data.iterrows():
                data.append([output_function(row.to_dict()) for output_function in output_functions])
        data = pd.DataFrame(data, columns=aliases)

        if where_clause:
            search_table_data = pd.concat([table.data, data], axis = 1)
            search_table = Table.create_from_table("search", table.columns + aliases, search_table_data)
            selected_rows = where_clause.find(search_table)
            return Table.create_from_table("result", aliases, data[selected_rows])
        return Table.create_from_table("result", aliases, data)

class SelectDistinct(Statement):
    def execute(self, database):
        new_statement = Select(self.tokens)
        new_statement.clauses = self.clauses
        result = new_statement.execute(database)
        return Table.create_from_table("result", result.columns, result.data.drop_duplicates())
    
class InsertInto(Statement):
    def execute(self, database):
        table = database.get_table(self.tokens[0].value)

        columns = table.columns
        if len(self.tokens) > 1:
            columns = list(map(lambda t: t.value, flatten_tokens(self.tokens[1:])))
            columns = table.search_for_columns(columns)

        values_clause = self.find_clause(Values)
        rows = values_clause.get_rows(columns)

        new_df = pd.DataFrame(rows, columns=columns)
        table.data = pd.concat((table.data, new_df))

class Delete(Statement):
    def execute(self, database):
        from_clause = self.find_clause(From)
        table = from_clause.get_table(database)
    
        where_clause = self.find_clause(Where, optional=True)
        if not where_clause:
            table.data = table.data.head(0)
        else:
            rows = where_clause.find(table)
            table.data = table.data[~rows]

class Backup(Statement):
    def execute(self, database):
        database.write_out()