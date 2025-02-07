import logging
import re

def setup_logger(name):
    """
    Creates a logger instance with consistent formatting.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger

def validate_api_response(response, keys):
    """
    Checks if the response contains all the required keys.
    """
    return all(key in response for key in keys)

def handle_errors(func):
    """
    Decorator to handle errors gracefully.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            return None
    return wrapper

def format_currency(value, currency="€"):
    """
    Formats a float or integer as a currency string.
    """
    return f"{currency}{value:,.2f}"

def sanitize_text(text):
    """
    Removes HTML tags and trims text.
    """
    return re.sub(r'<.*?>', '', text).strip()
