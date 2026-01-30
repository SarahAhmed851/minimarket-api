"""
Unit tests for input validation
Tests Pydantic schemas and custom validators
"""
import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate
from app.schemas.product import ProductCreate


class TestUserValidation:
    """Test user input validation"""
    
    def test_valid_user_data(self):
        """Test that valid data passes validation"""
        user = UserCreate(
            username="validuser",
            email="valid@example.com",
            password="Valid123"
        )
        assert user.username == "validuser"
        assert user.email == "valid@example.com"
    
    def test_username_too_short(self):
        """Test that short username is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",  # Too short (< 3 chars)
                email="test@example.com",
                password="Test12345"
            )
        assert "username" in str(exc_info.value).lower()
    
    def test_username_too_long(self):
        """Test that long username is rejected"""
        with pytest.raises(ValidationError):
            UserCreate(
                username="a" * 100,  # Too long (> 50 chars)
                email="test@example.com",
                password="Test12345"
            )
    
    def test_invalid_email_format(self):
        """Test that invalid email is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="not-an-email",  # Invalid format
                password="Test12345"
            )
        assert "email" in str(exc_info.value).lower()
    
    def test_password_too_short(self):
        """Test that short password is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="Short1"  # Too short (< 8 chars)
            )
        assert "password" in str(exc_info.value).lower()
    
    def test_password_missing_number(self):
        """Test custom validator: password must have number"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="NoNumbers"  # No digits
            )
        error_msg = str(exc_info.value).lower()
        assert "number" in error_msg or "digit" in error_msg
    
    def test_password_missing_uppercase(self):
        """Test custom validator: password must have uppercase"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="nouppercase123"  # No uppercase
            )
        error_msg = str(exc_info.value).lower()
        assert "uppercase" in error_msg


class TestProductValidation:
    """Test product input validation"""
    
    def test_valid_product_data(self):
        """Test that valid product data passes"""
        product = ProductCreate(
            name="Test Product",
            description="A test description",
            price=99.99
        )
        assert product.name == "Test Product"
        assert product.price == 99.99
    
    def test_empty_name_rejected(self):
        """Test that empty product name is rejected"""
        with pytest.raises(ValidationError):
            ProductCreate(
                name="",  # Empty
                price=99.99
            )
    
    def test_negative_price_rejected(self):
        """Test that negative price is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                name="Test Product",
                price=-10.00  # Negative
            )
        assert "price" in str(exc_info.value).lower()
    
    def test_zero_price_rejected(self):
        """Test that zero price is rejected"""
        with pytest.raises(ValidationError):
            ProductCreate(
                name="Test Product",
                price=0  # Zero (must be > 0)
            )
    
    def test_optional_description(self):
        """Test that description is optional"""
        product = ProductCreate(
            name="Test Product",
            price=99.99
            # No description
        )
        assert product.description is None