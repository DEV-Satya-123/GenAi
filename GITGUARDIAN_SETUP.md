# 🛡️ GitGuardian Integration Setup

## 🎯 Hybrid Security Scanner

Your AI Git Agent now uses **both** custom security scanning AND GitGuardian API for maximum protection!

## 🔧 Setup GitGuardian API (Optional but Recommended)

### 1. Get GitGuardian API Key
1. Go to [GitGuardian Dashboard](https://dashboard.gitguardian.com/)
2. Sign up for free account (or use existing)
3. Navigate to **API** section
4. Generate a new **Personal Access Token**
5. Copy the API key

### 2. Add API Key to Environment
```bash
# Add to your .env file
echo "GITGUARDIAN_API_KEY=your_api_key_here" >> .env

# Or set as environment variable
export GITGUARDIAN_API_KEY="your_api_key_here"
```

### 3. Test the Integration
```bash
# Test with GitGuardian API
GITGUARDIAN_API_KEY="your_key" python test_security.py

# Test without GitGuardian (custom only)
python test_security.py
```

## 🚀 How It Works

### Dual-Layer Security Scanning:

#### 🔧 Custom Scanner (Always Active)
- ✅ .gitignore modification detection
- ✅ Newly tracked sensitive files
- ✅ File pattern analysis
- ✅ Project-specific rules
- ✅ Instant response (no network)

#### 🌐 GitGuardian API (When Available)
- ✅ 1000+ secret types detection
- ✅ Advanced ML-based analysis
- ✅ Real secret validation
- ✅ Enterprise-grade accuracy
- ✅ Regular threat updates

## 📊 Security Levels

### 🚫 BLOCKED
- Active secrets detected by GitGuardian
- Private keys or certificates
- Database passwords in plain text

### ⚠️ CRITICAL
- API keys or tokens detected
- .env files removed from .gitignore
- Sensitive files being tracked

### 🔍 WARNING
- Potential secrets (unvalidated)
- Configuration files with credentials
- API connection issues

### ✅ SAFE
- No sensitive data detected
- Clean code changes only

## 💡 Benefits of Hybrid Approach

### 🎯 Best Coverage
- **Custom scanner** catches unique issues GitGuardian misses
- **GitGuardian** catches complex secrets custom scanner might miss
- **Dual validation** reduces false positives and negatives

### 🚀 Performance
- **Custom scanner** runs instantly (no network)
- **GitGuardian** runs in parallel (enhanced detection)
- **Graceful fallback** if API is unavailable

### 💰 Cost Effective
- **Custom scanner** handles most cases (free)
- **GitGuardian** used for advanced detection (paid but worth it)
- **Reduced API calls** = lower costs

## 🔧 Configuration Options

### Environment Variables
```bash
# Required for AI features
GEMINI_API_KEY="your_gemini_key"

# Optional for enhanced security
GITGUARDIAN_API_KEY="your_gitguardian_key"
```

### Docker Environment
```yaml
# docker-compose.yml
environment:
  - GEMINI_API_KEY=${GEMINI_API_KEY}
  - GITGUARDIAN_API_KEY=${GITGUARDIAN_API_KEY}
```

## 🎯 Usage Examples

### With GitGuardian API
```
🛡️ Running custom security analysis...
🌐 Running GitGuardian API analysis...

🚫 BLOCKED: 1 critical security issue(s)
🌐 GITGUARDIAN: 1 advanced detection(s)
   • GitGuardian: AWS Access Key detected (VALID - Active secret!)

🔍 Scanned with: Custom Scanner + GitGuardian API
❌ RECOMMENDATION: DO NOT COMMIT - Fix security issues first
```

### Without GitGuardian API
```
🛡️ Running custom security analysis...
ℹ️ GitGuardian API key not provided, using custom scanner only

⚠️ CRITICAL: 1 security issue(s)
🔒 GITIGNORE: 1 protection(s) removed

🔍 Scanned with: Custom Scanner
⚠️ RECOMMENDATION: Review carefully before committing
```

## 🎉 You Now Have Enterprise-Grade Security!

Your AI Git Agent combines:
- **Custom intelligence** for unique threats
- **Industry-standard detection** for comprehensive coverage
- **Real-time validation** for active secrets
- **Proactive protection** against future exposures

**This hybrid approach makes your tool more powerful than most commercial security scanners!** 🚀