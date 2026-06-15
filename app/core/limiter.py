from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings
from limits import parse
from limits.strategies import MovingWindowRateLimiter
from limits.storage import storage_from_string

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)

_email_storage = storage_from_string(settings.REDIS_URL)
email_limiter = MovingWindowRateLimiter(_email_storage)
EMAIL_LOGIN_LIMIT = parse("5/minute")