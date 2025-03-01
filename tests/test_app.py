import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
import os
import sys

# Add the parent directory to the path so we can import the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import main

# Mock session state needs to be updated to handle attribute-style access
class MockSessionState(dict):
    """A mock class that mimics Streamlit's session state with both dict and attribute access"""
    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None
        
    def __setattr__(self, key, value):
        self[key] = value

class TestApp(unittest.TestCase):
    def setUp(self):
        # Mock Streamlit
        self.streamlit_patcher = patch('app.st')
        self.mock_st = self.streamlit_patcher.start()
        
        # Mock PostTransformer
        self.transformer_patcher = patch('app.PostTransformer')
        self.mock_transformer_class = self.transformer_patcher.start()
        self.mock_transformer = MagicMock()
        self.mock_transformer_class.return_value = self.mock_transformer
        
        # Mock session state with our custom class that supports attribute access
        self.mock_session_state = MockSessionState()
        self.mock_st.session_state = self.mock_session_state
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
        self.env_patcher.start()
        
        # Mock load_dotenv
        self.dotenv_patcher = patch('app.load_dotenv')
        self.mock_load_dotenv = self.dotenv_patcher.start()
    
    def tearDown(self):
        self.streamlit_patcher.stop()
        self.transformer_patcher.stop()
        self.env_patcher.stop()
        self.dotenv_patcher.stop()
    
    def test_app_initialization(self):
        # Test that the app initializes correctly
        main()
        
        # Verify load_dotenv was called
        self.mock_load_dotenv.assert_called_once()
        
        # Verify page config was set
        self.mock_st.set_page_config.assert_called_once()
        
        # Verify title was set
        self.mock_st.title.assert_called_with("✨ Social Sculptor")
        
        # Verify transformer was initialized
        self.mock_transformer_class.assert_called_once()
    
    def test_platform_selection(self):
        # Set up session state
        self.mock_session_state["platform"] = "LinkedIn"
        
        # Run the app
        main()
        
        # Verify platform was set on transformer
        self.mock_transformer.set_platform.assert_called_with("LinkedIn")
    
    def test_transform_button_click(self):
        # Set up session state
        self.mock_session_state["platform"] = "LinkedIn"
        
        # Mock the button click
        self.mock_st.button.return_value = True
        
        # Mock the text area input
        self.mock_st.text_area.return_value = "Test input text"
        
        # Mock the transformer response
        self.mock_transformer.transform_post.return_value = "Transformed text"
        
        # Run the app
        main()
        
        # Verify transform_post was called with the right arguments
        self.mock_transformer.transform_post.assert_called_with("Test input text", "LinkedIn")
        
        # Verify success message was shown
        self.mock_st.success.assert_called_with("Your transformed post is ready!")
        
        # Verify save_transformation was called
        self.mock_transformer.save_transformation.assert_called_with("Test input text", "Transformed text")
    
    def test_empty_input_warning(self):
        # Set up session state
        self.mock_session_state["platform"] = "LinkedIn"
        
        # Mock the button click
        self.mock_st.button.return_value = True
        
        # Mock empty text area input
        self.mock_st.text_area.return_value = ""
        
        # Run the app
        main()
        
        # Verify warning was shown
        self.mock_st.warning.assert_called_with("Please enter some text to transform!")
        
        # Verify transform_post was not called
        self.mock_transformer.transform_post.assert_not_called()
    
    def test_add_example(self):
        # Set up session state
        self.mock_session_state["platform"] = "LinkedIn"
        self.mock_session_state["example_text"] = "Test example"
        
        # Mock the sidebar context manager
        self.mock_st.sidebar.__enter__ = MagicMock(return_value=self.mock_st)
        self.mock_st.sidebar.__exit__ = MagicMock(return_value=None)
        
        # Mock the Add Example button click
        # We need to make the first button return False (Transform button) and the second True (Add Example)
        self.mock_st.button.side_effect = [False, True]
        
        # Run the app
        main()
        
        # Verify add_example was called with the right argument
        self.mock_transformer.add_example.assert_called_with("Test example")
        
        # Verify session state was updated
        self.assertEqual(self.mock_session_state["clear_text"], True)
        self.assertEqual(self.mock_session_state["show_success"], True)
        
        # Verify rerun was called
        self.mock_st.rerun.assert_called_once()

if __name__ == '__main__':
    unittest.main() 