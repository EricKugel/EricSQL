# operators = ["distinct", "and", "or", "not", "like", "in", "between", "=", ">", "<", ">=", "<=", "!=", "*", "asc", "desc"]

def like_function(a):
    pass

def in_function(a, b):
    pass

def between_function(a, b):
    pass

lambdas = {
    "distinct": Exception("Invalid use of distinct"), # TODO: how to raise an expection? Well, I suppose trying to perform math on an exception will break...
    "asc": Exception("Invalid use of asc"), # TODO: how to raise an expection? Well, I suppose trying to perform math on an exception will break...
    "desc": Exception("Invalid use of desc"), # TODO: how to raise an expection? Well, I suppose trying to perform math on an exception will break...
    "not": lambda a: not a,
    "like": like_function,
    "in": in_function,
    "between": between_function,
    "=": lambda a, b: a == b
}

for operator in ["+", "-", "*", "/", "//", "%", "<", ">", "<=", ">=", "!=", "and", "or"]:
    lambdas[operator] = eval("lambda a, b: a " + operator + " b")

precedence = {"**": 10,"~": 9.5,"!": 9.5,"*": 9,"/": 9,"//": 9,"%": 9,"+": 8,"-": 8,"<": 7,"<=": 7,">": 7,">=": 7,"=": 7,"!=": 7, "and": 6, "or": 5}