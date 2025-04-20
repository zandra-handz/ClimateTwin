import time
import logging

 
import functools
from inspect import signature

logger = logging.getLogger(__name__)

def log_view_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Figure out if this is a method or a function
        sig = signature(func)
        is_method = 'self' in sig.parameters  # Corrected line

        start = time.time()
        response = func(*args, **kwargs)
        end = time.time()

        if is_method:
            logger.info(f"{args[0].__class__.__name__}.{func.__name__} took {end - start:.3f}s")
        else:
            logger.info(f"{func.__name__} took {end - start:.3f}s")
        return response
    return wrapper

class TimedAPIView:
    def dispatch(self, request, *args, **kwargs):
        start = time.time()
        response = super().dispatch(request, *args, **kwargs)
        duration = time.time() - start
        logger.info(f"{self.__class__.__name__} took {duration:.3f}s")
        return response