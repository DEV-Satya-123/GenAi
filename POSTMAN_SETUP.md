# Postman Testing Guide - AI Git Automation API

## Quick Setup

### 1. Import Collection (Optional)
Create a new collection named "AI Git Agent" in Postman.

### 2. Set Base URL Variable
- Collection → Variables
- Variable: `base_url`
- Value: `http://localhost:8000`

---

## Authentication Flow

### Step 1: Register User

**Request:**
```
POST {{base_url}}/api/auth/register
```

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123!"
}
```

**Expected Response (200 OK):**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true
}
```

---

### Step 2: Login to Get Token

**Request:**
```
POST {{base_url}}/api/auth/login
```

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Body (x-www-form-urlencoded):**
```
username: testuser
password: SecurePass123!
```

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Test Script (Auto-save token):**
```javascript
var jsonData = pm.response.json();
pm.collectionVariables.set("auth_token", jsonData.access_token);
console.log("Token saved:", jsonData.access_token);
```

---

### Step 3: Get Current User Info

**Request:**
```
GET {{base_url}}/api/auth/me
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response (200 OK):**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true
}
```

---

## Repository Management

### Get Repository Status

**Request:**
```
GET {{base_url}}/api/status
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
  "has_changes": false,
  "current_branch": "main",
  "repo_path": "D:\\GITHUB\\ai_git_agent",
  "timestamp": "2026-03-31T23:14:27.351773"
}
```

---

### List All Repositories

**Request:**
```
GET {{base_url}}/api/repositories
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "repositories": {},
  "active_repo_path": null
}
```

---

### Add Local Repository

**Request:**
```
POST {{base_url}}/api/add-local
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "local_path": "D:\\GITHUB\\ai_git_agent",
  "name": "my-project"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Local repository added successfully",
  "repo_id": "my-project_abc12345",
  "repo_path": "D:\\GITHUB\\ai_git_agent"
}
```

---

### Clone Repository

**Request:**
```
POST {{base_url}}/api/clone
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "git_url": "https://github.com/octocat/Hello-World.git",
  "name": "hello-world"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Repository cloned successfully",
  "repo_id": "hello-world_xyz98765",
  "repo_path": "D:\\GITHUB\\ai_git_agent\\cloned-repos\\hello-world_xyz98765"
}
```

---

### Set Active Repository

**Request:**
```
POST {{base_url}}/api/set-active-repo
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "repo_id": "my-project_abc12345"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Active repository updated",
  "active_repo": {
    "id": "my-project_abc12345",
    "name": "my-project",
    "path": "D:\\GITHUB\\ai_git_agent"
  }
}
```

---

### Delete Repository

**Request:**
```
DELETE {{base_url}}/api/repository/my-project_abc12345
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Repository deleted successfully"
}
```

---

## Workflow Operations

### Run AI Agent

**Request:**
```
POST {{base_url}}/api/run
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Workflow paused for approval",
  "result": {
    "status": "awaiting_approval",
    "commit_message": "feat: add new feature"
  }
}
```

---

### Approve Commit

**Request:**
```
POST {{base_url}}/api/approve
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "action": "approve",
  "approval_type": "commit",
  "commit_message": "feat: add new feature"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Commit approved, awaiting push approval",
  "result": {
    "status": "awaiting_push_approval"
  }
}
```

---

### Approve Push

**Request:**
```
POST {{base_url}}/api/approve
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "action": "approve",
  "approval_type": "push"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Push completed",
  "result": {
    "committed": true,
    "pushed": true
  }
}
```

---

## Error Responses

### 401 Unauthorized (No Token)
```json
{
  "detail": "Not authenticated"
}
```

### 401 Unauthorized (Invalid Token)
```json
{
  "error": "HTTPException",
  "message": "Could not validate credentials",
  "status_code": 401
}
```

### 429 Too Many Requests (Rate Limited)
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "detail": "5 per 1 hour"
}
```

### 400 Bad Request (Validation Error)
```json
{
  "error": "Validation Error",
  "message": "Invalid input data",
  "details": [
    {
      "field": "body.password",
      "message": "Password must be at least 8 characters",
      "type": "value_error"
    }
  ]
}
```

---

## Collection Variables Setup

1. **Create Collection** → "AI Git Agent"
2. **Add Variables:**
   - `base_url`: `http://localhost:8000`
   - `auth_token`: (auto-populated by login test script)

3. **Add Pre-request Script (Collection level):**
```javascript
// Auto-refresh token if expired (optional)
if (!pm.collectionVariables.get("auth_token")) {
    console.log("No token found. Please login first.");
}
```

---

## Testing Checklist

- [ ] Register new user
- [ ] Login and get token
- [ ] Get current user info
- [ ] Get repository status
- [ ] List repositories
- [ ] Add local repository
- [ ] Clone repository
- [ ] Set active repository
- [ ] Run AI agent
- [ ] Approve commit
- [ ] Approve push
- [ ] Delete repository
- [ ] Test without token (should fail with 401)
- [ ] Test with expired token (should fail with 401)

---

## Tips

1. **Save Token Automatically**: Add test script to login request
2. **Use Variables**: Use `{{auth_token}}` instead of copying token
3. **Environment**: Create separate environments for dev/prod
4. **Test Scripts**: Add assertions to verify responses
5. **Pre-request Scripts**: Auto-refresh expired tokens

---

## Common Issues

**Issue**: "Not authenticated"  
**Solution**: Make sure Authorization header has `Bearer {{auth_token}}`

**Issue**: "Could not validate credentials"  
**Solution**: Token expired (30 min), login again

**Issue**: "Rate limit exceeded"  
**Solution**: Wait before retrying, or increase limits in code

**Issue**: "Invalid Git URL format"  
**Solution**: Only GitHub, GitLab, Bitbucket URLs allowed

---

**Last Updated**: 2026-03-31  
**API Version**: 1.0.0
