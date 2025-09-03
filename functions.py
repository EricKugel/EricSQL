from helpers import flatten_tokens

aggregate_functions = ["max", "min", "count"]

class Function():
    def __init__(self, tokens):
        if len(tokens) == 1 and tokens[0].type == "group":
            self.tokens = tokens[0].value
        else:
            self.tokens = tokens

class Count(Function):
    args = 1
    def execute(self, table):
        if token.type != "operator" or token.value != "*":
            # TODO: The exceptions write themselves
            raise Exception("I'm really sorry but functions like COUNT with a variable number of arguments are soooo much work to implement. Would you mind using syntax like this instead, with just an asterisk? SELECT COUNT(*) FROM (SELECT DISTINCT CustomerID FROM Customers)")

        distinct = self.tokens[0].type == "operator" and self.tokens[0].value == "distinct"
        if distinct:
            self.tokens = self.tokens[1:]

        columns = self.tokens[0]
        if self.tokens[0].type == "operator" and columns.value == "*":
            selected_columns = table.columns
        else:
            selected_columns = list(map(lambda t: t.value, flatten_tokens(self.tokens)))
            selected_columns = table.search_for_columns(selected_columns)

        df = table.data[selected_columns]
        if distinct:
            df = df.drop_duplicates()
        
        return len(df)
    
class Min(Function):
    args = -1
    def execute(self, table):
        pass

# TODO: Expressions
# TODO: What is numeric?
class Sum(Function):
    args = 1
    def execute(self, table):
        scheme, column = table.find_column(self.tokens[0].value)
        if scheme[1] not in ["int"]:
            raise Exception(f"Column {column} is not numeric")
        column = table.data[column].dropna()
        return sum(column)