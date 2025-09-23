# Real-Time Chat Implementation

## Overview

This implementation adds real-time chat functionality to the Fitness Trainer application using Socket.IO for WebSocket communication, with all messages stored in the database for persistence.

## Features

### 🚀 Core Features
- **Real-time messaging** using Socket.IO
- **Multiple chat rooms** with different themes
- **Database persistence** for all messages
- **User authentication** integration
- **Online status indicators**
- **Typing indicators**
- **Responsive design** for mobile and desktop

### 🏠 Default Chat Rooms
- **general** - General fitness discussion and motivation
- **workout-tips** - Share workout tips and exercise advice
- **nutrition** - Discuss nutrition and meal planning
- **progress** - Share your fitness progress and achievements

### 💾 Database Schema
```sql
-- Chat rooms table
CREATE TABLE chat_room (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME,
    is_active BOOLEAN DEFAULT TRUE
);

-- Messages table
CREATE TABLE chat_message (
    id INTEGER PRIMARY KEY,
    room_id INTEGER FOREIGN KEY REFERENCES chat_room(id),
    user_id INTEGER FOREIGN KEY REFERENCES user(id),
    message TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    created_at DATETIME,
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at DATETIME
);

-- Participants table
CREATE TABLE chat_participant (
    id INTEGER PRIMARY KEY,
    room_id INTEGER FOREIGN KEY REFERENCES chat_room(id),
    user_id INTEGER FOREIGN KEY REFERENCES user(id),
    joined_at DATETIME,
    last_active DATETIME,
    is_online BOOLEAN DEFAULT FALSE
);
```

## Setup Instructions

### 1. Install Dependencies
```bash
# Run the setup script
./setup_chat.sh

# Or manually:
uv add flask-socketio>=5.3.0 python-socketio>=5.8.0 redis>=5.0.0 eventlet>=0.33.0
uv sync
```

### 2. Run Database Migration
```bash
uv run alembic upgrade head
```

### 3. Start the Application
```bash
# Development mode
uv run python3 -m flask run --port=8081

# Production mode with Socket.IO support
uv run gunicorn --worker-class eventlet -w 1 app:app
```

## API Endpoints

### WebSocket Events

#### Client → Server
- `connect` - Initialize connection
- `disconnect` - Handle disconnection
- `join_room` - Join a chat room
- `leave_room` - Leave a chat room
- `send_message` - Send a chat message
- `get_rooms` - Get list of available rooms
- `typing_start` - Start typing indicator
- `typing_stop` - Stop typing indicator

#### Server → Client
- `status` - Connection status updates
- `rooms_list` - List of available chat rooms
- `room_joined` - Successfully joined room with message history
- `new_message` - New message received
- `user_joined` - User joined notification
- `user_left` - User left notification
- `user_typing` - Typing indicator updates
- `error` - Error messages

### HTTP Endpoints
- `GET /chat` - Chat interface page (requires login)

## Frontend Implementation

### Chat Class (`FitnessChat`)
The chat functionality is implemented as a JavaScript class in `templates/chat.html`:

```javascript
class FitnessChat {
    constructor() {
        this.socket = null;
        this.currentRoom = null;
        this.currentUser = null;
        this.typingTimeout = null;
        this.typingUsers = new Set();
    }
}
```

### Key Methods
- `initializeChat()` - Setup Socket.IO connection
- `selectRoom(roomName)` - Join a chat room
- `sendMessage()` - Send a message
- `displayMessage()` - Display messages in UI
- `handleTypingIndicator()` - Show/hide typing indicators
- `updateParticipants()` - Update online users list

## Security Features

### Authentication
- All WebSocket connections require valid user session
- Messages are associated with authenticated users
- Room access is controlled through participant records

### Data Validation
- Message content validation on server-side
- Room name validation
- User authentication verification

### XSS Prevention
- HTML escaping for all message content
- Safe handling of user data

## Database Operations

### Message Storage
- All messages are stored in `chat_message` table
- Includes timestamps, user information, and message type
- Support for different message types (text, system, join, leave)

### Participant Tracking
- User participation tracked in `chat_participant` table
- Online status and last activity timestamps
- Room membership management

## Performance Considerations

### WebSocket Management
- Efficient room joining/leaving
- Typing indicator timeout management
- Connection status monitoring

### Database Optimization
- Indexed queries for message retrieval
- Efficient participant status updates
- Proper relationship definitions

## Troubleshooting

### Common Issues

#### Socket.IO Connection Failed
- Check if dependencies are installed correctly
- Verify Socket.IO server is running with proper worker class
- Check browser console for connection errors

#### Database Migration Issues
- Ensure database connection is working
- Run `uv run alembic current` to check migration status
- Check database permissions

#### Authentication Problems
- Verify user session is active
- Check if user is properly authenticated
- Ensure login system is working

### Debug Commands
```bash
# Check migration status
uv run alembic current

# Check database connection
uv run python3 -c "from app import create_app; app, _, _ = create_app(); print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])"

# Test Socket.IO connection
# Open browser dev tools and check Network tab for WebSocket connection
```

## Production Deployment

### Environment Variables
```bash
# Required for production
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-connection-string
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Optional for Redis (if using external Redis)
REDIS_URL=redis://localhost:6379/0
```

### Gunicorn Configuration
```bash
# Production start command
uv run gunicorn \
    --worker-class eventlet \
    --workers 1 \
    --bind 0.0.0.0:8081 \
    --timeout 120 \
    app:app
```

### Scaling Considerations
- For multiple workers, use Redis as message queue
- Consider horizontal scaling with load balancer
- Monitor WebSocket connections and database performance

## Future Enhancements

### Planned Features
- [ ] Private messaging between users
- [ ] File sharing in chat
- [ ] Message reactions and emojis
- [ ] Push notifications for new messages
- [ ] Chat moderation tools
- [ ] Message search functionality
- [ ] Read receipts
- [ ] Voice messages

### Technical Improvements
- [ ] Redis integration for horizontal scaling
- [ ] Message pagination for large histories
- [ ] Caching for frequently accessed data
- [ ] WebSocket connection pooling
- [ ] Advanced rate limiting

## Contributing

When contributing to the chat functionality:

1. Test all WebSocket events thoroughly
2. Ensure database migrations are proper
3. Test authentication and authorization
4. Verify cross-browser compatibility
5. Check mobile responsiveness
6. Update documentation as needed

## Support

For issues or questions about the chat implementation:
- Check the troubleshooting section above
- Review browser console logs for errors
- Verify server logs for WebSocket events
- Test database connections and migrations