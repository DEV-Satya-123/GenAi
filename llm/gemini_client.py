from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from config import GEMINI_API_KEY


class CommitMessage(BaseModel):
    commit_message: str = Field(description="A clear, concise commit message describing the changes")


class GeminiClient:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=GEMINI_API_KEY,
            temperature=0.3
        )
        self.parser = PydanticOutputParser(pydantic_object=CommitMessage)
    
    def generate_commit_message(self, diff: str) -> str:
        prompt = PromptTemplate(
            template="""You are an expert at writing SHORT, meaningful git commit messages.
Analyze the git diff and generate ONE concise commit message that summarizes ALL changes.

IMPORTANT RULES:
- Use conventional commit format (feat:, fix:, docs:, refactor:, chore:, style:)
- Write ONE single message for ALL changes combined
- Keep it under 50 characters
- Be specific but brief
- Focus on the main change, not every detail
- DO NOT list multiple changes separately

Examples of GOOD messages:
- "feat: add user authentication"
- "fix: resolve login bug"
- "docs: update README"
- "refactor: simplify auth logic"

Examples of BAD messages (too detailed):
- "feat: add login.py, update auth.py, modify config.py"
- "fix: fix bug in line 23, update function in line 45"

Git Diff:
{diff}

{format_instructions}
""",
            input_variables=["diff"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        chain = prompt | self.llm | self.parser
        result = chain.invoke({"diff": diff})
        return result.commit_message
