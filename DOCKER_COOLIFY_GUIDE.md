# Docker + Coolify Deployment Guide

## Project Structure
```
fitness-website/
├── app/
│   ├── __init__.py      # Main Flask application
│   └── models.py        # Database models
├── templates/           # HTML templates
├── static/             # Static files (CSS, JS, images)
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── Dockerfile         # Docker configuration
├── .dockerignore      # Files to ignore in Docker build
└── .gitignore         # Files to ignore in Git
```

## Docker Configuration

### Dockerfile
The `Dockerfile` defines how to build your application container:

```dockerfile
FROM python:3.11-slim                    # Use lightweight Python image
WORKDIR /app                            # Set working directory
RUN apt-get update && apt-get install -y gcc  # Install build dependencies
COPY requirements.txt .                # Copy requirements first for better caching
RUN python -m venv /opt/venv            # Create virtual environment
ENV PATH="/opt/venv/bin:$PATH"          # Add venv to PATH
RUN pip install --no-cache-dir -r requirements.txt  # Install dependencies
COPY . .                               # Copy application code
ENV PYTHONUNBUFFERED=1                 # Set environment variables
ENV PORT=8000                          # Set port
EXPOSE $PORT                           # Expose port
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/ || exit 1  # Health check
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "4", "--timeout", "120", "app:app"]  # Start command
```

### .dockerignore
Excludes unnecessary files from the Docker build context:
```
.git, .env, __pycache__/, *.pyc, venv/, .venv/, .vscode/, .idea/, *.log
```

## Environment Variables

### Required Variables
- `SECRET_KEY`: Flask secret key (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `DATABASE_URL`: Database connection string (default: `sqlite:///fitness.db`)
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret

### Optional Variables
- `PORT`: Application port (default: 8000)
- `PYTHONUNBUFFERED`: Python output buffering (default: 1)

## Coolify Deployment

### Method 1: Dockerfile (Recommended)

1. **Connect your GitHub repository to Coolify**
   - In Coolify dashboard, click "New Application"
   - Select "GitHub" as source
   - Choose your repository
   - Select "Dockerfile" as build method

2. **Configure Environment Variables**
   ```bash
   SECRET_KEY=your-secret-key-here
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   DATABASE_URL=sqlite:///fitness.db
   ```

3. **Port Configuration**
   - Set container port to `8000`
   - Coolify will automatically map to a public URL

4. **Health Check**
   - Coolify will use the health check defined in Dockerfile
   - Checks every 30 seconds if the app is responding

### Method 2: Nixpacks

1. **Use the provided `nixpacks.toml`**
   ```toml
   [phases.setup]
   nixPkgs = ["python3", "gcc", "sqlite"]

   [phases.install]
   cmds = [
       "python -m venv /opt/venv",
       ". /opt/venv/bin/activate && pip install --upgrade pip",
       ". /opt/venv/bin/activate && pip install -r requirements.txt"
   ]

   [start]
   cmd = "gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app"

   [variables]
   PORT = "8000"
   ```

2. **In Coolify, select "Nixpacks" as build method**
   - Coolify will automatically detect the Python application
   - Configure environment variables as above

## Local Testing

### Build and Run Locally
```bash
# Build Docker image
docker build -t fitness-trainer .

# Run container
docker run -p 8000:8000 --env-file .env fitness-trainer

# Or with docker-compose
docker-compose up --build
```

### Test Application
- Visit `http://localhost:8000`
- Test all routes: `/food`, `/calories`, `/exercise`
- Test Google OAuth login
- Verify database persistence

## Production Considerations

### Database
- For production, use PostgreSQL instead of SQLite
- Set `DATABASE_URL=postgresql://user:pass@host:port/dbname`
- Add database service in Coolify

### Security
- Never commit `.env` file
- Use Coolify's secret management
- Enable HTTPS in production
- Use strong `SECRET_KEY`

### Performance
- Gunicorn workers: 2-4 per CPU core
- Consider adding Redis for session storage
- Use CDN for static assets

### Monitoring
- Coolify provides basic monitoring
- Set up application logging
- Monitor resource usage

## Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure port 8000 is available
2. **Database errors**: Check `DATABASE_URL` format
3. **OAuth failures**: Verify Google client ID/secret
4. **Static files not loading**: Check template paths

### Coolify Logs
- Check Coolify dashboard for deployment logs
- View container logs for runtime errors
- Use health check status for debugging

## Updating the Application

1. **Make changes to your code**
2. **Commit and push to GitHub**
3. **Coolify will automatically deploy**
4. **Monitor deployment status in dashboard**

## Backup and Recovery

### Database Backup
```bash
# For SQLite
docker exec container_name sqlite3 /app/fitness.db ".backup /backup/fitness.db"

# For PostgreSQL
docker exec container_name pg_dump -U user dbname > backup.sql
```

### Environment Variables
- Store in Coolify's secret management
- Export configuration for backup