from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from tools.git_tools import GitTools
from llm.gemini_client import GeminiClient
import uuid


class AgentState(TypedDict):
    has_changes: bool
    diff: str
    commit_message: str
    approved: bool
    committed: bool
    push_approved: bool
    pushed: bool
    error: str
    thread_id: str


class GitAutomationAgent:
    def __init__(self, repo_path: str):
        self.git_tools = GitTools(repo_path)
        self.gemini_client = GeminiClient()
        # Initialize memory saver for checkpointing
        self.memory = MemorySaver()
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
        
        # Compile with checkpointer for persistence
        return workflow.compile(checkpointer=self.memory)
    
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
            # Get security analysis
            print("🛡️ Running security analysis...")
            issues, security_level, security_summary = self.git_tools.get_security_analysis()
            
            # Store security info in state
            state["security_issues"] = issues
            state["security_level"] = security_level
            state["security_summary"] = security_summary
            
            print(f"🔍 Security check: {security_level.value}")
            
            # Use the focused diff for better commit message generation
            commit_diff = self.git_tools.get_commit_diff()
            commit_message = self.gemini_client.generate_commit_message(commit_diff, security_summary)
            state["commit_message"] = commit_message
            print(f"✨ Generated: {commit_message}")
        except Exception as e:
            state["error"] = str(e)
            print(f"❌ Error generating commit message: {e}")
        
        return state
    
    def human_approval(self, state: AgentState) -> AgentState:
        """Proper agentic HITL with interrupt() from langgraph.types"""
        print("\n" + "="*60)
        print(f"📋 Proposed commit message:")
        print(f"   {state['commit_message']}")
        print("="*60)
        
        # Use proper LangGraph interrupt() from langgraph.types
        decision = interrupt({
            "type": "commit_approval",
            "reason": "AI generated a commit message that needs human approval",
            "commit_message": state["commit_message"],
            "diff_preview": state["diff"][:500] + "..." if len(state["diff"]) > 500 else state["diff"],
            "instruction": "Approve, reject, or edit this commit message"
        })
        
        # Process the human decision
        if decision.get("action") == "approve":
            state["approved"] = True
            print("✅ Approved! Proceeding to commit...")
        elif decision.get("action") == "edit":
            state["approved"] = True
            state["commit_message"] = decision.get("commit_message", state["commit_message"])
            print(f"✅ Updated to: {state['commit_message']}")
        else:
            state["approved"] = False
            print("❌ Rejected. Aborting...")
        
        return state
    
    def push_approval(self, state: AgentState) -> AgentState:
        """Proper agentic HITL with interrupt() for push approval"""
        print("\n" + "="*60)
        print(f"🚀 Ready to push to remote repository")
        print(f"   Branch: {self.git_tools.get_current_branch()}")
        print("="*60)
        
        # Use proper LangGraph interrupt() from langgraph.types
        decision = interrupt({
            "type": "push_approval",
            "reason": "Changes are committed locally and ready to push to remote",
            "commit_message": state["commit_message"],
            "branch": self.git_tools.get_current_branch(),
            "instruction": "Approve or reject pushing to remote repository"
        })
        
        # Process the human decision
        if decision.get("action") == "approve":
            state["push_approved"] = True
            print("✅ Approved! Pushing...")
        else:
            state["push_approved"] = False
            print("❌ Push cancelled. Changes are committed locally only.")
        
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
    
    def run_with_approvals(self, thread_id: str = None):
        """Run workflow with proper interrupt handling"""
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        initial_state = {
            "has_changes": False,
            "diff": "",
            "commit_message": "",
            "approved": False,
            "committed": False,
            "push_approved": False,
            "pushed": False,
            "error": "",
            "thread_id": thread_id
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Run the workflow - it will pause at interrupt() calls
        result = self.graph.invoke(initial_state, config=config)
        return result
    
    def get_pending_approval(self, thread_id: str):
        """Get pending approval if workflow is interrupted"""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = self.graph.get_state(config)
            
            if state and state.next:
                # Check if we're at an interrupt point
                if "human_approval" in state.next:
                    return {
                        "type": "commit_approval",
                        "commit_message": state.values.get("commit_message", ""),
                        "instruction": "Please approve, reject, or edit the commit message"
                    }
                elif "push_approval" in state.next:
                    return {
                        "type": "push_approval",
                        "commit_message": state.values.get("commit_message", ""),
                        "instruction": "Please approve or reject pushing to remote repository"
                    }
            
            return None
        except Exception as e:
            print(f"❌ Error getting pending approval: {e}")
            return None
    
    def resume_workflow(self, thread_id: str, approval_data: dict):
        """Resume workflow after human approval"""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            
            # Resume the workflow with the approval decision
            result = self.graph.invoke(approval_data, config=config)
            return result
        except Exception as e:
            print(f"❌ Error resuming workflow: {e}")
            return {"error": str(e)}
    
    def get_workflow_state(self, thread_id: str):
        """Get current workflow state"""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = self.graph.get_state(config)
            return state.values if state else None
        except Exception as e:
            print(f"❌ Error getting workflow state: {e}")
            return None
    
    def start_workflow(self, thread_id: str = None):
        """Start a new workflow"""
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        initial_state = {
            "has_changes": False,
            "diff": "",
            "commit_message": "",
            "approved": False,
            "committed": False,
            "push_approved": False,
            "pushed": False,
            "error": "",
            "thread_id": thread_id
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Start the workflow - it will pause at first interrupt()
            result = self.graph.invoke(initial_state, config=config)
            return {"thread_id": thread_id, "state": result}
        except Exception as e:
            print(f"❌ Error starting workflow: {e}")
            return {"error": str(e)}
    
    # Legacy method for backward compatibility
    def run(self):
        """Simplified run method for testing approval flow"""
        result = {
            "has_changes": False,
            "diff": "",
            "commit_message": "",
            "approved": False,
            "committed": False,
            "push_approved": False,
            "pushed": False,
            "error": ""
        }
        
        try:
            # Step 1: Detect changes
            print("🔍 Detecting changes...")
            has_changes = self.git_tools.has_changes()
            result["has_changes"] = has_changes
            
            if not has_changes:
                print("✅ No changes detected")
                return result
            
            print("📝 Changes detected!")
            
            # Step 2: Analyze diff
            print("📊 Analyzing diff...")
            diff = self.git_tools.get_diff()
            result["diff"] = diff
            
            # Step 3: Generate commit message with security analysis
            print("🤖 Generating commit message with AI...")
            print("🛡️ Running security analysis...")
            issues, security_level, security_summary = self.git_tools.get_security_analysis()
            
            print(f"🔍 Security check: {security_level.value}")
            
            commit_diff = self.git_tools.get_commit_diff()
            commit_message = self.gemini_client.generate_commit_message(commit_diff, security_summary)
            result["commit_message"] = commit_message
            result["security_issues"] = issues
            result["security_level"] = security_level.value  # Convert enum to string
            result["security_summary"] = security_summary
            print(f"✨ Generated: {commit_message}")
            
            # Stop here for approval - don't auto-commit yet
            print("⏸️ Workflow paused for human approval...")
            return result
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Error: {e}")
            return result


# Helper functions for creating approval responses
def create_commit_approval_response(action: Literal["approve", "reject", "edit"], commit_message: str = None):
    """Helper to create commit approval response"""
    response = {"action": action}
    if action == "edit" and commit_message:
        response["commit_message"] = commit_message
    return response


def create_push_approval_response(action: Literal["approve", "reject"]):
    """Helper to create push approval response"""
    return {"action": action}