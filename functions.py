from helpers import flatten_tokens

aggregate_functions = ["max", "min", "count"]

class Function():
    pass

class Count(Function):
    args = 1
    def execute(token_value, table):
        if token_value != "*":
            # TODO: The exceptions write themselves
            raise Exception("I'm really sorry but functions like COUNT with a variable number of arguments are soooo much work to implement. Would you mind using syntax like this instead, with just an asterisk? SELECT COUNT(*) FROM (SELECT DISTINCT CustomerID FROM Customers)")
        
        return len(table.data)
    
class Min(Function):
    args = -1
    def execute(row, table):
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