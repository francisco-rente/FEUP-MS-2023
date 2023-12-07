import time


def timed(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__}: executed in {end - start:.2f}s")
        return res

    return wrapper
