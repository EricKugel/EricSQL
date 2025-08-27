# I hate having this here but circular imports are KILLING ME

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