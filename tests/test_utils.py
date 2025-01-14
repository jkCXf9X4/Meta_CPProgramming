
from src.utils import split_brace

# def test_split_list():

#     l = [1, 2, 3, 4, 5, 6]
#     split = split_list(l, 3)
#     print(split)


    


def test_brace_split():
    l = ['int', 'get_int', '(', ')', '{', '\n', 'return', 'b', ';', '\n', '}']
    
    before, inside, after = split_brace(l)

    assert before == ['int', 'get_int', '(', ')']
    assert inside == ['\n', 'return', 'b', ';', '\n']
    assert after == []
