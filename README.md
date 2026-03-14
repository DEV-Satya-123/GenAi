# 🤖 AI Git Automation Agent

An intelligent Git automation tool that uses Google Gemini AI to generate meaningful commit messages and automate your Git workflow with human-in-the-loop approval.

## ✨ Features

- 🔍 Automatic detection of file changes
- 🤖 AI-powered commit message generation using Google Gemini
- 📊 Analyzes git diffs to understand changes
- ✋ Human-in-the-loop approval before committing
- 🚀 Automated git add, commit, and push workflow
- 👀 Watch mode for continuous monitoring
- 🎯 Follows conventional commit format

## 🏗️ Architecture

Built with:
- **Google Gemini API** - LLM for commit message generation
- **LangChain** - LLM integration and structured outputs
- **LangGraph** - Agent workflow orchestration
- **GitPython** - Git operations
- **Watchdog** - File system monitoring

## 📋 Prerequisites

- Python 3.8+
- Git installed and configured
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- A Git repository with remote configured

## 🚀 Installation

1. Clone or download this project:
```bash
cd ai_git_agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
REPO_PATH=.
BRANCH_TO_MONITOR=main
```

## 💻 Usage

### One-time Run
Process current changes once:
```bash
python main.py
```

### Watch Mode
Continuously monitor for changes:
```bash
python main.py --watch
```

## 🔄 Workflow

The agent follows this workflow:

1. **Detect Changes** - Checks for uncommitted changes
2. **Analyze Diff** - Reads the git diff
3. **Generate Commit Message** - AI creates a meaningful message
4. **Human Approval** - You review and approve/reject
5. **Git Commit** - Stages and commits if approved
6. **Git Push** - Pushes to remote repository

## 📁 Project Structure

```
ai_git_agent/
├── main.py                 # Entry point
├── agent_graph.py          # LangGraph workflow
├── change_detector.py      # File monitoring
├── config.py              # Configuration
├── llm/
│   └── gemini_client.py   # Gemini API client
├── tools/
│   └── git_tools.py       # Git operations
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Configuration

Edit `.env` to customize:

- `GEMINI_API_KEY` - Your Gemini API key (required)
- `REPO_PATH` - Path to repository (default: current directory)
- `BRANCH_TO_MONITOR` - Branch to work on (default: main)

## ⚠️ Important Notes

- **Review AI messages** - Always review generated commit messages before approving
- **Test first** - Try on a test branch before using on main/production
- **Sensitive data** - The diff is sent to Gemini API, avoid committing secrets
- **Git credentials** - Ensure your Git is configured with proper authentication
- **Network required** - Needs internet for API calls and pushing

## 🛠️ Troubleshooting

**"GEMINI_API_KEY not found"**
- Make sure `.env` file exists and contains your API key

**"Failed to initialize Git repository"**
- Ensure you're in a valid Git repository
- Run `git init` if needed

**Push fails**
- Check your Git remote configuration: `git remote -v`
- Verify authentication (SSH keys or credentials)

**API errors**
- Verify your Gemini API key is valid
- Check your API quota/limits

## 📝 Example Output

```
🤖 AI Git Automation Agent Starting...

🔍 Detecting changes...
📝 Changes detected!
📊 Analyzing diff...
🤖 Generating commit message with AI...
✨ Generated: feat: add user authentication and login validation

============================================================
📋 Proposed commit message:
   feat: add user authentication and login validation
============================================================

✋ Approve commit and push? (y/n): y
✅ Approved! Proceeding...
💾 Staging and committing changes...
✅ Committed successfully!
🚀 Pushing to remote...
✅ Pushed successfully!

🎉 All done! Changes committed and pushed.
```

## 🤝 Contributing

Feel free to open issues or submit pull requests!

## 📄 License

MIT License - feel free to use this project however you'd like.

## 🙏 Acknowledgments

- Google Gemini for the AI capabilities
- LangChain & LangGraph teams for the excellent frameworks
- GitPython maintainers

---

Built with ❤️ using AI automation
