# Chat Setup Instructions

## Automatic Setup (Recommended)

The chat functionality is automatically configured during deployment via the `nixpacks.toml` file:

1. **Dependencies**: All required packages are installed via `pyproject.toml`
2. **Database Migration**: `alembic upgrade head` runs automatically
3. **Default Rooms**: Created if they don't exist during build phase
4. **Socket.IO Support**: Configured with eventlet worker class

## Manual Setup (if needed)

### 1. Update Dependencies
```bash
uv add flask-socketio>=5.3.0 python-socketio>=5.8.0 redis>=5.0.0 eventlet>=0.33.0
uv sync
```

### 2. Run Database Migration
```bash
uv run alembic upgrade head
```

### 3. Start Application
```bash
# Development
uv run python3 -m flask run --port=8081

# Production with Socket.IO
uv run gunicorn --worker-class eventlet --workers 1 --timeout 120 app:app
```

## Deployment

The application is configured to automatically:
- Install all chat dependencies
- Run database migrations
- Create default chat rooms
- Start with proper Socket.IO worker class

No additional setup is required for deployment platforms that support nixpacks (like Render, Railway, etc.).

## Default Chat Rooms

The following rooms are created automatically:
- **general** - General fitness discussion and motivation
- **workout-tips** - Share workout tips and exercise advice
- **nutrition** - Discuss nutrition and meal planning
- **progress** - Share your fitness progress and achievements

## Access Chat

Once deployed, users can access the chat by:
1. Logging into the application
2. Clicking on "Chat" in the navigation menu
3. Selecting a room to join the conversation