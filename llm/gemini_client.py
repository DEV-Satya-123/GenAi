from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from config import GEMINI_API_KEY
import json


class CommitMessage(BaseModel):
    commit_message: str = Field(description="A clear, concise commit message describing the changes")


class GeminiClient:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=GEMINI_API_KEY,
            temperature=0.3
        )
    
    def generate_commit_message(self, diff: str, security_summary: str = None) -> str:
        prompt = PromptTemplate(
            template="""You are an expert software developer writing git commit messages.
Analyze the git diff and generate ONE concise commit message that describes the main purpose of the changes.

IMPORTANT RULES:
- Use conventional commit format: type(scope): description
- Types: feat, fix, docs, style, refactor, test, chore
- Keep under 50 characters total
- Focus on WHAT was changed and WHY, not HOW
- Write in imperative mood (add, fix, update, remove)
- Be specific about the feature/component changed

ANALYZE THE DIFF FOR:
- New files added → "feat: add [component]"
- Bug fixes → "fix: resolve [issue]"
- Code improvements → "refactor: improve [component]"
- Documentation → "docs: update [section]"
- Configuration → "chore: update [config]"
- UI/styling → "style: improve [component]"

Examples:
- "feat: add user login system"
- "fix: resolve database connection issue"
- "refactor: optimize query performance"
- "docs: add API documentation"
- "chore: update dependencies"

Git Diff:
{diff}

{security_info}

Return ONLY a JSON object with this format:
{{"commit_message": "your commit message here"}}
""",
            input_variables=["diff", "security_info"]
        )
        
        # Include security information if provided
        security_info = ""
        if security_summary:
            security_info = f"\nSECURITY ANALYSIS:\n{security_summary}\n"
        
        chain = prompt | self.llm
        result = chain.invoke({"diff": diff, "security_info": security_info})
        
        # Parse the response
        try:
            # Try to extract JSON from the response
            content = result.content if hasattr(result, 'content') else str(result)
            
            # Find JSON in the response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                parsed = json.loads(json_str)
                return parsed.get('commit_message', content.strip())
            else:
                # Fallback: return the content as-is
                return content.strip()
        except:
            # If parsing fails, return the raw content
            return result.content if hasattr(result, 'content') else str(result)
