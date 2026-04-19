from slowapi import Limiter
from slowapi.util import get_remote_address

# In-memory limiter keyed by client IP.
# For multi-instance deployments, swap the storage_uri to a Redis URL:
#   Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")
limiter = Limiter(key_func=get_remote_address)
