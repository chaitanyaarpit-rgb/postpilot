import os
import base64
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

_key = os.getenv("ENCRYPTION_KEY")
if not _key:
    # Auto-generate and warn (dev only)
    _key = Fernet.generate_key().decode()
    print(f"WARNING: No ENCRYPTION_KEY set. Using ephemeral key. Set in .env for production.")

fernet = Fernet(_key.encode() if isinstance(_key, str) else _key)


def encrypt(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()
