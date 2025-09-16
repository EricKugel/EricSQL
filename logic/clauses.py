from logic.engine import *
from logic.helpers import flatten_tokens

from logic.table import Table

# This is mostly just for ease of isinstance
class Clause():
    snoop = False
    def __init__(self, tokens):
        self.tokens = tokens

    # For use with stop_snooping
    def dud(self, result):
        return result

    # If a statement greedily consumes a snooping clause, 
    # it should tell the clause to stop snooping
    def stop_snooping(self):
        self.snoop_callback = self.dud

# TODO: Multiple sources (i.e. more than one table)
class From(Clause):
    def get_table(self, database):
        # To avoid circular imports
        from logic.query import create_queries
        # It's possible (and sometimes pretty handy) in SQL to have recursive SELECT statements.
        if self.tokens[0].type == "group":
            recursive_query = create_queries(self.tokens[0].value, database)[0]
            return recursive_query.execute()
        # Simple case, just get a plain table
        return database.get_table(self.tokens[0].value)
    
class OrderBy(Clause):
    snoop = True
    def snoop_callback(self, result):
        ascending = []
        columns = []
        in_queue = 0

        # col1 col2 asc col3 desc
        # So a queue is necessary to hold cols until the direction is established
        for token in flatten_tokens(self.tokens):
            if token.type == "operator" and token.value in ["asc", "desc"]:
                ascending.extend([True] * in_queue if token.value == "asc" else [False] * in_queue)
                in_queue = 0
            else:
                columns.append(token.value)
                in_queue += 1

        ascending.extend([True] * in_queue)
        found_columns = result.search_for_columns(columns)

        # Pandas makes some of this a little too easy. Eventually I'll rewrite this in C (no I won't)
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
        
        # At the end of the day this is easiest for everybody--don't bother with parentheses at all.
        if len(values) % len(columns) != 0:
            raise Exception("Wrong number of values in INSERT INTO statement")

        rows = []
        for i in range(0, len(values), (length := len(columns))):
            rows.append(values[i:i + length])
        return rows
    
class Where(Clause):
    # In the case where Where runs by itself
    def snoop_callback(self, result):
        result.data = result.data[self.find(result)]
        return result

    # Creates a function using the expression passed in, applies this function to every row
    # Returns a list of row indexes which are targeted by the expression.
    def find(self, result):
        tester = create_function(self.tokens, result, False)
        return result.data.apply(lambda row: tester(row.to_dict()), axis=1)