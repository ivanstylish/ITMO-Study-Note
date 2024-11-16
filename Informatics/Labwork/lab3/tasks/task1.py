import re

def solve(string):
    """ Возвращает количество смайликов вида ;<{= в строке
    407959 % 6 = 1 => Глаза: ;
    407959 % 4 = 3 => Нос: <{
    407959 % 8 = 7 => Рот: =
    """
    pattern = r';<{='
    return len(re.findall(pattern, string))

print(solve(input()))