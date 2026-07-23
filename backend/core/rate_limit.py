"""Rate limiting configuration."""

from backend.core.config import get_settings
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=[get_settings().rate_limit])
