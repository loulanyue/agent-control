import hashlib
import time
import os
import secrets

# Crockford Base32 characters for ULID
CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

def generate_ulid(prefix: str = "") -> str:
    """Generate a sortable ULID string with an optional entity prefix (e.g. TASK_01...)"""
    timestamp_ms = int(time.time() * 1000)
    # 48 bits of timestamp
    time_chars = []
    t = timestamp_ms
    for _ in range(10):
        time_chars.append(CROCKFORD_BASE32[t % 32])
        t //= 32
    time_part = "".join(reversed(time_chars))

    # 80 bits of randomness
    random_bytes = os.urandom(10)
    rand_int = int.from_bytes(random_bytes, byteorder="big")
    rand_chars = []
    for _ in range(16):
        rand_chars.append(CROCKFORD_BASE32[rand_int % 32])
        rand_int //= 32
    rand_part = "".join(reversed(rand_chars))

    ulid_str = time_part + rand_part
    if prefix:
        return f"{prefix}_{ulid_str}"
    return ulid_str

def hash_token(token: str) -> str:
    """Hash API client token using SHA-256"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def generate_token() -> tuple[str, str]:
    """Generate a secure bearer token and return (raw_token, sha256_hash)"""
    token = "ac_" + secrets.token_urlsafe(32)
    return token, hash_token(token)
