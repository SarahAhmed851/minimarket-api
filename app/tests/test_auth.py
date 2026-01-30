"""
Basic security tests for authentication
"""
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_register_user():
    """Test user registration"""
    # Use a strong password that passes all validators
    response = client.post("/users/register", json={
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"test_{uuid.uuid4()}@example.com",
        "password": "TestPass123"  # ← Fixed password
    })
    assert response.status_code == 201, f"Registration failed: {response.json()}"
    assert "id" in response.json()
    assert "password" not in response.json()  # Security: no password in response

def test_register_duplicate_email():
    """Test duplicate email rejection"""
    unique_email = f"duplicate_{uuid.uuid4()}@example.com"
    
    # Register first user
    client.post("/users/register", json={
        "username": f"user1_{uuid.uuid4().hex[:8]}",
        "email": unique_email,
        "password": "Pass12345"
    })
    
    # Try to register with same email
    response = client.post("/users/register", json={
        "username": f"user2_{uuid.uuid4().hex[:8]}",
        "email": unique_email,
        "password": "Pass67890"
    })
    assert response.status_code == 400

def test_login_success():
    """Test successful login returns JWT"""
    unique_email = f"login_{uuid.uuid4()}@example.com"
    
    # Register user
    client.post("/users/register", json={
        "username": f"logintest_{uuid.uuid4().hex[:8]}",
        "email": unique_email,
        "password": "Login12345"
    })
    
    # Login
    response = client.post("/users/login", json={
        "email": unique_email,
        "password": "Login12345"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

def test_login_wrong_password():
    """Security test: wrong password returns 401"""
    unique_email = f"wrongpwd_{uuid.uuid4()}@example.com"
    
    # Register user first
    client.post("/users/register", json={
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": unique_email,
        "password": "Correct123"
    })
    
    # Try with wrong password
    response = client.post("/users/login", json={
        "email": unique_email,
        "password": "WrongPassword"
    })
    assert response.status_code == 401

def test_access_protected_route_without_token():
    """Security test: protected route requires authentication"""
    response = client.post("/products/", json={
        "name": "Test Product",
        "price": 99.99
    })
    # Should be 401 (not authenticated) or 403 (forbidden)
    assert response.status_code in [401, 403]

def test_user_cannot_access_other_user_data():
    """CRITICAL Security test: User isolation"""
    # Create User A and their product
    email_a = f"usera_{uuid.uuid4()}@example.com"
    client.post("/users/register", json={
        "username": f"usera_{uuid.uuid4().hex[:8]}",
        "email": email_a,
        "password": "UserA12345"
    })
    login_a = client.post("/users/login", json={
        "email": email_a,
        "password": "UserA12345"
    })
    token_a = login_a.json()["access_token"]
    
    product = client.post("/products/", 
        json={"name": "UserA Product", "price": 100},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    product_id = product.json()["id"]
    
    # Create User B
    email_b = f"userb_{uuid.uuid4()}@example.com"
    client.post("/users/register", json={
        "username": f"userb_{uuid.uuid4().hex[:8]}",
        "email": email_b,
        "password": "UserB12345"
    })
    login_b = client.post("/users/login", json={
        "email": email_b,
        "password": "UserB12345"
    })
    token_b = login_b.json()["access_token"]
    
    # User B tries to update User A's product
    response = client.put(f"/products/{product_id}",
        json={"price": 1.00},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    
    # MUST be 403 Forbidden
    assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.json()}"



def test_create_product_with_valid_token():
    """Test that authenticated user CAN create product"""
    # Register and login
    email = f"creator_{uuid.uuid4()}@example.com"
    client.post("/users/register", json={
        "username": f"creator_{uuid.uuid4().hex[:8]}",
        "email": email,
        "password": "Creator123"
    })
    
    login_response = client.post("/users/login", json={
        "email": email,
        "password": "Creator123"
    })
    token = login_response.json()["access_token"]
    
    # Create product with token
    response = client.post("/products/",
        json={"name": "Authenticated Product", "price": 199.99},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == "Authenticated Product"


def test_get_products_public_access():
    """Test that anyone can view all products (public endpoint)"""
    response = client.get("/products/")
    
    # Should work without authentication
    assert response.status_code == 200
    assert "products" in response.json() or isinstance(response.json(), list)


def test_get_my_products_requires_auth():
    """Test that /products/my requires authentication"""
    response = client.get("/products/my")
    
    # Should fail without token
    assert response.status_code in [401, 403]


def test_update_own_product_succeeds():
    """Test that user CAN update their own product"""
    # Register, login, create product
    email = f"owner_{uuid.uuid4()}@example.com"
    client.post("/users/register", json={
        "username": f"owner_{uuid.uuid4().hex[:8]}",
        "email": email,
        "password": "Owner123"
    })
    
    login = client.post("/users/login", json={
        "email": email,
        "password": "Owner123"
    })
    token = login.json()["access_token"]
    
    product = client.post("/products/",
        json={"name": "My Product", "price": 100},
        headers={"Authorization": f"Bearer {token}"}
    )
    product_id = product.json()["id"]
    
    # Update own product
    response = client.put(f"/products/{product_id}",
        json={"price": 150},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["price"] == 150


def test_delete_own_product_succeeds():
    """Test that user CAN delete their own product"""
    # Register, login, create product
    email = f"deleter_{uuid.uuid4()}@example.com"
    client.post("/users/register", json={
        "username": f"deleter_{uuid.uuid4().hex[:8]}",
        "email": email,
        "password": "Deleter123"
    })
    
    login = client.post("/users/login", json={
        "email": email,
        "password": "Deleter123"
    })
    token = login.json()["access_token"]
    
    product = client.post("/products/",
        json={"name": "To Delete", "price": 100},
        headers={"Authorization": f"Bearer {token}"}
    )
    product_id = product.json()["id"]
    
    # Delete own product
    response = client.delete(f"/products/{product_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 204


def test_delete_other_user_product_forbidden():
    """SECURITY: Test that user CANNOT delete other user's product"""
    # User A creates product
    email_a = f"usera_{uuid.uuid4()}@example.com"
    client.post("/users/register", json={
        "username": f"usera_{uuid.uuid4().hex[:8]}",
        "email": email_a,
        "password": "UserA123"
    })
    login_a = client.post("/users/login", json={
        "email": email_a,
        "password": "UserA123"
    })
    token_a = login_a.json()["access_token"]
    
    product = client.post("/products/",
        json={"name": "UserA Product", "price": 100},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    product_id = product.json()["id"]
    
    # User B tries to delete
    email_b = f"userb_{uuid.uuid4()}@example.com"
    client.post("/users/register", json={
        "username": f"userb_{uuid.uuid4().hex[:8]}",
        "email": email_b,
        "password": "UserB123"
    })
    login_b = client.post("/users/login", json={
        "email": email_b,
        "password": "UserB123"
    })
    token_b = login_b.json()["access_token"]
    
    response = client.delete(f"/products/{product_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    
    # MUST be 403 Forbidden
    assert response.status_code == 403


def test_invalid_token_rejected():
    """SECURITY: Test that invalid token is rejected"""
    response = client.post("/products/",
        json={"name": "Test", "price": 99},
        headers={"Authorization": "Bearer fake.invalid.token"}
    )
    
    assert response.status_code == 401


def test_malformed_authorization_header():
    """SECURITY: Test that malformed auth header is rejected"""
    response = client.post("/products/",
        json={"name": "Test", "price": 99},
        headers={"Authorization": "NotBearer sometoken"}
    )
    
    assert response.status_code in [401, 403]