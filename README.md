# Fraud App Detection Using Sentiment Analysis

A Django REST Framework backend application that helps users distinguish genuine mobile apps from potentially fraudulent or low-quality apps by analyzing user-generated feedback (reviews/ratings) using GenAI-powered sentiment analysis.

## Project Overview

This project uses Large Language Models (LLMs) via the Groq API to analyze app reviews and classify apps as:
- **LEGIT**: Genuine, trustworthy applications
- **SUSPICIOUS**: Apps with concerning patterns or mixed signals
- **FRAUD**: Apps with clear fraudulent indicators

## Features

- **User Authentication**: JWT-based authentication system
- **App Management**: Store and manage mobile app metadata
- **Review Management**: Bulk upload and manage user reviews for apps
- **AI-Powered Analysis**: LLM-based fraud detection using review sentiment and patterns
- **Analysis History**: Track all analysis runs with full auditability

## Project Structure

```
fraud_app_detector/
├── manage.py
├── fraud_app_detector/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/          # User authentication and profiles
│   ├── apps_store/        # Mobile app metadata management
│   ├── reviews/           # Review storage and management
│   └── analysis/          # LLM-based fraud analysis
└── requirements.txt
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   
   Create a `.env` file in the project root (copy from `.env.example` if available):
   ```bash
   # Required settings
   SECRET_KEY=django-insecure-change-me-to-a-random-secret-key
   DEBUG=True
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   
   # Optional settings
   ALLOWED_HOSTS=127.0.0.1,localhost
   CSRF_TRUSTED_ORIGINS=http://localhost:8000
   ```
   
   **Note**: The `.env` file is gitignored for security. Settings are loaded automatically via `python-dotenv`.

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication (`/api/auth/`)

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login (obtain JWT token)
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/me/` - Get current user info

### Apps (`/api/apps/`)

- `GET /api/apps/` - List all apps (user's own)
- `POST /api/apps/` - Create a new app
- `GET /api/apps/<id>/` - Get app details
- `PUT /api/apps/<id>/` - Update app
- `DELETE /api/apps/<id>/` - Delete app

### Reviews (`/api/reviews/`)

- `GET /api/reviews/` - List reviews (filter by `?app=<id>`)
- `POST /api/reviews/` - Create a single review
- `POST /api/reviews/bulk/` - Bulk upload reviews
- `GET /api/reviews/<id>/` - Get review details
- `PUT /api/reviews/<id>/` - Update review
- `DELETE /api/reviews/<id>/` - Delete review

### Analysis (`/api/analysis/`)

- `POST /api/analysis/run/` - Run fraud analysis on an app
- `GET /api/analysis/` - List analysis runs (filter by `?app=<id>`)
- `GET /api/analysis/<id>/` - Get analysis details

## Usage Examples

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123",
    "password2": "securepassword123"
  }'
```

### 2. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'
```

### 3. Create an App

```bash
curl -X POST http://localhost:8000/api/apps/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example App",
    "package_name": "com.example.app",
    "store_url": "https://play.google.com/store/apps/details?id=com.example.app",
    "developer": "Example Developer",
    "category": "Finance"
  }'
```

### 4. Upload Reviews (Bulk)

```bash
curl -X POST http://localhost:8000/api/reviews/bulk/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": 1,
    "reviews": [
      {
        "text": "Great app! Very useful.",
        "rating": 5,
        "author": "User1",
        "source": "Google Play"
      },
      {
        "text": "This app stole my money!",
        "rating": 1,
        "author": "User2",
        "source": "Google Play"
      }
    ]
  }'
```

### 5. Run Analysis

```bash
curl -X POST http://localhost:8000/api/analysis/run/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": 1,
    "max_reviews": 200
  }'
```

## Configuration

### Environment Variables

All configuration is done via environment variables (loaded from `.env` file). The following variables are available:

**Required:**
- `SECRET_KEY` - Django secret key (change in production!)
- `DEBUG` - Set to `True` for development, `False` for production
- `GROQ_API_KEY` - Your Groq API key (required for analysis)
- `GROQ_MODEL` - Model to use (default: `llama-3.3-70b-versatile`)

**Optional:**
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CSRF_TRUSTED_ORIGINS` - Comma-separated list of trusted origins
- `TIME_ZONE` - Timezone (default: UTC)
- `JWT_ACCESS_MINUTES` - JWT access token lifetime in minutes (default: 30)
- `JWT_REFRESH_DAYS` - JWT refresh token lifetime in days (default: 7)
- `LOG_LEVEL` - Logging level (default: INFO)

### Groq Setup

1. Sign up at [Groq](https://console.groq.com/)
2. Get your API key from the [keys page](https://console.groq.com/keys)
3. Add `GROQ_API_KEY=your_key_here` to your `.env` file
4. Choose a model by setting `GROQ_MODEL` in `.env`

### Model Selection

You can use any model available on Groq. Some recommendations:
- `llama-3.3-70b-versatile` - Powerful and fast (default)
- `llama-3.1-8b-instant` - Fastest, good for quick analysis
- `mixtral-8x7b-32768` - Large context window

## Database

The project uses SQLite by default (configured in `settings.py`). For production, consider switching to PostgreSQL or MySQL.

## Security Notes

- **Always** change `SECRET_KEY` in production (use a strong random key)
- Set `DEBUG=False` in production (via `.env` file)
- Never commit `.env` file to version control (already in `.gitignore`)
- Use environment variables for all sensitive settings
- Configure `ALLOWED_HOSTS` properly for production
- Use HTTPS in production
- Keep your `GROQ_API_KEY` secure and never expose it publicly

## Development

### Running Tests

```bash
python manage.py test
```

### Accessing Admin Panel

1. Create a superuser: `python manage.py createsuperuser`
2. Visit: `http://localhost:8000/admin/`
3. Login with superuser credentials

## License

This project is for academic/research purposes.

## Support

For issues or questions, please refer to the project documentation or contact the development team.

# farud-app-detection

