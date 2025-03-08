import os
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from database import init_db, LinkedInExample, TwitterExample, InstagramExample, LinkedInTransformation, TwitterTransformation, InstagramTransformation
import uuid


class PostTransformer:
    PLATFORM_MODELS = {
        'LinkedIn': (LinkedInExample, LinkedInTransformation),
        'Twitter': (TwitterExample, TwitterTransformation),
        'Instagram': (InstagramExample, InstagramTransformation)
    }

    def __init__(self):
        self.llm = None
        self.db_session = init_db()
        self.current_platform = None
        self.examples = []

    def set_platform(self, platform):
        """Update current platform and load relevant examples"""
        self.current_platform = platform
        self.examples = self._load_examples()

    def _load_examples(self):
        """Load platform-specific examples"""
        if not self.current_platform:
            return []

        example_model = self.PLATFORM_MODELS[self.current_platform][0]
        examples = self.db_session.query(example_model).all()
        return [example.content for example in examples]

    def add_example(self, content):
        """Add new example to platform-specific table"""
        if not self.current_platform:
            raise ValueError("Please select a platform first!")

        if not content or not content.strip():
            raise ValueError("Example content cannot be empty!")

        try:
            example_model = self.PLATFORM_MODELS[self.current_platform][0]
            example = example_model(id=str(uuid.uuid4()),
                                    content=content.strip())
            self.db_session.add(example)
            self.db_session.commit()
            self.examples = self._load_examples()
            return True
        except Exception as e:
            self.db_session.rollback()
            raise Exception(f"Error adding example: {str(e)}")

    def save_transformation(self, original_text, transformed_text):
        """Save transformation to platform-specific table"""
        if not self.current_platform:
            raise ValueError("Please select a platform first!")

        transformation_model = self.PLATFORM_MODELS[self.current_platform][1]
        transformation = transformation_model(
            id=str(uuid.uuid4()),
            original_text=original_text,
            transformed_text=transformed_text)
        self.db_session.add(transformation)
        self.db_session.commit()

    def set_api_key(
            self,
            api_key,
            temperature=0.8):  # modified signature to include temperature
        """Initialize the LLM with the provided API key and temperature"""
        os.environ["OPENAI_API_KEY"] = api_key
        self.llm = ChatOpenAI(temperature=temperature, model="gpt-4o-mini")

    def transform_post(self, text, platform):
        """Transform the input text into a platform-specific post"""
        if not self.llm:
            raise ValueError("Please set your OpenAI API key first!")

        prompt = ChatPromptTemplate.from_messages([(
            "system",
            f"""You are an expert social media content creator for {platform}. 
            Transform the user's text into an engaging post while:
            1. Preserving the original message and tone
            2. Making it more impactful and memorable
            3. Optimizing for {platform}'s best practices
            4. Adding relevant emojis where appropriate
            5. Including appropriate hashtags (for Instagram/Twitter)
            6. Removing any markdown text formatting
            """), ("user", text)])

        response = self.llm(prompt.format_messages())
        return response.content
