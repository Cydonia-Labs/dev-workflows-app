"""Symmetric encryption for sensitive tokens stored in the database.

Uses Fernet (AES-128-CBC with HMAC-SHA256) from the cryptography library
to encrypt GitHub OAuth tokens at rest. The encryption key is derived
from the application's SECRET_KEY using PBKDF2.
"""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken


# Salt for key derivation — fixed per application.
# Changing this invalidates all encrypted tokens in the database.
_KEY_DERIVATION_SALT = b"dev-workflows-token-encryption-v1"


def _derive_fernet_key(secret_key: str) -> bytes:
    """Derive a Fernet-compatible key from the application secret.

    Uses PBKDF2-HMAC-SHA256 with a fixed salt to produce a
    deterministic 32-byte key, then base64-encodes it for Fernet.

    Args:
        secret_key: The application SECRET_KEY from environment.

    Returns:
        A base64-encoded 32-byte key suitable for Fernet.
    """
    raw_key = hashlib.pbkdf2_hmac(
        "sha256",
        secret_key.encode(),
        _KEY_DERIVATION_SALT,
        iterations=100_000,
        dklen=32,
    )
    return base64.urlsafe_b64encode(raw_key)


def encrypt_token(plaintext: str, secret_key: str) -> str:
    """Encrypt a token for safe storage in the database.

    Args:
        plaintext: The token to encrypt (e.g., a GitHub OAuth token).
        secret_key: The application SECRET_KEY for key derivation.

    Returns:
        The encrypted token as a base64 string.

    Example:
        >>> encrypted = encrypt_token("ghp_abc123", "my-secret-key")
        >>> decrypt_token(encrypted, "my-secret-key")
        'ghp_abc123'
    """
    fernet = Fernet(_derive_fernet_key(secret_key))
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str, secret_key: str) -> str:
    """Decrypt a token retrieved from the database.

    Args:
        ciphertext: The encrypted token string.
        secret_key: The application SECRET_KEY for key derivation.

    Returns:
        The original plaintext token.

    Raises:
        InvalidToken: If decryption fails (wrong key or corrupted data).
    """
    fernet = Fernet(_derive_fernet_key(secret_key))
    return fernet.decrypt(ciphertext.encode()).decode()
