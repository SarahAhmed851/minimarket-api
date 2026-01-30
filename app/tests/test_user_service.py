"""
Unit tests for UserService
Tests service layer logic in isolation
"""
import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.models.user import User
from app.auth.security import hash_password, verify_password


class TestUserService:
    """Unit tests for UserService class"""
    
    def setup_method(self):
        """Set up mock database for each test"""
        self.mock_db = Mock()
        self.service = UserService(self.mock_db)
    
    def test_create_user_success(self):
        """Test successful user creation"""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Test12345"
        )
        
        # Mock: email doesn't exist
        self.mock_db.query().filter().first.return_value = None
        
        # Act
        result = self.service.create_user(user_data)
        
        # Assert
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert result.hashed_password.startswith("$2b$")  # bcrypt hash
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
    
    def test_create_user_duplicate_email(self):
        """Test that duplicate email raises error"""
        # Arrange
        user_data = UserCreate(
            username="newuser",
            email="existing@example.com",
            password="Test12345"
        )
        
        # Mock: email already exists
        existing_user = User(
            id=1,
            username="olduser",
            email="existing@example.com",
            hashed_password="somehash"
        )
        self.mock_db.query().filter().first.return_value = existing_user
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.service.create_user(user_data)
        
        assert exc_info.value.status_code == 400
        assert "already registered" in exc_info.value.detail.lower()
    
    def test_create_user_duplicate_username(self):
        """Test that duplicate username raises error"""
        # Arrange
        user_data = UserCreate(
            username="existinguser",
            email="new@example.com",
            password="Test12345"
        )
        
        # Mock: username already exists
        existing_user = User(
            id=1,
            username="existinguser",
            email="other@example.com",
            hashed_password="somehash"
        )
        self.mock_db.query().filter().first.return_value = existing_user
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.service.create_user(user_data)
        
        assert exc_info.value.status_code == 400
    
    def test_authenticate_user_success(self):
        """Test successful authentication"""
        # Arrange
        email = "test@example.com"
        password = "Test12345"
        hashed = hash_password(password)
        
        # Mock: user exists with correct password
        mock_user = User(
            id=1,
            username="testuser",
            email=email,
            hashed_password=hashed
        )
        self.mock_db.query().filter().first.return_value = mock_user
        
        # Act
        result = self.service.authenticate_user(email, password)
        
        # Assert
        assert result.email == email
        assert result.username == "testuser"
    
    def test_authenticate_user_wrong_password(self):
        """Test authentication fails with wrong password"""
        # Arrange
        email = "test@example.com"
        correct_password = "Test12345"
        wrong_password = "WrongPass123"
        hashed = hash_password(correct_password)
        
        # Mock: user exists
        mock_user = User(
            id=1,
            username="testuser",
            email=email,
            hashed_password=hashed
        )
        self.mock_db.query().filter().first.return_value = mock_user
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.service.authenticate_user(email, wrong_password)
        
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()
    
    def test_authenticate_user_not_found(self):
        """Test authentication fails when user doesn't exist"""
        # Arrange
        email = "nonexistent@example.com"
        password = "Test12345"
        
        # Mock: user doesn't exist
        self.mock_db.query().filter().first.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.service.authenticate_user(email, password)
        
        assert exc_info.value.status_code == 401
    
    def test_password_is_hashed(self):
        """Test that passwords are never stored in plain text"""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="PlainTextPassword123"
        )
        
        # Mock
        self.mock_db.query().filter().first.return_value = None
        
        # Act
        result = self.service.create_user(user_data)
        
        # Assert
        assert result.hashed_password != "PlainTextPassword123"
        assert result.hashed_password.startswith("$2b$")  # bcrypt format
        assert len(result.hashed_password) > 50  # hashed passwords are long