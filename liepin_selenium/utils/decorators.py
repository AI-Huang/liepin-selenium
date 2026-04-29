"""
Useful decorators for spider operations
"""

import functools
import time

from .logger import setup_logger


def retry(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Retry decorator with exponential backoff

    Args:
        max_retries (int): Maximum number of retries
        delay (int): Initial delay in seconds
        backoff (int): Multiplier for exponential backoff
        exceptions (tuple): Exception types to catch

    Returns:
        function: Decorated function
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = setup_logger(func.__name__)
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    logger.warning(f"Attempt {retries} failed: {str(e)}")

                    if retries < max_retries:
                        logger.info(f"Retrying in {current_delay} seconds...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed")
                        raise

            return None

        return wrapper

    return decorator


def timer(func):
    """
    Timer decorator to measure function execution time

    Args:
        func: Function to decorate

    Returns:
        function: Decorated function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = setup_logger(func.__name__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
        finally:
            elapsed_time = time.time() - start_time
            logger.info(
                f"Function {func.__name__} completed in {elapsed_time:.2f} seconds"
            )

        return result

    return wrapper
