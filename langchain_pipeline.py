import os
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from database import init_db, LinkedInExample, TwitterExample, InstagramExample, LinkedInTransformation, TwitterTransformation, InstagramTransformation
import uuid
from huggingface_dataset import HuggingFaceDatasetManager


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
        # Initialize HF dataset manager
        self.hf_dataset_manager = HuggingFaceDatasetManager()

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
        """Save transformation to platform-specific table and Hugging Face dataset"""
        if not self.current_platform:
            raise ValueError("Please select a platform first!")

        # Save to local database
        transformation_model = self.PLATFORM_MODELS[self.current_platform][1]
        transformation_id = str(uuid.uuid4())
        transformation = transformation_model(
            id=transformation_id,
            original_text=original_text,
            transformed_text=transformed_text)
        self.db_session.add(transformation)
        self.db_session.commit()
        
        # Save to Hugging Face dataset with metadata
        metadata = {
            "id": transformation_id,
            "model": self.llm.model_name if self.llm else "unknown",
            "temperature": self.llm.temperature if self.llm else 0.0,
            "example_count": len(self.examples)
        }
        
        try:
            self.hf_dataset_manager.add_transformation(
                platform=self.current_platform,
                original_text=original_text,
                transformed_text=transformed_text,
                metadata=metadata
            )
        except Exception as e:
            print(f"Warning: Failed to save to Hugging Face dataset: {str(e)}")

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

        prompt = ChatPromptTemplate.from_messages([("system", f"""
            You are a highly skilled and experienced social media content creator specializing in crafting engaging and impactful posts for {platform}. Your expertise lies in transforming user-provided text into optimized content that aligns with the best practices of {platform}.

            Follow these guidelines meticulously:
            1 Preserve the Original Message & Tone: Maintain the user's intent, ensuring that the core message and tone remain intact.

            2 Enhance Impact & Memorability: Refine the content to make it more engaging, persuasive, and shareable. Utilize compelling hooks, storytelling techniques, and audience-relevant language.

            3 Optimize for {platform} Best Practices: Structure the content according to what works best on {platform}, including sentence length, readability, and formatting that enhances engagement.

            4 Prioritize Content Quality & Relevance: Ensure that the post is well-structured, free of errors, and tailored to resonate with the target audience for {platform}. Incorporate strategic keywords to improve visibility and engagement.

            5 Incorporate Relevant Emojis for {platform}: Use emojis sparingly and strategically to enhance readability and emotional appeal without overloading the content.

            6 Strictly Avoid Hashtags & Mentions: Do not include any hashtags or mentions in the response.

            7 Remove Any Markdown Formatting: Ensure the final output contains no markdown elements such as asterisks, underscores, or other formatting symbols.

            8 Keep the Post Easy to Read & Understand: Write in a clear, engaging, and concise manner, making the content accessible to a broad audience.

            9 Adapt Content to Platform-Specific Trends: If applicable, subtly align the content with trending styles, formats, or themes relevant to {platform} while maintaining authenticity.

            10 Encourage Engagement & Action: Where appropriate, include a natural call-to-action (CTA) that encourages likes, comments, shares, or interactions.

            11. Adapt Content length to Platform: Ensure the post length is optimized for {platform} to maximize engagement and readability.

            Additional Instructions:
            Do not add unnecessary fluff; keep the content concise yet powerful.
            If the original text is too long, summarize it while keeping the core message intact.
            If the text lacks clarity, improve its coherence without altering its meaning.
            Transform the user's input into an engaging, impactful, and platform-optimized post that captures attention and encourages interaction.

            Take a deep breath and work on this problem step-by-step. 
            You have the skills and creativity needed to excel in this task. 
            Begin by analyzing the original text, identifying its strengths and weaknesses, and envisioning how it can be enhanced to resonate with the target audience on {platform}. 
            Then, craft a compelling response that aligns with the best practices of {platform} and showcases your expertise in content creation.
            """), ("user", text)])

        response = self.llm(prompt.format_messages())
        return response.content
