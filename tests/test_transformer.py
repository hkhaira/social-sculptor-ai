import unittest
import os
from unittest.mock import patch, MagicMock
import uuid

from langchain_pipeline import PostTransformer
from database import (
    LinkedInExample, TwitterExample, InstagramExample,
    LinkedInTransformation, TwitterTransformation, InstagramTransformation
)

class TestPostTransformer(unittest.TestCase):
    def setUp(self):
        # Create a mock database session
        self.mock_session = MagicMock()
        
        # Patch the init_db function to return our mock session
        self.patcher = patch('langchain_pipeline.init_db', return_value=self.mock_session)
        self.mock_init_db = self.patcher.start()
        
        # Create the transformer with the mocked session
        self.transformer = PostTransformer()
        
        # Mock UUID generation for deterministic testing
        self.uuid_patcher = patch('uuid.uuid4', return_value='test-uuid')
        self.mock_uuid = self.uuid_patcher.start()
    
    def tearDown(self):
        self.patcher.stop()
        self.uuid_patcher.stop()
    
    def test_set_platform(self):
        # Test setting the platform
        self.transformer.set_platform("LinkedIn")
        self.assertEqual(self.transformer.current_platform, "LinkedIn")
        
        # Verify _load_examples was called
        self.mock_session.query.assert_called_once()
    
    def test_add_example_linkedin(self):
        # Test adding a LinkedIn example
        self.transformer.set_platform("LinkedIn")
        self.transformer.add_example("Test LinkedIn example")
        
        # Verify the example was added to the session
        self.mock_session.add.assert_called_once()
        added_example = self.mock_session.add.call_args[0][0]
        self.assertIsInstance(added_example, LinkedInExample)
        self.assertEqual(added_example.content, "Test LinkedIn example")
        self.assertEqual(added_example.id, "test-uuid")
        
        # Verify commit was called
        self.mock_session.commit.assert_called_once()
    
    def test_add_example_twitter(self):
        # Test adding a Twitter example
        self.transformer.set_platform("Twitter")
        self.transformer.add_example("Test Twitter example")
        
        # Verify the example was added to the session
        self.mock_session.add.assert_called_once()
        added_example = self.mock_session.add.call_args[0][0]
        self.assertIsInstance(added_example, TwitterExample)
        self.assertEqual(added_example.content, "Test Twitter example")
    
    def test_add_example_instagram(self):
        # Test adding an Instagram example
        self.transformer.set_platform("Instagram")
        self.transformer.add_example("Test Instagram example")
        
        # Verify the example was added to the session
        self.mock_session.add.assert_called_once()
        added_example = self.mock_session.add.call_args[0][0]
        self.assertIsInstance(added_example, InstagramExample)
        self.assertEqual(added_example.content, "Test Instagram example")
    
    def test_add_example_empty_content(self):
        # Test adding an example with empty content
        self.transformer.set_platform("LinkedIn")
        with self.assertRaises(ValueError):
            self.transformer.add_example("")
    
    def test_add_example_no_platform(self):
        # Test adding an example without setting platform
        self.transformer.current_platform = None
        with self.assertRaises(ValueError):
            self.transformer.add_example("Test example")
    
    def test_save_transformation(self):
        # Test saving a transformation
        self.transformer.set_platform("LinkedIn")
        self.transformer.save_transformation("Original text", "Transformed text")
        
        # Verify the transformation was added to the session
        self.mock_session.add.assert_called_once()
        added_transformation = self.mock_session.add.call_args[0][0]
        self.assertIsInstance(added_transformation, LinkedInTransformation)
        self.assertEqual(added_transformation.original_text, "Original text")
        self.assertEqual(added_transformation.transformed_text, "Transformed text")
        
        # Verify commit was called
        self.mock_session.commit.assert_called_once()
    
    def test_set_api_key(self):
        # Test setting the API key
        with patch.dict(os.environ, {}, clear=True):
            self.transformer.set_api_key("test-api-key", 0.5)
            self.assertEqual(os.environ.get("OPENAI_API_KEY"), "test-api-key")
            self.assertIsNotNone(self.transformer.llm)
    
    @patch('langchain_pipeline.ChatOpenAI')
    def test_transform_post(self, mock_chat_openai):
        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.content = "Transformed post content"
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = mock_response
        mock_chat_openai.return_value = mock_llm_instance
        
        # Set up the transformer
        self.transformer.set_platform("LinkedIn")
        self.transformer.llm = mock_llm_instance
        
        # Test transforming a post
        result = self.transformer.transform_post("Original post", "LinkedIn")
        self.assertEqual(result, "Transformed post content")
    
    def test_transform_post_no_llm(self):
        # Test transforming a post without setting the LLM
        self.transformer.set_platform("LinkedIn")
        self.transformer.llm = None
        with self.assertRaises(ValueError):
            self.transformer.transform_post("Original post", "LinkedIn")

if __name__ == '__main__':
    unittest.main() 