#!/usr/bin/env python3
"""
Graph Visualization Script for AI Git Automation Agent
Run this to see the workflow structure without needing Jupyter
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    has_changes: bool
    diff: str
    commit_message: str
    approved: bool
    committed: bool
    push_approved: bool
    pushed: bool
    error: str


def detect_changes(state: AgentState) -> AgentState:
    print("🔍 Detecting changes...")
    state["has_changes"] = True
    return state


def analyze_diff(state: AgentState) -> AgentState:
    print("📊 Analyzing diff...")
    state["diff"] = "Mock diff"
    return state


def generate_commit_message(state: AgentState) -> AgentState:
    print("🤖 Generating commit message...")
    state["commit_message"] = "feat: add new feature"
    return state


def human_approval(state: AgentState) -> AgentState:
    print("✋ Awaiting commit approval...")
    state["approved"] = True
    return state


def git_commit(state: AgentState) -> AgentState:
    print("💾 Committing...")
    state["committed"] = True
    return state


def push_approval(state: AgentState) -> AgentState:
    print("✋ Awaiting push approval...")
    state["push_approved"] = True
    return state


def git_push(state: AgentState) -> AgentState:
    print("🚀 Pushing...")
    state["pushed"] = True
    return state


def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("detect_changes", detect_changes)
    workflow.add_node("analyze_diff", analyze_diff)
    workflow.add_node("generate_commit_message", generate_commit_message)
    workflow.add_node("human_approval", human_approval)
    workflow.add_node("git_commit", git_commit)
    workflow.add_node("push_approval", push_approval)
    workflow.add_node("git_push", git_push)
    
    # Set entry point
    workflow.set_entry_point("detect_changes")
    
    # Add edges
    workflow.add_conditional_edges(
        "detect_changes",
        lambda x: "analyze" if x["has_changes"] else "end",
        {"analyze": "analyze_diff", "end": END}
    )
    
    workflow.add_edge("analyze_diff", "generate_commit_message")
    workflow.add_edge("generate_commit_message", "human_approval")
    
    workflow.add_conditional_edges(
        "human_approval",
        lambda x: "commit" if x["approved"] else "end",
        {"commit": "git_commit", "end": END}
    )
    
    workflow.add_edge("git_commit", "push_approval")
    
    workflow.add_conditional_edges(
        "push_approval",
        lambda x: "push" if x["push_approved"] else "end",
        {"push": "git_push", "end": END}
    )
    
    workflow.add_edge("git_push", END)
    
    return workflow.compile()


def print_workflow_diagram():
    print("""
╔════════════════════════════════════════════════════════════════╗
║           AI GIT AUTOMATION AGENT WORKFLOW                     ║
║              (Dual Human-in-the-Loop)                          ║
╚════════════════════════════════════════════════════════════════╝

                        START
                          ↓
                  🔍 detect_changes
                          ↓
                ┌─────────┴─────────┐
          has_changes?          no changes
                ↓                   ↓
          📊 analyze_diff          END
                ↓
       🤖 generate_commit_message
                ↓
       ✋ human_approval (commit?)
                ↓
          ┌─────┴─────┐
      approved?    rejected
          ↓            ↓
     💾 git_commit    END
          ↓
     ✋ push_approval (push?)
          ↓
          ┌─────┴─────┐
      approved?    rejected
          ↓            ↓
     🚀 git_push     END
          ↓
         END

╔════════════════════════════════════════════════════════════════╗
║ WORKFLOW NODES:                                                ║
╠════════════════════════════════════════════════════════════════╣
║ 1. detect_changes          - Check for uncommitted changes    ║
║ 2. analyze_diff            - Read git diff                    ║
║ 3. generate_commit_message - AI generates commit message      ║
║ 4. human_approval          - User approves/edits message      ║
║ 5. git_commit              - Commit changes locally           ║
║ 6. push_approval           - User approves push               ║
║ 7. git_push                - Push to remote repository        ║
╚════════════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════════════╗
║ DECISION POINTS:                                               ║
╠════════════════════════════════════════════════════════════════╣
║ • No changes detected      → END                               ║
║ • Commit rejected          → END (no commit)                   ║
║ • Push rejected            → END (committed locally only)      ║
║ • All approved             → Complete workflow                 ║
╚════════════════════════════════════════════════════════════════╝
    """)


def print_mermaid_diagram():
    print("\n" + "="*70)
    print("MERMAID DIAGRAM (Copy to https://mermaid.live)")
    print("="*70)
    print("""
graph TD
    START([START]) --> A[🔍 detect_changes]
    A -->|has changes| B[📊 analyze_diff]
    A -->|no changes| END1([END])
    B --> C[🤖 generate_commit_message]
    C --> D[✋ human_approval]
    D -->|approved| E[💾 git_commit]
    D -->|rejected| END2([END])
    E --> F[✋ push_approval]
    F -->|approved| G[🚀 git_push]
    F -->|rejected| END3([END])
    G --> END4([END])
    
    style START fill:#90EE90
    style END1 fill:#FFB6C1
    style END2 fill:#FFB6C1
    style END3 fill:#FFB6C1
    style END4 fill:#90EE90
    style D fill:#FFD700
    style F fill:#FFD700
    """)
    print("="*70)


def run_demo():
    print("\n🤖 Building and testing the graph...\n")
    
    graph = build_graph()
    
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
    
    print("🚀 Running workflow with mock data...\n")
    print("="*70)
    result = graph.invoke(initial_state)
    print("="*70)
    
    print("\n📋 Final State:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Graph executed successfully!")


def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        AI GIT AUTOMATION AGENT - GRAPH VISUALIZER              ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    print_workflow_diagram()
    print_mermaid_diagram()
    
    response = input("\n🎯 Run a demo execution? (y/n): ").strip().lower()
    if response == 'y':
        run_demo()
    
    print("\n👋 Done! Use this visualization to understand the workflow.\n")


if __name__ == "__main__":
    main()
