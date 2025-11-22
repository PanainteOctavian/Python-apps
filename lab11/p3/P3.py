from threading import Thread, Lock
from queue import Queue
from typing import List, Callable, Tuple, Dict, Any, Iterable, Optional


class ThreadPool:
    def __init__(self, num_threads: int) -> None:
        # Coada pentru taskuri - aici se pun functiile care trebuie executate
        self.tasks: Queue = Queue()
        # Lista cu toate thread-urile create
        self.threads: List[Thread] = []
        # Lock pentru sincronizare - sa nu se suprapuna executiile
        self.lock: Lock = Lock()

        # Creaza si porneste num_threads thread-uri worker
        for _ in range(num_threads):
            thread: Thread = Thread(target=self._worker)
            thread.start()  # Porneste thread-ul
            self.threads.append(thread)  # Il adauga in lista

    def _worker(self) -> None:
        # Functia care ruleaza pe fiecare thread worker
        while True:
            # Declara variabilele pentru functie, argumente si keyword arguments
            func: Optional[Callable[..., Any]]
            args: Tuple[Any, ...]
            kwargs: Dict[str, Any]

            # Ia un task din coada (se blocheaza pana gaseste unul)
            func, args, kwargs = self.tasks.get()

            # Daca func este None, inseamna ca thread-ul trebuie sa se opreasca
            if func is None:
                break

            # Executa functia cu lock-ul activat pentru sincronizare
            with self.lock:
                func(*args, **kwargs)

            # Marcheaza taskul ca fiind terminat
            self.tasks.task_done()

    def map(self, func: Callable[..., Any], iterable: Iterable[Any]) -> None:
        # Aplica functia func pe fiecare element din iterable
        # Pune fiecare apel de functie in coada ca task
        for item in iterable:
            self.tasks.put((func, (item,), {}))

    def join(self) -> None:
        # Asteapta ca toate taskurile din coada sa fie terminate
        self.tasks.join()

    def terminate(self) -> None:
        # Opreste toate thread-urile worker
        # Pune cate un None in coada pentru fiecare thread (semnal de oprire)
        for _ in self.threads:
            self.tasks.put((None, (), {}))

        # Asteapta ca toate thread-urile sa se termine
        for thread in self.threads:
            thread.join()

    # Metode pentru context manager (pentru a folosi cu "with")
    def __enter__(self) -> 'ThreadPool':
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Cand iese din blocul "with", opreste thread-urile
        self.terminate()

if __name__ == "__main__":
    # Creaza un pool cu 6 thread-uri worker
    with ThreadPool(6) as pool:
        # Aplica functia print pe numerele de la 0 la 19
        # Vor fi impartite intre cele 6 thread-uri
        pool.map(print, range(20))
        # Asteapta ca toate sa se termine
        pool.join()