#!/usr/bin/env python3
import sys
from agent_graph import GitAutomationAgent
from change_detector import watch_repository
from config import REPO_PATH
import time


def run_agent():
    """Run the agent once"""
    print("\n🤖 AI Git Automation Agent Starting...\n")
    agent = GitAutomationAgent(REPO_PATH)
    result = agent.run()
    
    if result.get("error"):
        print(f"\n❌ Error: {result['error']}")
    elif result.get("pushed"):
        print("\n🎉 All done! Changes committed and pushed.")
    elif not result.get("has_changes"):
        print("\n💤 No changes to process.")
    else:
        print("\n👋 Operation cancelled or incomplete.")


def run_watch_mode():
    """Run in watch mode - monitor for changes"""
    print("👀 Watch mode: Monitoring repository for changes...")
    print("Press Ctrl+C to stop\n")
    
    def on_change():
        print("\n" + "="*60)
        print("🔔 Change detected! Running automation...")
        print("="*60)
        run_agent()
        print("\n👀 Watching for more changes...\n")
    
    try:
        watch_repository(REPO_PATH, on_change)
    except KeyboardInterrupt:
        print("\n\n👋 Stopped watching. Goodbye!")


def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║         🤖 AI Git Automation Agent                        ║
║         Powered by Google Gemini & LangGraph              ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        run_watch_mode()
    else:
        run_agent()


if __name__ == "__main__":
    main()
