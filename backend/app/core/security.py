"""
Security utilities: JWT tokens, password hashing (bcrypt), password recovery
"""

import os
import uuid
import random
import string
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from dotenv import load_dotenv

load_dotenv()

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Setup logger
logger = logging.getLogger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against bcrypt hash"""
    # Truncate password to 72 bytes (bcrypt limit)
    plain_password = plain_password[:72]
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt (salt is auto-generated)"""
    # Truncate password to 72 bytes (bcrypt limit)
    password = password[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token (longer expiry)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and verify JWT token.
    Returns empty dict if token is invalid (maintains compatibility).
    Logs detailed error information for debugging.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"✅ Token decodificado exitosamente")
        return payload
    except jwt.ExpiredSignatureError:
        logger.error(f"❌ Token expirado - verificar ACCESS_TOKEN_EXPIRE_MINUTES")
        return {}
    except jwt.JWTClaimsError as e:
        logger.error(f"❌ Claims inválidos en el token: {e}")
        return {}
    except jwt.JWTError as e:
        logger.error(f"❌ Error JWT: {e}")
        return {}
    except Exception as e:
        logger.error(f"❌ Error inesperado decodificando token: {e}")
        return {}


def generate_reset_token() -> str:
    """Generate a secure token for password recovery"""
    return str(uuid.uuid4()) + str(uuid.uuid4())


# ============================================
# VERIFICATION CODE GENERATION (NUEVO)
# ============================================

def generate_verification_code(length: int = 6) -> str:
    """
    Generate a numeric verification code for email/SMS verification
    """
    return ''.join(random.choices(string.digits, k=length))