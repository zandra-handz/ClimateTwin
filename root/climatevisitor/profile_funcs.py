import time
import logging

logger = logging.getLogger(__name__)

def log_view_time(func):
    def wrapper(self, request, *args, **kwargs):
        start = time.time()
        response = func(self, request, *args, **kwargs)
        end = time.time()
        logger.info(f"{self.__class__.__name__}.{func.__name__} took {end - start:.3f}s")
        return response
    return wrapper



class TimedAPIView:
    def dispatch(self, request, *args, **kwargs):
        start = time.time()
        response = super().dispatch(request, *args, **kwargs)
        duration = time.time() - start
        logger.info(f"{self.__class__.__name__} took {duration:.3f}s")
        return response