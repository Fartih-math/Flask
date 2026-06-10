from cryptography.fernet import Fernet
import os

KEY_ENV = 'ENCRYPTION_KEY'

def load_or_generate_key():
    key = os.environ.get(KEY_ENV)
    if key:
        return key.encode()
    else:
        # generate a new key and store it in the environment (not persistent)
        # better to set it once manually in Railway variables
        new_key = Fernet.generate_key()
        print("WARNING: No ENCRYPTION_KEY env var set, using temporary key")
        return new_key

KEY = load_or_generate_key()
cipher = Fernet(KEY)
