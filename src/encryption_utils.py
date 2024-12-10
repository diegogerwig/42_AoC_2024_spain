from cryptography.fernet import Fernet
import base64
import os
from pathlib import Path
import pandas as pd
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class DataEncryption:
    def __init__(self):
        self.key_file = Path('./data/.encryption_key')
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)
    
    def _load_or_create_key(self) -> bytes:
        """Load existing key or create a new one if it doesn't exist."""
        try:
            if self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    return f.read()
            else:
                key = Fernet.generate_key()
                self.key_file.parent.mkdir(exist_ok=True)
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                return key
        except Exception as e:
            logger.error(f"Error handling encryption key: {str(e)}")
            raise

    def encrypt_dataframe(self, df: pd.DataFrame) -> bytes:
        """Encrypt DataFrame to bytes."""
        try:
            # Convert DataFrame to CSV string
            csv_data = df.to_csv(index=False)
            # Encrypt the string
            encrypted_data = self.fernet.encrypt(csv_data.encode())
            return encrypted_data
        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}")
            raise

    def decrypt_dataframe(self, encrypted_data: bytes) -> Optional[pd.DataFrame]:
        """Decrypt bytes back to DataFrame."""
        try:
            # Decrypt the bytes
            decrypted_data = self.fernet.decrypt(encrypted_data)
            # Convert back to DataFrame
            return pd.read_csv(pd.io.common.StringIO(decrypted_data.decode()))
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            return None

    def save_encrypted_dataframe(self, df: pd.DataFrame, filepath: str) -> bool:
        """Save encrypted DataFrame to file."""
        try:
            encrypted_data = self.encrypt_dataframe(df)
            with open(filepath, 'wb') as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            logger.error(f"Error saving encrypted data: {str(e)}")
            return False

    def load_encrypted_dataframe(self, filepath: str) -> Optional[pd.DataFrame]:
        """Load and decrypt DataFrame from file."""
        try:
            with open(filepath, 'rb') as f:
                encrypted_data = f.read()
            return self.decrypt_dataframe(encrypted_data)
        except Exception as e:
            logger.error(f"Error loading encrypted data: {str(e)}")
            return None