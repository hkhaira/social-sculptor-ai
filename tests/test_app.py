import unittest
from unittest.mock import patch, MagicMock, call, ANY
import streamlit as st
import os
import sys

# Add the parent directory to the path so we can import the app module
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        self.mock_session_state[
            "platform"] = "LinkedIn"  # Set default platform
        self.mock_session_state["clear_text"] = False
        self.mock_session_state["show_success"] = False
        self.mock_st.session_state = self.mock_session_state

        # Mock environment variables
        self.env_patcher = patch.dict(os.environ,
                                      {"OPENAI_API_KEY": "test-api-key"})
        self.env_patcher.start()

        # Mock load_dotenv
        self.dotenv_patcher = patch('app.load_dotenv')
        self.mock_load_dotenv = self.dotenv_patcher.start()

        # Mock selectbox to return the platform string directly
        self.mock_st.selectbox.return_value = "LinkedIn"

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

        # Return main text input for the primary text_area (no key) and example text for sidebar if key provided
        self.mock_st.text_area.side_effect = lambda *args, **kwargs: "Test input text" if kwargs.get(
            "key") is None else "Test example"

        # Mock the transformer response
        self.mock_transformer.transform_post.return_value = "Transformed text"

        # Mock the button to return True for "Transform ✨"
        self.mock_st.button.side_effect = lambda label, *args, **kwargs: True if label == "Transform ✨" else False

        # Run the app
        main()

        # Verify transform_post was called with the right arguments
        self.mock_transformer.transform_post.assert_called_with(
            "Test input text", "LinkedIn")

        # Verify success message was shown
        self.mock_st.success.assert_called_with(
            "Your transformed post is ready!")

    def test_empty_input_warning(self):
        # Set up session state
        self.mock_session_state["platform"] = "LinkedIn"

        # Return empty string for the main text area input
        self.mock_st.text_area.side_effect = lambda *args, **kwargs: "" if kwargs.get(
            "key") is None else "Test example"

        # Mock the button to return True for "Transform ✨"
        self.mock_st.button.side_effect = lambda label, *args, **kwargs: True if label == "Transform ✨" else False

        # Run the app
        main()

        # Verify warning was shown for empty input
        self.mock_st.warning.assert_called_with(ANY)

        # Verify transform_post was not called
        self.mock_transformer.transform_post.assert_not_called()

    def test_add_example(self):
        # Set up session state
        self.mock_session_state["platform"] = "LinkedIn"
        self.mock_session_state["example_text"] = "Test example"

        # Instead of mocking st.sidebar, set text_area to return the example text when key is "example_text"
        self.mock_st.text_area.side_effect = lambda *args, **kwargs: "Test example" if kwargs.get(
            "key") == "example_text" else "Test input text"

        # Mock the button to return True for "Add Example" and False for others
        self.mock_st.button.side_effect = lambda label, *args, **kwargs: True if label == "Add Example" else False

        # Run the app
        main()

        # Verify add_example was called with the right argument
        self.mock_transformer.add_example.assert_called_with("Test example")

        # Verify session state was updated
        self.assertEqual(self.mock_session_state["clear_text"], True)
        self.assertEqual(self.mock_session_state["show_success"], True)


if __name__ == '__main__':
    unittest.main()
