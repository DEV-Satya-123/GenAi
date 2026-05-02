# PostgreSQL Setup Guide

## 🚀 Quick Start

### 1. Install PostgreSQL

**Windows:**
```bash
# Download from: https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql

# Or use Docker:
docker run --name gitsmartai-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
```

**Mac:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

---

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE gitsmartai;

# Create user (optional)
CREATE USER gitsmartai_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE gitsmartai TO gitsmartai_user;

# Exit
\q
```

---

### 3. Update Environment Variables

Create or update `.env` file:

```env
# PostgreSQL Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/gitsmartai

# Or with custom user:
# DATABASE_URL=postgresql://gitsmartai_user:your_secure_password@localhost:5432/gitsmartai

# Other existing variables...
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
```

---

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `sqlalchemy` - ORM for database operations
- `psycopg2-binary` - PostgreSQL adapter
- `alembic` - Database migrations

---

### 5. Initialize Database

```bash
# Run migration script
python -m backend.database.migrate_from_json
```

This will:
- ✅ Create all database tables
- ✅ Migrate users from `users.json`
- ✅ Migrate repositories from `repos.json`
- ✅ Preserve all existing data

---

### 6. Start the Application

```bash
python backend/api.py
```

---

## 📊 Database Schema

### Tables Created:

1. **users** - User authentication
   - id, username, email, password_hash
   - is_active, created_at, updated_at

2. **repositories** - Repository management
   - id, repo_id, user_id, name, git_url, path
   - is_active, is_local, current_branch
   - cloned_at, last_checked

3. **commits** - Commit history
   - id, repository_id, commit_hash, message
   - author_name, author_email, committed_at
   - files_changed, insertions, deletions

4. **audit_logs** - Security audit trail
   - id, user_id, event_type, event_data
   - ip_address, success, created_at

5. **repository_statistics** - Cached analytics
   - id, repository_id, total_commits
   - health_score, health_rating, languages

---

## 🔧 Troubleshooting

### Connection Error

```
Error: could not connect to server
```

**Solution:**
```bash
# Check if PostgreSQL is running
# Windows:
pg_ctl status

# Mac/Linux:
sudo systemctl status postgresql

# Start if not running:
sudo systemctl start postgresql
```

### Authentication Failed

```
Error: password authentication failed
```

**Solution:**
- Check DATABASE_URL in `.env`
- Verify PostgreSQL user password
- Reset password if needed:
  ```sql
  ALTER USER postgres PASSWORD 'new_password';
  ```

### Database Does Not Exist

```
Error: database "gitsmartai" does not exist
```

**Solution:**
```bash
createdb gitsmartai
```

---

## 🐳 Docker Setup (Recommended)

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: gitsmartai-postgres
    environment:
      POSTGRES_DB: gitsmartai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**Start:**
```bash
docker-compose up -d
```

**Stop:**
```bash
docker-compose down
```

---

## 📈 Benefits of PostgreSQL

### vs JSON Files:

| Feature | JSON Files | PostgreSQL |
|---------|-----------|------------|
| **Concurrent Users** | ❌ 1-2 | ✅ 100+ |
| **Data Integrity** | ⚠️ Risk of corruption | ✅ ACID transactions |
| **Query Speed** | ⚠️ Slow for large data | ✅ Fast with indexes |
| **Relationships** | ❌ Manual | ✅ Foreign keys |
| **Search** | ❌ Limited | ✅ Full-text search |
| **Backup** | ⚠️ Manual file copy | ✅ Built-in tools |
| **Scalability** | ❌ Limited | ✅ Unlimited |

---

## 🔄 Rollback to JSON (if needed)

If you need to go back to JSON files:

1. Stop the application
2. Comment out database imports in `api.py`
3. Restore JSON files from backup
4. Restart application

---

## 📚 Next Steps

1. ✅ Test login with existing users
2. ✅ Verify repositories are loaded
3. ✅ Check all features work
4. ✅ Set up database backups
5. ✅ Configure production settings

---

## 🎯 Production Checklist

- [ ] Use strong DATABASE_URL password
- [ ] Enable SSL for database connection
- [ ] Set up automated backups
- [ ] Configure connection pooling
- [ ] Add database monitoring
- [ ] Set up replication (optional)

---

## 📞 Support

If you encounter issues:
1. Check PostgreSQL logs
2. Verify DATABASE_URL format
3. Test database connection manually
4. Check firewall settings

**Database URL Format:**
```
postgresql://[user]:[password]@[host]:[port]/[database]
```

Example:
```
postgresql://postgres:password@localhost:5432/gitsmartai
```

---

## ✅ Verification

Test database connection:

```python
from backend.database.connection import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.fetchone())
```

Should output PostgreSQL version.

---

**🎉 You're now using PostgreSQL! Your project is production-ready!**
