import asyncio
from typing import List, Coroutine


async def calculate_sum(n: int) -> int:
    return sum(i for i in range(1, n + 1))


async def worker(name: str, queue: asyncio.Queue) -> None:
    while queue.qsize() > 0:
        n: int = await queue.get()
        result: int = await calculate_sum(n)
        print(f"Corutina {name}: Suma numerelor de la 0 la {n} este {result}.")
        queue.task_done()


async def main():
    queue: asyncio.Queue = asyncio.Queue()

    values_of_n: List[int] = [10, 20, 30, 40]

    for n in values_of_n:
        queue.put_nowait(n)

    workers: List[Coroutine[str, asyncio.Queue, None]] = [worker(f"worker {i}", queue) for i in range(1, 5)]

    await asyncio.gather(*workers)

    await queue.join()


if __name__ == "__main__":
    asyncio.run(main())
