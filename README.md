# MiniMarket API 🛒

A simple marketplace API built with FastAPI for the Web Security course (SIE.IN.5011).

## Project Description

MiniMarket is a RESTful API where users can:
- ✅ Register and create accounts
- ✅ Log in and receive JWT tokens
- ✅ Create product listings
- ✅ View all products from everyone
- ✅ Edit/delete only their own products (access control)

## Tech Stack

- **Python 3.10+** - Programming language
- **FastAPI** - Web framework
- **SQLite** - Database (file-based)
- **SQLAlchemy** - ORM (database interaction)
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **bcrypt** - Password hashing
- **JWT** - Authentication tokens

## Project Structure
```
minimarket-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment variables configuration
│   ├── database.py          # Database connection setup
│   ├── auth/
│   │   ├── __init__.py
│   │   └── security.py      # Password hashing & JWT tokens
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User database model
│   │   └── product.py       # Product database model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py          # User request/response validation
│   │   └── product.py       # Product request/response validation
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py  # User business logic
│   │   └── product_service.py # Product business logic
│   └── routers/
│       ├── __init__.py
│       ├── health.py        # Health check endpoints
│       ├── users.py         # User registration/login endpoints
│       └── products.py      # Product CRUD endpoints
├── alembic/
│   ├── versions/
│   │   ├── feed21286_create_users_table.py
│   │   └── 15f0120a75f4_create_products_table.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini              # Migration configuration
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git!)
├── .env.example             # Example environment variables
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd minimarket-api
```

### 2. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
# Copy the example file
copy .env.example .env    # Windows
cp .env.example .env      # Mac/Linux

# Edit .env and change SECRET_KEY to a random string
```

### 5. Run database migrations
```bash
alembic upgrade head
```

### 6. Start the server
```bash
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs (interactive)
- **ReDoc**: http://localhost:8000/redoc (readable)

## API Endpoints

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| GET | `/hello` | Simple hello endpoint |

### Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/users/register` | Create new user | No |
| POST | `/users/login` | Login and get JWT token | No |

### Products

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/products/` | Create new product | Yes |
| GET | `/products/` | Get all products | No |
| GET | `/products/my` | Get my products | Yes |
| GET | `/products/{id}` | Get specific product | No |
| PUT | `/products/{id}` | Update product (own only) | Yes |
| DELETE | `/products/{id}` | Delete product (own only) | Yes |

## Example Requests

### Register a new user:
```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "password123"}'
```

### Login:
```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "password123"}'
```

### Create a product (with token):
```bash
curl -X POST "http://localhost:8000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"name": "Laptop", "description": "Gaming laptop", "price": 1500.99}'
```

## Security Features

- ✅ **Password Hashing**: All passwords are hashed with bcrypt before storage
- ✅ **JWT Authentication**: Login returns a secure token for API access
- ✅ **Access Control**: Users can only edit/delete their own products
- ✅ **Input Validation**: All inputs are validated using Pydantic schemas
- ✅ **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection string | sqlite:///./database.db |
| SECRET_KEY | JWT signing secret | (must change!) |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration | 30 |

## Testing

Use the interactive API documentation at http://localhost:8000/docs to test:

1. Register two users (Alice and Bob)
2. Login as Alice, create a product
3. Login as Bob, try to edit Alice's product → Should get 403 Forbidden
4. Bob creates his own product
5. View all products → Should see both

## Database

To view the database, use [DB Browser for SQLite](https://sqlitebrowser.org/):
- Open `database.db` file
- View `users` and `products` tables
- Check the data structure

