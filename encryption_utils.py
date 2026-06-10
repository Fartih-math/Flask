from cryptography.fernet import Fernet
import os

KEY_FILE = 'secret.key'

def load_or_generate_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        return key

KEY = load_or_generate_key()
cipher = Fernet(KEY)

def encrypt_name(name: str) -> str:
    return cipher.encrypt(name.encode()).decode()

def decrypt_name(encrypted_name: str) -> str:
    return cipher.decrypt(encrypted_name.encode()).decode()
