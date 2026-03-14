from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from tools.git_tools import GitTools
from llm.gemini_client import GeminiClient


class AgentState(TypedDict):
    has_changes: bool
    diff: str
    commit_message: str
    approved: bool
    committed: bool
    push_approved: bool
    pushed: bool
    error: str


class GitAutomationAgent:
    def __init__(self, repo_path: str):
        self.git_tools = GitTools(repo_path)
        self.gemini_client = GeminiClient()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("detect_changes", self.detect_changes)
        workflow.add_node("analyze_diff", self.analyze_diff)
        workflow.add_node("generate_commit_message", self.generate_commit_message)
        workflow.add_node("human_approval", self.human_approval)
        workflow.add_node("git_commit", self.git_commit)
        workflow.add_node("push_approval", self.push_approval)
        workflow.add_node("git_push", self.git_push)
        
        # Define edges
        workflow.set_entry_point("detect_changes")
        
        workflow.add_conditional_edges(
            "detect_changes",
            lambda x: "analyze" if x["has_changes"] else "end",
            {
                "analyze": "analyze_diff",
                "end": END
            }
        )
        
        workflow.add_edge("analyze_diff", "generate_commit_message")
        workflow.add_edge("generate_commit_message", "human_approval")
        
        workflow.add_conditional_edges(
            "human_approval",
            lambda x: "commit" if x["approved"] else "end",
            {
                "commit": "git_commit",
                "end": END
            }
        )
        
        workflow.add_edge("git_commit", "push_approval")
        
        workflow.add_conditional_edges(
            "push_approval",
            lambda x: "push" if x["push_approved"] else "end",
            {
                "push": "git_push",
                "end": END
            }
        )
        
        workflow.add_edge("git_push", END)
        
        return workflow.compile()
    
    def detect_changes(self, state: AgentState) -> AgentState:
        print("🔍 Detecting changes...")
        has_changes = self.git_tools.has_changes()
        state["has_changes"] = has_changes
        
        if not has_changes:
            print("✅ No changes detected")
        else:
            print("📝 Changes detected!")
        
        return state
    
    def analyze_diff(self, state: AgentState) -> AgentState:
        print("📊 Analyzing diff...")
        diff = self.git_tools.get_diff()
        state["diff"] = diff
        print(f"Diff preview:\n{diff[:200]}...")
        return state
    
    def generate_commit_message(self, state: AgentState) -> AgentState:
        print("🤖 Generating commit message with AI...")
        try:
            commit_message = self.gemini_client.generate_commit_message(state["diff"])
            state["commit_message"] = commit_message
            print(f"✨ Generated: {commit_message}")
        except Exception as e:
            state["error"] = str(e)
            print(f"❌ Error generating commit message: {e}")
        
        return state
    
    def human_approval(self, state: AgentState) -> AgentState:
        print("\n" + "="*60)
        print(f"📋 Proposed commit message:")
        print(f"   {state['commit_message']}")
        print("="*60)
        print("\nOptions:")
        print("  [y] Yes - Approve and use this message")
        print("  [n] No - Reject and abort")
        print("  [e] Edit - Modify the commit message")
        
        response = input("\n✋ Your choice (y/n/e): ").strip().lower()
        
        if response == 'e':
            print("\n✏️  Enter your custom commit message:")
            custom_message = input("   > ").strip()
            if custom_message:
                state["commit_message"] = custom_message
                print(f"✅ Updated to: {custom_message}")
                state["approved"] = True
            else:
                print("❌ Empty message. Aborting...")
                state["approved"] = False
        elif response == 'y':
            print("✅ Approved! Proceeding to commit...")
            state["approved"] = True
        else:
            print("❌ Rejected. Aborting...")
            state["approved"] = False
        
        return state
    
    def git_commit(self, state: AgentState) -> AgentState:
        print("💾 Staging and committing changes...")
        
        if not self.git_tools.git_add_all():
            state["error"] = "Failed to stage changes"
            state["committed"] = False
            return state
        
        if self.git_tools.git_commit(state["commit_message"]):
            state["committed"] = True
            print("✅ Committed successfully!")
        else:
            state["error"] = "Failed to commit"
            state["committed"] = False
        
        return state
    
    def push_approval(self, state: AgentState) -> AgentState:
        print("\n" + "="*60)
        print(f"🚀 Ready to push to remote repository")
        print(f"   Branch: {self.git_tools.get_current_branch()}")
        print("="*60)
        
        response = input("\n✋ Approve push to remote? (y/n): ").strip().lower()
        state["push_approved"] = response == 'y'
        
        if state["push_approved"]:
            print("✅ Approved! Pushing...")
        else:
            print("❌ Push cancelled. Changes are committed locally only.")
        
        return state
    
    def git_push(self, state: AgentState) -> AgentState:
        print("🚀 Pushing to remote...")
        
        if self.git_tools.git_push():
            state["pushed"] = True
            print("✅ Pushed successfully!")
        else:
            state["error"] = "Failed to push"
            state["pushed"] = False
            print("❌ Push failed. Check your remote configuration.")
        
        return state
    
    def run(self):
        initial_state = {
            "has_changes": False,
            "diff": "",
            "commit_message": "",
            "approved": False,
            "committed": False,
            "push_approved": False,
            "pushed": False,
            "error": ""
        }
        
        result = self.graph.invoke(initial_state)
        return result
