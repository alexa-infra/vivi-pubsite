def _Consume(text, index, what):
    index = _SkipWhitespace(text, index)
    assert text[index:index+len(what)] == what, \
            "Expected to read '{0}' but read '{1}' instead" \
            .format(what, text[index:index+len(what)])
    return index + len(what)

def _ParseIdentifier(text, index):
    return _ParseString(text, index, False)

def _IsWhitespace(c):
    return c == ' ' or c == '\t' or c == '\n' or c == '\r'

def _SkipWhitespace(text, index):
    while True:
        if index >= len(text):
            return -1

        c = text[index]

        if _IsWhitespace(c):
            index += 1
            continue
        elif c == '/':
            index = _SkipComment(text, index+1)
            continue
        break
    return index

def _SkipRestOfLine(text, index):
    prevc = index == 0 and '\0' or text[index-1]
    while True:
        if index >= len(text):
            return -1
        c = text[index]
        index += 1
        if c == '\n':
            break
        if prevc == '\r' and c == '\n':
            break
        prevc = c
    return index

def _SkipToEndOfComment(text, index):
    prevc = index == 0 and '\0' or text[index-1]
    while True:
        if index >= len(text):
            return -1
        c = text[index]
        index += 1
        if prevc == '*' and c == '/':
            break
        prevc = c
    return index

def _SkipComment(text, index):
    if index >= len(text):
        return -1
    c = text[index]
    assert c == '/' or c == '*', "Wrong syntax of comment '{0}'".format(c)
    if c == '/':
        return _SkipRestOfLine(text, index+1)
    elif c == '*':
        return _SkipToEndOfComment(text, index+1)

import string
ident_chars = set(string.ascii_letters + string.digits + '_' + '+-')

def _IsIdentifier(c):
    return c in ident_chars

def _Peek(text, index):
    index = _SkipWhitespace(text, index)
    if index == -1 or (index == (len(text)-1)):
        return None
    return text[index]

def _ParseString(text, index, allowSpacesWithoutQuotes):
    index = _SkipWhitespace(text, index)

    result = list()

    hasQuotes = True
    if text[index] != '\"':
        index -= 1
        hasQuotes = False

    while True:
        index += 1
        c = text[index]

        if not hasQuotes and not _IsIdentifier(c):
            break
        if c == '\"':
            index += 1
            break
        elif c == '\\':
            index += 1
            d = text[index]

            if d == '\"':
                result.append(d)
            else:
                result.append(c)
                result.append(d)

        else:
            result.append(c)

    s = ''.join(result)

    return (index, s)

def _ParseNumber (text, index):
    index = _SkipWhitespace(text, index)

    value = list()
    while True:
        if index == len(text):
            break
        if _IsWhitespace(text[index]) or text[index] == ',' or text[index] == ']' or text[index] == '}':
            break
        else:
            value.append(text[index])
        index += 1

    value = ''.join(value)

    try:
        return (index, int(value))
    except ValueError:
        return (index, float(value))

def _ParseMap(text, index):
    result = {}

    while True:
        index = _SkipWhitespace(text, index)
        if index == -1:
            break
        elif text[index] == '}':
            index = _Consume(text, index, '}')
            break

        (index, key) = _ParseString(text, index, False)
        index = _Consume(text, index, ':')
        (index, value) = _Parse(text, index)
        result[key] = value

        if _Peek(text, index) == ',':
            index = _Consume(text, index, ',')
        if index == len(text)-1:
            break

    return (index, result)

def _ParseList(text, index):
    result = []

    while True:
        index = _SkipWhitespace(text, index)
        if text[index] == ']':
            index += 1
            break

        (index, value) = _Parse(text, index)
        result.append(value)

        if _Peek(text, index) == ',':
            index = _Consume(text, index, ',')

    return (index, result)

def _Parse(text, index):
    index = _SkipWhitespace(text, index)
    c = text[index]
    value = None
    if c == 't':
        index = _Consume(text, index, 'true')
        value = True
    elif c == 'f':
        index = _Consume(text, index, 'false')
        value = False
    elif c == 'n':
        index = _Consume(text, index, 'null')
        value = None
    elif c == '{':
        (index, value) = _ParseMap(text, index+1)
    elif c == '[':
        (index, value) = _ParseList(text, index+1)
    elif c == '\"':
        (index, value) = _ParseString(text, index, False)
    else:
        try:
            (index, value) = _ParseNumber(text, index)
        except ValueError:
            (index, value) = _ParseString(text, index, True)
    return (index, value)

def loads(text):
    return _ParseMap(text, 0)[1]
