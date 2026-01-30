"""
Unit tests for authentication/security functions
Tests password hashing, token creation, etc.
"""
import pytest
from datetime import timedelta
from jose import jwt
from app.auth.security import (
    hash_password, 
    verify_password, 
    create_access_token
)
from app.config import settings


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_hash_password_returns_different_hash(self):
        """Test that same password produces different hashes (due to salt)"""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different (bcrypt uses random salt)
        assert hash1 != hash2
        # But both should be bcrypt format
        assert hash1.startswith("$2b$")
        assert hash2.startswith("$2b$")
    
    def test_hash_password_never_returns_plain_text(self):
        """Test that hash is never the same as plain password"""
        password = "MyPassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > len(password)
    
    def test_verify_password_correct(self):
        """Test that correct password verifies successfully"""
        password = "CorrectPassword123"
        hashed = hash_password(password)
        
        result = verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_incorrect(self):
        """Test that wrong password fails verification"""
        password = "CorrectPassword123"
        wrong_password = "WrongPassword456"
        hashed = hash_password(password)
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        # Try with different case
        result = verify_password("testpassword123", hashed)
        
        assert result is False


class TestJWTTokens:
    """Test JWT token creation and validation"""
    
    def test_create_token_contains_email(self):
        """Test that token contains user email"""
        email = "test@example.com"
        token = create_access_token(data={"sub": email})
        
        # Decode token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        assert payload["sub"] == email
    
    def test_create_token_contains_expiration(self):
        """Test that token contains expiration time"""
        token = create_access_token(data={"sub": "test@example.com"})
        
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
    
    def test_token_signature_cannot_be_faked(self):
        """Test that token signature is validated"""
        token = create_access_token(data={"sub": "test@example.com"})
        
        # Try to decode with wrong secret
        with pytest.raises(Exception):
            jwt.decode(
                token, 
                "wrong-secret-key",  # Wrong key!
                algorithms=[settings.ALGORITHM]
            )
    
    def test_custom_expiration_time(self):
        """Test token with custom expiration"""
        custom_expire = timedelta(minutes=15)
        token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=custom_expire
        )
        
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        assert "exp" in payload