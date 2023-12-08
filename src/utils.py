import time


def timed(debug):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if debug:
                start = time.time()
                res = func(*args, **kwargs)
                end = time.time()
                print(f'{func.__name__}: executed in {end - start:.2f}s')
            else:
                res = func(*args, **kwargs)
            return res
        return wrapper
    return decorator
