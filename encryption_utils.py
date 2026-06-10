from cryptography.fernet import Fernet
import os

KEY_FILE = 'secret.key'
KEY_ENV = 'ENCRYPTION_KEY'

def load_key():
    # Try to get key from environment variable first
    key = os.environ.get(KEY_ENV)
    if key:
        return key.encode()
    # Otherwise, try to read from file
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    # If no key exists, generate a new one and save to file (local only)
    new_key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as f:
        f.write(new_key)
    return new_key

KEY = load_key()
cipher = Fernet(KEY)

def encrypt_name(name: str) -> str:
    return cipher.encrypt(name.encode()).decode()

def decrypt_name(encrypted_name: str) -> str:
    return cipher.decrypt(encrypted_name.encode()).decode()
