"""Veilige opslag van inloggegevens met encryptie."""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .config import CREDENTIALS_FILE, EMAIL_CREDENTIALS_FILE, SECRET_KEY


def _get_fernet() -> Fernet:
    """Genereer Fernet key van secret."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"tennis_padel_vlaanderen_salt",
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(SECRET_KEY.encode()))
    return Fernet(key)


def save_credentials(username: str, password: str) -> None:
    """Bewaar inloggegevens versleuteld."""
    fernet = _get_fernet()
    data = f"{username}\n{password}"
    encrypted = fernet.encrypt(data.encode())
    CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_FILE.write_bytes(encrypted)
    # Beperk bestandsrechten (alleen eigenaar kan lezen)
    os.chmod(CREDENTIALS_FILE, 0o600)


def load_credentials() -> tuple[str, str] | None:
    """Laad inloggegevens (uit bestand of environment variables voor CI)."""
    # CI/Cloud: lees uit environment
    username = os.environ.get("TENNIS_USERNAME")
    password = os.environ.get("TENNIS_PASSWORD")
    if username and password:
        return (username.strip(), password.strip())

    if not CREDENTIALS_FILE.exists():
        return None
    try:
        fernet = _get_fernet()
        encrypted = CREDENTIALS_FILE.read_bytes()
        decrypted = fernet.decrypt(encrypted).decode()
        username, password = decrypted.split("\n", 1)
        return (username.strip(), password.strip())
    except Exception:
        return None


def credentials_exist() -> bool:
    """Controleer of er credentials zijn (bestand of environment)."""
    return load_credentials() is not None


def delete_credentials() -> bool:
    """Verwijder opgeslagen credentials."""
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()
        return True
    return False


def save_email_credentials(password: str) -> None:
    """Bewaar e-mail wachtwoord (Gmail) versleuteld."""
    fernet = _get_fernet()
    encrypted = fernet.encrypt(password.encode())
    EMAIL_CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    EMAIL_CREDENTIALS_FILE.write_bytes(encrypted)
    os.chmod(EMAIL_CREDENTIALS_FILE, 0o600)


def load_email_credentials() -> str | None:
    """Laad e-mail wachtwoord (uit bestand of environment voor CI)."""
    # CI/Cloud: lees uit environment
    password = os.environ.get("EMAIL_PASSWORD")
    if password:
        return password.strip()

    if not EMAIL_CREDENTIALS_FILE.exists():
        return None
    try:
        fernet = _get_fernet()
        encrypted = EMAIL_CREDENTIALS_FILE.read_bytes()
        return fernet.decrypt(encrypted).decode().strip()
    except Exception:
        return None


def email_credentials_exist() -> bool:
    """Controleer of e-mail credentials zijn (bestand of environment)."""
    return load_email_credentials() is not None


def delete_email_credentials() -> bool:
    """Verwijder opgeslagen e-mail wachtwoord."""
    if EMAIL_CREDENTIALS_FILE.exists():
        EMAIL_CREDENTIALS_FILE.unlink()
        return True
    return False
