import requests
import json
from multiprocessing import Pool, Value
from datetime import datetime
from abc import ABC, abstractmethod
import os
import time
from typing import Dict, Optional, List

cache: Dict[str, Dict[str, str]] = {}
counter: 'Value' = Value('i', 0)
last_check: 'Value' = Value('d', time.time())


class RequestStrategy(ABC):
    @abstractmethod
    def make_request(self, url: str) -> Optional[Dict[str, str]]:
        pass


class RequestsStrategy(RequestStrategy):
    def make_request(self, url: str) -> Optional[Dict[str, str]]:
        try:
            response: str = requests.get(url, timeout=5).text
            timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except requests.exceptions.RequestException as e:
            print(f"Could not make request to {url}: {e}")
            return None

        return {"timestamp": timestamp, "response": response}


class PrototypeStrategy(RequestStrategy):
    def make_request(self, url: str) -> Optional[Dict[str, str]]:
        current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if url in cache and (
                datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S") - datetime.strptime(cache[url]["timestamp"],
                                                                                         "%Y-%m-%d %H:%M:%S")).seconds < 3600:
            return cache[url]

        return None


def make_request(strategy: 'RequestStrategy', url: str) -> Optional[Dict[str, str]]:
    with counter.get_lock():
        counter.value += 1
        if time.time() - last_check.value >= 60:
            if counter.value >= 10:
                print("Rate limit exceeded - should fork here")
            last_check.value = time.time()
            counter.value = 0

    response: Optional[Dict[str, str]] = strategy.make_request(url)

    if response is not None:
        cache[url] = response
        with open("cache.txt", "a") as f:
            f.write(json.dumps(cache) + "\n")

    return response


def make_requests(urls: List[str]) -> None:
    with Pool(processes=2) as pool:
        results = []
        for url in urls:
            strategy: 'RequestStrategy' = PrototypeStrategy() if url in cache else RequestsStrategy()
            results.append(pool.apply_async(make_request, (strategy, url)))

        for result in results:
            result.get()

        pool.close()
        pool.join()


if __name__ == '__main__':
    urls: List[str] = [
        "https://www.google.com",
        #"https://www.youtube.com",
        #"https://www.facebook.com",
        #"https://www.instagram.com",
        #"https://www.twitter.com",
        #"http://mike.tuiasi.ro",
        #"https://www.wikipedia.org",
        #"https://www.yahoo.com",
        #"https://www.yandex.com",
        "https://www.whatsapp.com"
    ]

    # Load cache if exists
    try:
        with open("cache.txt", "r") as f:
            cache = json.loads(f.read())
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    make_requests(urls)