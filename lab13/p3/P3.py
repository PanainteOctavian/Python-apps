from itertools import zip_longest
from typing import List


def process_numbers(numbers: List[int]) -> int:
    filtered: List[int] = list(filter(lambda x: x >= 5, numbers))
    pairs: List[int] = list(zip_longest(*[iter(filtered)] * 2))
    multiplied: List[int] = [a * b for a, b in pairs if b is not None]
    result: int = sum(multiplied)
    return result


if __name__ == '__main__':
    numbers: List[int] = [1, 21, 75, 39, 7, 2, 35, 3, 31, 7, 8]
    print(process_numbers(numbers))
