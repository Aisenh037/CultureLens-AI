from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# In-memory storage is per-process. For multiple workers or instances, point
# `storage_uri` at Redis so limits are shared.
limiter = Limiter(key_func=get_remote_address, enabled=settings.RATE_LIMIT_ENABLED)
