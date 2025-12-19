import asyncio
import hashlib
from app.services.token import JwtService


async def main():
    service = JwtService("access", "abc", "HS256", 15)
    payload = {"sub": "1", "email": "mail@blocksdev.pro"}

    token_str = service.encode_token(payload)
    print(token_str)
    token = service.decode_token(token_str)

    token_hash = hashlib.sha256(f"{token_str}".encode()).hexdigest()
    legacy_hash = hashlib.sha256(
        f"{token_str}-{token.sub}-{token.iat}".encode()
    ).hexdigest()

    print(f"Token hash and Legacy hash same > {token_hash == legacy_hash}")
    print(f"Token hash > {token_hash}")
    print(f"Legacy hash > {legacy_hash}")


if __name__ == "__main__":
    asyncio.run(main())
