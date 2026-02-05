# Todo API - Backend Deployment

This is a standalone deployment package for the Todo API backend. It contains everything needed to deploy the FastAPI application to various hosting platforms.

## Prerequisites

- Python 3.12+
- PostgreSQL database (recommended) or SQLite
- Environment variables configured

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
DATABASE_URL="postgresql://username:password@localhost:5432/todo_db"
# For SQLite in development: DATABASE_URL="sqlite:///./todo_app.db"

# JWT Secret (Generate a strong secret for production)
BETTER_AUTH_SECRET="your-super-secret-jwt-key-change-this-in-production"

# Environment (development, production)
ENVIRONMENT="production"

# Server Configuration
HOST="0.0.0.0"
PORT=8000

# Allowed Origins (comma-separated list)
ALLOWED_ORIGINS="https://your-frontend-domain.com,https://www.your-frontend-domain.com"

# OpenAI API (optional, for AI features)
OPENAI_API_KEY=""
OPENAI_MODEL="gpt-4"

# RAG Engine Configuration
RAG_ENGINE_URL="http://localhost:8000"

# MCP Service Configuration
MCP_BASE_URL="http://localhost:3000/mcp"

# Logging level
LOG_LEVEL="INFO"
```

## Deployment Options

### 1. Railway.app

1. Connect your GitHub repository to Railway
2. Select the `backend-deploy` directory as the root
3. Add the environment variables in Railway dashboard
4. Deploy

### 2. Render.com

1. Create a new Web Service
2. Connect your GitHub repository
3. Set the root directory to `backend-deploy`
4. Add the environment variables in Render dashboard
5. Set the build command to install dependencies
6. Set the start command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Heroku

1. Create a new app in Heroku Dashboard
2. Connect to your GitHub repository
3. Set the root directory to `backend-deploy`
4. Add the environment variables in Config Vars
5. Deploy the branch

### 4. Docker/Container Deployment

Build and run the Docker container:

```bash
# Build the image
docker build -t todo-api .

# Run the container
docker run -d -p 8000:8000 --env-file .env todo-api
```

### 5. VPS Deployment

1. Clone or copy the `backend-deploy` directory to your server
2. Install Python 3.12+ and pip
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables
5. Run the application:

```bash
# Direct execution
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or using the start script
chmod +x start.sh
./start.sh
```

## Production Setup with Gunicorn

For production deployments, use Gunicorn with the provided configuration:

```bash
pip install gunicorn uvicorn[standard]
gunicorn app.main:app -c gunicorn_conf.py
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger UI) - only in non-production
- `GET /redoc` - API documentation (ReDoc) - only in non-production
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login
- `GET/POST/PUT/DELETE /api/{user_id}/tasks` - Task management
- `POST /api/chatbot/chat` - AI chatbot endpoint

## Database Configuration

The application supports both PostgreSQL and SQLite databases:

- **Production**: Use PostgreSQL for better performance and concurrency
- **Development**: SQLite can be used for simple setups

Make sure to set the `DATABASE_URL` environment variable accordingly.

## Health Checks

The application provides a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "environment": "production"
}
```

## Security Considerations

- Always use HTTPS in production
- Generate a strong `BETTER_AUTH_SECRET` for JWT signing
- Restrict `ALLOWED_ORIGINS` to your frontend domains only
- Regularly rotate secrets
- Use environment variables for all sensitive configuration

## Scaling

- The application is designed to be horizontally scalable
- Use a load balancer for multiple instances
- Ensure database connection pooling is configured appropriately
- Consider using Redis for session storage in scaled deployments

## Troubleshooting

- Check logs for error messages
- Verify all environment variables are set
- Confirm database connectivity
- Ensure CORS settings allow your frontend domain# todoapp-backend
