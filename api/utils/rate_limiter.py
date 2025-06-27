from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter instance # Initialize limiter
limiter = Limiter(key_func=get_remote_address)
