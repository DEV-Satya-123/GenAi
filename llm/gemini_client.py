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
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.3
        )
        self.parser = PydanticOutputParser(pydantic_object=CommitMessage)
    
    def generate_commit_message(self, diff: str) -> str:
        prompt = PromptTemplate(
            template="""You are an expert at writing clear, concise git commit messages.
Analyze the following git diff and generate a meaningful commit message.

Follow these guidelines:
- Use conventional commit format (feat:, fix:, docs:, refactor:, etc.)
- Be specific about what changed
- Keep it under 72 characters if possible
- Focus on the "what" and "why", not the "how"

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
