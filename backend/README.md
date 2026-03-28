# 🏗️ Backend Architecture

## 📁 Project Structure

```
backend/
├── api.py                          # Main FastAPI application & route definitions
├── models/                         # Data models & validation
│   ├── __init__.py
│   ├── requests.py                 # Pydantic request models
│   └── responses.py                # Pydantic response models
├── services/                       # Business logic layer
│   ├── __init__.py
│   ├── repository_service.py      # Repository management operations
│   └── websocket_service.py       # WebSocket connection management
└── utils/                          # Utility functions
    ├── __init__.py
    └── config.py                   # Configuration management
```

## 🎯 Architecture Principles

### Separation of Concerns
- **API Layer** (`api.py`): HTTP routes, request/response handling
- **Service Layer** (`services/`): Business logic, data operations
- **Model Layer** (`models/`): Data validation, type safety
- **Utility Layer** (`utils/`): Shared helpers, configuration

### Benefits
- ✅ **Maintainability**: Easy to find and fix issues
- ✅ **Testability**: Each component can be tested independently
- ✅ **Scalability**: Add features without touching core files
- ✅ **Readability**: Clear responsibility for each module
- ✅ **Collaboration**: Multiple developers can work simultaneously

## 📦 Module Documentation

### Models (`models/`)

#### `requests.py`
Pydantic models for validating incoming API requests:
- `CloneToPathRequest`: Clone repository to specific path
- `AddLocalRequest`: Add existing local repository
- `SetActiveRepoRequest`: Set active repository
- `ApprovalRequest`: Handle commit/push approvals

#### `responses.py`
Pydantic models for API responses:
- `StatusResponse`: Repository status information
- `RunResponse`: Workflow execution results

### Services (`services/`)

#### `repository_service.py`
Handles all repository management operations:
- **Clone repositories** to specified paths
- **Add local repositories** to tracking
- **Delete repositories** with smart cleanup
- **Load/save** repository configuration
- **Validate** Git repository structure

Key Methods:
```python
async def clone_to_path(git_url, clone_to_path, name)
async def add_local_repository(local_path, name)
async def delete_repository(repo_id, current_repo_path, default_repo_path)
def load_repositories()
def save_repositories(repos)
```

#### `websocket_service.py`
Manages WebSocket connections for real-time updates:
- **Connect/disconnect** client management
- **Broadcast** messages to all clients
- **Handle approvals** for workflow decisions

Key Methods:
```python
async def connect(websocket)
def disconnect(websocket)
async def broadcast(message)
def set_active_agent(agent)
def handle_approval(approval_data)
```

### Utils (`utils/`)

#### `config.py`
Configuration and path management:
- **Get config paths** for repositories and configuration files
- **Ensure directories** exist
- **Centralize** path management

## 🔄 Data Flow

### Repository Cloning Flow
```
1. API receives POST /api/clone-to-path
2. Validates request with CloneToPathRequest model
3. Calls RepositoryService.clone_to_path()
4. Service validates path and executes git clone
5. Saves configuration to repos.json
6. Returns success response via RunResponse model
7. Broadcasts WebSocket update to connected clients
```

### Workflow Execution Flow
```
1. API receives POST /api/run
2. Initializes GitAutomationAgent with active repository
3. Agent detects changes and runs security scan
4. Generates AI commit message
5. Broadcasts approval request via WebSocket
6. User approves/rejects via POST /api/approve
7. Executes commit/push based on approval
8. Broadcasts completion via WebSocket
```

## 🎨 Design Patterns

### Service Pattern
Business logic separated from API routes for:
- Reusability across different endpoints
- Independent testing
- Clear responsibility boundaries

### Repository Pattern
Configuration persistence abstracted into service:
- Load/save operations centralized
- Easy to switch storage backends
- Consistent data access

### Observer Pattern
WebSocket manager broadcasts events:
- Decoupled communication
- Real-time updates
- Multiple subscribers support

## 🧪 Testing Strategy

### Unit Tests
```python
# Test repository service
def test_clone_repository():
    service = RepositoryService(test_dir, test_config)
    success, message, data = await service.clone_to_path(url, path)
    assert success == True

# Test WebSocket manager
def test_broadcast():
    manager = WebSocketManager()
    await manager.broadcast({"type": "test"})
    assert len(manager.active_connections) == 0
```

### Integration Tests
```python
# Test full workflow
async def test_clone_and_activate():
    # Clone repository
    response = await client.post("/api/clone-to-path", json=data)
    assert response.status_code == 200
    
    # Set as active
    response = await client.post("/api/set-active-repo", json={"repo_id": repo_id})
    assert response.status_code == 200
```

## 📝 Code Comments Convention

All functions include comprehensive docstrings:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception occurs
        
    Note:
        Additional important information
    """
```

## 🚀 Future Enhancements

### Potential Additions
- **Database Layer**: Replace JSON with PostgreSQL/MongoDB
- **Caching Layer**: Redis for performance optimization
- **Queue System**: Celery for background tasks
- **Authentication**: JWT-based user authentication
- **Rate Limiting**: Protect API endpoints
- **Logging Service**: Centralized logging with ELK stack

### Scalability Considerations
- **Microservices**: Split into separate services
- **Load Balancing**: Multiple backend instances
- **Message Queue**: RabbitMQ for async operations
- **Container Orchestration**: Kubernetes deployment

## 🎯 Best Practices

### Code Organization
- ✅ One responsibility per module
- ✅ Clear naming conventions
- ✅ Comprehensive documentation
- ✅ Type hints everywhere
- ✅ Error handling at all levels

### Performance
- ✅ Async/await for I/O operations
- ✅ Connection pooling for databases
- ✅ Caching for repeated operations
- ✅ Lazy loading where appropriate

### Security
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CORS configuration
- ✅ Rate limiting

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)