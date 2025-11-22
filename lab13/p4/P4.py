from math import isqrt
from typing import List, Callable

def is_prime(n: int) -> bool:
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    limit: int = isqrt(n)
    for i in range(5, limit + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True


class Automaton:
    def __init__(self, lst: List[int]) -> None:
        self.lst: List[int] = lst
        self.states: List[Callable[[], None]] = [lambda: list(filter(is_prime, self.lst)),
                                                 lambda: list(filter(lambda x: x % 2 != 0, self.lst)),
                                                 lambda: list(filter(lambda x: x <= 50, self.lst)),
                                                 lambda: print(self.lst)]
        self.state: Callable = self.states.pop(0)

    def process(self) -> None:
        while self.states:
            self.lst: None = self.state()
            self.state = self.states.pop(0)
        self.state()


if __name__ == '__main__':
    a: Automaton = Automaton([4, 2, 51, 53, 49, 50, 52, 100])
    a.process()
