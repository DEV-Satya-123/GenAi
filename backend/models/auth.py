"""Authentication models"""

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """User registration request"""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data"""
    username: str | None = None


class User(BaseModel):
    """User model"""
    username: str
    email: str
    is_active: bool = True
