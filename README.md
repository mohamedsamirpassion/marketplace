# Marketplace

# Cairo Bazaar

Cairo Bazaar is an online marketplace platform focused on the Egyptian market, allowing users to buy and sell items across various categories.

## Features

- **User authentication**: Email-based registration and login with email verification
- **Google OAuth integration**: Sign in with Google functionality
- **Multilingual support**: English and Arabic languages
- **Responsive design**: Mobile-friendly interface
- **Listings management**: Create, edit, and manage listings
- **User profiles**: Personal profiles with listings history
- **Favorites**: Save favorite listings for later viewing
- **Search and filtering**: Advanced search capabilities with multiple filters
- **Admin dashboard**: Comprehensive admin controls for site management

## Technologies

- Django 5.1+
- Bootstrap 5.3
- PostgreSQL (Production) / SQLite (Development)
- Django Allauth for authentication
- WhiteNoise for static files
- Gunicorn for deployment

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: 
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with required environment variables
6. Run migrations: `python manage.py migrate`
7. Start the development server: `python manage.py runserver`

## Deployment

The application is configured for deployment on Railway or Render with minimal setup required. See deployment instructions in the env_setup.md file.
