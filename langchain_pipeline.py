import os
from pathlib import Path
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from database import Example, init_db, Transformation

class PostTransformer:
    def __init__(self):
        self.llm = None
        self.db_session = init_db()
        self.examples = self._load_examples()

    def set_api_key(self, api_key):
        """Initialize the LLM with the provided API key"""
        os.environ["OPENAI_API_KEY"] = api_key
        self.llm = ChatOpenAI(temperature=0.8, model="gpt-4o-mini")

    def _load_examples(self):
        """Load examples from database"""
        examples = self.db_session.query(Example).all()
        return [example.content for example in examples]

    def add_example(self, content):
        """Add new example to database"""
        example = Example(content=content)
        self.db_session.add(example)
        self.db_session.commit()
        self.examples = self._load_examples()

    def save_transformation(self, original_text, transformed_text, platform):
        """Save transformation history"""
        transformation = Transformation(
            original_text=original_text,
            transformed_text=transformed_text,
            platform=platform
        )
        self.db_session.add(transformation)
        self.db_session.commit()

    def transform_post(self, text, platform):
        """Transform the input text into a platform-specific post"""
        if not self.llm:
            raise ValueError("Please set your OpenAI API key first!")

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert social media content creator for {platform}. 
            Transform the user's text into an engaging post while:
            1. Preserving the original message and tone
            2. Making it more impactful and memorable
            3. Optimizing for {platform}'s best practices
            4. Adding relevant emojis where appropriate
            5. Including appropriate hashtags (for Instagram/Twitter)
            """),
            ("user", text)
        ])

        response = self.llm(prompt.format_messages())
        return response.content 