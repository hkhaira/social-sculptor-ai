import streamlit as st
from langchain_pipeline import PostTransformer
import os
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()
    default_api_key = os.getenv("OPENAI_API_KEY", "")

    # Set api_key from the environment variable
    api_key = default_api_key

    st.set_page_config(
        page_title="Social Sculptor",
        page_icon="✨",
        layout="centered",
        initial_sidebar_state="collapsed"  # set sidebar closed by default
    )

    st.title("✨ Social Sculptor")
    st.subheader("Transform your writing into engaging social media posts")

    # Configuration section in sidebar
    with st.sidebar:
        st.header("Configuration")
        st.subheader("Training Examples")
        
        # Use session state to manage the text area value
        if "example_text" not in st.session_state:
            st.session_state.example_text = ""
        
        new_example = st.text_area(
            "Your Example:",
            value=st.session_state.example_text,
            help="Provide examples to train the AI on your writing style for generating improved posts."
        )
        
        if st.button("Add Example"):
            if new_example:  # Only add if there's text
                transformer.add_example(new_example)
                st.success("Example added successfully!")
                # Clear the text area by updating session state
                st.session_state.example_text = ""
                # Rerun to show the cleared text area
                st.rerun()

        # Add temperature slider in sidebar
        temperature = st.slider("LLM Temperature",
                                min_value=0.0,
                                max_value=1.0,
                                value=0.8,
                                step=0.01)

    # Initialize the transformer
    transformer = PostTransformer()

    # API Key handling (User input commented out for security)
    # with st.sidebar:
    #     st.header("Configuration")
    #     api_key = st.text_input(
    #         "OpenAI API Key",
    #         value=default_api_key,
    #         type="password",
    #         help="Enter your OpenAI API key. You can also set it in the .env file."
    #     )
    #     if api_key:
    #         transformer.set_api_key(api_key)

    # Set the API key using the environment variable
    transformer.set_api_key(api_key, temperature)  # pass temperature value

    # Main interface
    user_text = st.text_area("Enter your text:",
                             height=150,
                             placeholder="Paste your text here...")

    # Platform selection with auto-reload of examples
    platform = st.selectbox("Select target platform:",
                            ["LinkedIn", "Twitter", "Instagram"])
    # Set the platform immediately after selection
    transformer.set_platform(platform)

    if st.button("Transform ✨", disabled=not api_key):
        if not user_text:
            st.warning("Please enter some text to transform!")
            return

        with st.spinner("Transforming your post..."):
            try:
                transformed_post = transformer.transform_post(
                    user_text, platform)
                st.success("Your transformed post is ready!")
                
                # Calculate dynamic height based on content length
                # Assuming average of 50 characters per line, 20px per line
                min_height = 150
                max_height = 500
                content_length = len(transformed_post)
                calculated_height = min(max(min_height, (content_length // 50) * 20), max_height)
                
                st.text_area("Transformed Post:",
                             value=transformed_post,
                             height=calculated_height)
                # Save the transformation
                transformer.save_transformation(user_text, transformed_post)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Update transformation history to use platform-specific table
    with st.expander("Transformation History"):
        transformation_model = transformer.PLATFORM_MODELS[platform][1]
        transformations = transformer.db_session.query(
            transformation_model).order_by(
                transformation_model.created_at.desc()).limit(10).all()

        for t in transformations:
            st.write("**Original:**")
            st.text(t.original_text)
            st.write("**Transformed:**")
            st.text(t.transformed_text)
            st.write(f"*Created at: {t.created_at}*")
            st.divider()


if __name__ == "__main__":
    main()
