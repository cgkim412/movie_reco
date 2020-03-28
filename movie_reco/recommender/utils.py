import time

def stopwatch(func):
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        t1 = time.perf_counter()
        print(f"Runtime of {func.__name__.upper()}: {t1-t0} seconds")
        return result
    return wrapper