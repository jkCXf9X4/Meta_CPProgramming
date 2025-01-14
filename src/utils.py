

from itertools import groupby


def split_list(l, obj):
    result = []

    # Group elements based on whether they are not the split value
    for key, group in groupby(l, lambda x: x != obj):
        if key:
            result.append(list(group))

    return result

def split_first(l, obj):
    for i, j in enumerate(l):
        if j == obj:
            return l[:i], l[i:]
        
def split_last(l:list, obj):
    l = l.copy()
    l.reverse()

    for i, j in enumerate(l):
        if j == obj:
            return l[:i], l[i:]
        

def split_brace(tokens):
    first = None
    last = None
    index = 0
    for i, obj in enumerate(tokens):
        if obj == "{":
            index += 1
            if index == 1:
                first = i
        if obj == "}":
            if index == 1:
                last = i
            index -= 1


    if first and last:
        return tokens[:first], tokens[first+1:last], tokens[last+1:]

    raise Exception("Opening and closing bracket not found")