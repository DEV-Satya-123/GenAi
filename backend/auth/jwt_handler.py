"""JWT token handling with secure password hashing"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
import secrets
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# JWT Configuration - Load from environment
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing configuration
PBKDF2_ITERATIONS = 100000  # Industry standard
HASH_ALGORITHM = "sha256"

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

#get_password_hash() → 2. create_access_token() → 3. decode_access_token() → 4. get_current_user()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash using PBKDF2
    
    Args:
        plain_password: Plain text password
        hashed_password: Stored hash in format: iterations$salt$hash
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Parse stored hash
        parts = hashed_password.split('$')
        if len(parts) != 3:
            return False
        
        iterations = int(parts[0])
        salt = bytes.fromhex(parts[1])
        stored_hash = parts[2]
        
        # Hash the plain password with same parameters
        password_hash = hashlib.pbkdf2_hmac(
            HASH_ALGORITHM,
            plain_password.encode('utf-8'),
            salt,
            iterations
        ).hex()
        
        # Constant-time comparison to prevent timing attacks
        return secrets.compare_digest(password_hash, stored_hash)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash password using PBKDF2 with random salt
    
    Args:
        password: Plain text password
        
    Returns:
        Hash in format: iterations$salt$hash
    """
    # Generate cryptographically secure random salt
    salt = secrets.token_bytes(32)
    
    # Hash password using PBKDF2
    password_hash = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        password.encode('utf-8'),
        salt,
        PBKDF2_ITERATIONS
    ).hex()
    
    # Return in format: iterations$salt$hash
    return f"{PBKDF2_ITERATIONS}${salt.hex()}${password_hash}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get current user from JWT token"""
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"username": username}
