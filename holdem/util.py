import functools
from time import time
import logging


class Timeit:
    def __init__(self, message=None):
        self.logger = logging.getLogger(__name__)
        self.message = message

    def __call__(self, func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            ts = time()
            result = func(*args, **kwargs)
            te = time()
            if self.message is not None:
                self.logger.info(f'{self.message}: {(te - ts):.2f} sec')
            else:
                message = f'func: {func.__module__}.{func.__name__}(*{args}, **{kwargs}) took {(te - ts):.2f} sec'
                self.logger.info(message)
            return result

        return wrap
