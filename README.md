#  Distributed Chat Application

A real-time chat application built with modern backend technologies. This project demonstrates scalable architecture, real-time communication, and production-ready practices.

##  Tech Stack

- **Backend**: FastAPI (Python)
- **Databases**: PostgreSQL, MongoDB, Redis
- **Real-time**: WebSockets
- **Task Queue**: Celery
- **Containerization**: Docker & Docker Compose
- **Authentication**: JWT

##  Features

- **Real-time messaging** with WebSocket connections
- **User authentication** and session management
- **Multiple chat rooms** with member management
- **Message history** and search functionality
- **File sharing** with upload support
- **Message reactions** and threading
- **Rate limiting** and spam protection
- **Background tasks** for notifications
- **Scalable architecture** supporting thousands of users




##  API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### Rooms
- `GET /api/rooms/` - Get user's rooms
- `POST /api/rooms/` - Create new room
- `POST /api/rooms/{room_id}/join` - Join a room
- `GET /api/rooms/{room_id}/members` - Get room members

### Messages
- `GET /api/messages/{room_id}` - Get message history
- `POST /api/messages/{room_id}` - Send message
- `PUT /api/messages/{message_id}` - Edit message
- `POST /api/messages/{message_id}/react` - Add reaction

### WebSocket
- `WS /api/ws/{room_id}` - Real-time messaging



##  Environment Variables

Create a `.env` file with:

```env
# Database URLs
POSTGRESQL_URL=postgresql://user:password@localhost/chatdb
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379

# JWT Settings
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MongoDB
MONGODB_NAME=chat_db

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

##  Performance

Current performance metrics:
- **Concurrent connections**: 1000+ WebSocket connections
- **Message latency**: <100ms
- **Database queries**: Optimized with proper indexing
- **Memory usage**: Efficient connection pooling



##  Monitoring

The application includes:
- Health check endpoints (`/health`)
- Structured logging with correlation IDs
- Metrics for message volume and active users
- Error tracking and alerting


##  Known Issues

- Large file uploads may timeout (>10MB)
- Message search is case-sensitive
- WebSocket reconnection needs manual refresh


##  What I Learned

Building this project taught me:
- **Real-time systems**: Managing WebSocket connections and message broadcasting
- **Database design**: Choosing the right database for each data type
- **Scalability**: Handling thousands of concurrent users
- **Security**: Implementing proper authentication and rate limiting
- **Testing**: Writing comprehensive tests for async applications
- **DevOps**: Containerizing applications with Docker

