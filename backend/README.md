# WellVest Backend API

FastAPI backend for the WellVest application with JWT authentication, PostgreSQL database, and comprehensive API endpoints.

## Features

- JWT-based authentication
- PostgreSQL database with SQLAlchemy ORM
- Alembic migrations
- Comprehensive API endpoints for:
  - User authentication (login/register)
  - User profile management
  - Investment tracking
  - Wallet management (Income and Shopping wallets)
  - Network and referral system
  - Bonus tracking
  - NOC management

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd wellvest/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a PostgreSQL database:
```bash
createdb wellvest
```

5. Configure environment variables:
   - Copy `.env.example` to `.env` (or use the existing `.env` file)
   - Update the database connection string and other settings as needed

6. Initialize the database:
```bash
python scripts/init_db.py
```

7. Run migrations:
```bash
alembic upgrade head
```

## Running the Application

Start the FastAPI server:
```bash
python scripts/run.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token

### Users
- `GET /api/users/me` - Get current user information
- `PUT /api/users/me` - Update current user information
- `GET /api/users/me/profile` - Get complete user profile with related data

### Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update user profile
- `GET /api/profile/addresses` - Get user addresses
- `POST /api/profile/addresses` - Create new address
- `PUT /api/profile/addresses/{address_id}` - Update address
- `GET /api/profile/bank-details` - Get user bank details
- `POST /api/profile/bank-details` - Create new bank detail
- `PUT /api/profile/bank-details/{bank_detail_id}` - Update bank detail

### Investments
- `GET /api/investments` - Get all investments
- `POST /api/investments` - Create new investment
- `GET /api/investments/{investment_id}` - Get specific investment with team investments
- `PUT /api/investments/{investment_id}` - Update investment
- `GET /api/team-investments` - Get all team investments
- `POST /api/team-investments` - Create new team investment

### Wallets
- `GET /api/income-wallet` - Get income wallet with transactions
- `POST /api/income-wallet/transactions` - Create new income transaction
- `GET /api/income-wallet/transactions` - Get all income transactions
- `PUT /api/income-wallet/transactions/{transaction_id}` - Update income transaction
- `GET /api/shopping-wallet` - Get shopping wallet with transactions and vouchers
- `POST /api/shopping-wallet/transactions` - Create new shopping transaction
- `GET /api/shopping-wallet/transactions` - Get all shopping transactions
- `POST /api/shopping-wallet/vouchers` - Create new shopping voucher
- `GET /api/shopping-wallet/vouchers` - Get all shopping vouchers
- `PUT /api/shopping-wallet/vouchers/{voucher_id}` - Update shopping voucher

### Network
- `GET /api/network` - Get user network with members
- `PUT /api/network` - Update user network
- `POST /api/network/join/{referral_code}` - Join a network using referral code
- `GET /api/bonuses` - Get all bonuses
- `POST /api/bonuses` - Create new bonus
- `PUT /api/bonuses/{bonus_id}` - Update bonus
- `GET /api/noc` - Get all NOCs
- `POST /api/noc` - Create new NOC
- `PUT /api/noc/{noc_id}` - Update NOC

## Frontend Integration

To integrate with the React frontend:
1. Update the API base URL in the frontend configuration
2. Replace static data with API calls
3. Implement JWT token storage in localStorage
4. Add authentication headers to API requests
