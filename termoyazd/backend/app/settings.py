"""Deployment settings. Production never permits wildcard origins or hosts."""
from dataclasses import dataclass
from urllib.parse import urlsplit
import os


def positive_int(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if value <= 0:
        raise ValueError(f'{name} must be positive')
    return value


@dataclass(frozen=True)
class Settings:
    production: bool
    origins: tuple[str, ...]
    hosts: tuple[str, ...]
    max_body_bytes: int = 16384
    max_calculations: int = 2

    @classmethod
    def from_env(cls) -> 'Settings':
        environment = os.getenv('TERMOYAZD_ENV', 'development')
        if environment not in ('development', 'production'):
            raise ValueError('TERMOYAZD_ENV must be development or production')
        production = environment == 'production'
        origins = tuple(s.strip() for s in os.getenv('TERMOYAZD_CORS_ORIGINS', '' if production else 'http://localhost:5173,http://127.0.0.1:5173').split(',') if s.strip())
        for origin in origins:
            parsed = urlsplit(origin)
            if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment or '*' in origin:
                raise ValueError('CORS origins must be exact origins without paths, credentials or wildcards')
            if production and parsed.scheme != 'https':
                raise ValueError('Production CORS origins must use HTTPS')
        default_hosts = os.getenv('RENDER_EXTERNAL_HOSTNAME', '') if production else 'localhost,127.0.0.1,testserver'
        hosts = tuple(s.strip() for s in os.getenv('TERMOYAZD_ALLOWED_HOSTS', default_hosts).split(',') if s.strip())
        if not hosts or any('*' in h or '/' in h or ':' in h for h in hosts):
            raise ValueError('Configure exact TERMOYAZD_ALLOWED_HOSTS (hostnames only)')
        return cls(production, origins, hosts,
                   positive_int('TERMOYAZD_MAX_BODY_BYTES', 16384),
                   positive_int('TERMOYAZD_MAX_CALCULATIONS', 2))
