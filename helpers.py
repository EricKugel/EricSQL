# I hate having these here but circular imports are KILLING ME

def flatten_tokens(tokens):
    if not isinstance(tokens, list) and tokens.type != "group":
        return [tokens]
    elif not isinstance(tokens, list):
        tokens = [tokens]

    all_tokens = []
    for token in tokens:
        if token.type == "group":
            all_tokens.extend(flatten_tokens(token.value))
        elif token.type == "special":
            continue
        else:
            all_tokens.append(token)

    return all_tokens

def separate_by_commas(tokens):
    groups = []
    group = []
    for token in tokens:
        if token.type == "special":
            groups.append(group)
            group = []
        else:
            group.append(token)
    groups.append(group)

    return groups

def check_for_alias(tokens, table):
    if len(tokens) > 1 and tokens[-2].type == "operator" and tokens[-2].value == "as":
        return tokens[-1].value, True
    elif len(tokens) == 1 and tokens[0].type in {"unknown", "string", "number"}:
        if tokens[0].type == "unknown":
            return table.find_column(tokens[0].value)[1], False
        return tokens[0].value, False