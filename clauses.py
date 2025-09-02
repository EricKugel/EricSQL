from engine import *
from helpers import flatten_tokens

from table import Table

class Clause():
    snoop = False
    def __init__(self, tokens):
        self.tokens = tokens

    def dud(self, result):
        return result

    def stop_snooping(self):
        self.snoop_callback = self.dud

# TODO: Multiple sources (i.e. more than one table)
class From(Clause):
    def get_table(self, database):
        from query import create_queries
        if self.tokens[0].type == "group":
            recursive_query = create_queries(self.tokens[0].value, database)[0]
            return recursive_query.execute()
        return database.get_table(self.tokens[0].value)
    
class OrderBy(Clause):
    snoop = True
    def snoop_callback(self, result):
        ascending = []
        columns = []
        in_queue = 0

        for token in flatten_tokens(self.tokens):
            if token.type == "operator" and token.value in ["asc", "desc"]:
                ascending.extend([True] * in_queue if token.value == "asc" else [False] * in_queue)
                in_queue = 0
            else:
                columns.append(token.value)
                in_queue += 1

        ascending.extend([True] * in_queue)
        found_columns = result.search_for_columns(columns)

        sorted_data = result.data.sort_values(by = found_columns, ascending = ascending)
        return Table.create_from_table("result", result.columns, sorted_data)
    
class Values(Clause):
    def get_rows(self, columns):
        values = []
        for token in self.tokens:
            if token.type == "group":
                child_tokens = flatten_tokens(token.value)
                values.extend(list(map(lambda t: t.value, child_tokens)))
            elif token.type == "special":
                pass
            else:
                values.append(token.value)
        
        rows = []
        for i in range(0, len(values), (length := len(columns))):
            rows.append(values[i:i + length])
        return rows
    
class Where(Clause):
    def snoop_callback(self, result):
        result.data = result.data[self.find(result)]
        return result

    def find(self, result):
        tester = create_function(self.tokens, result, False)
        return result.data.apply(lambda row: tester(row.to_dict()), axis=1)