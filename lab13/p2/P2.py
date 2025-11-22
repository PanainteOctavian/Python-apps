import more_itertools as mit
import re
from typing import List, Dict, Any, Generator, Tuple


def map_func(text: str) -> Generator[Tuple[str, str], None, None]:
    words = re.findall(r'\b\w+\b', text)
    return ((word[0], word) for word in words)


def reduce_func(words: List[str]) -> List[str]:
    return sorted(words)


def sort_words(text: str) -> Dict[chr, list[Any]]:
    return dict(mit.map_reduce(map_func(text), keyfunc=lambda x: x[0], valuefunc=lambda x: x[1], reducefunc=reduce_func))


if __name__ == '__main__':
    text: str = "Starting from the example with map_reduce from the more_itertools module"
    print(sort_words(text))
