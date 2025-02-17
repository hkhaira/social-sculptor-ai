import streamlit as st
from langchain_pipeline import PostTransformer
from database import Transformation
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    default_api_key = os.getenv("OPENAI_API_KEY", "")

    st.set_page_config(
        page_title="SocialSculptor",
        page_icon="✨",
        layout="centered"
    )

    st.title("✨ Social Sculptor")
    st.subheader("Transform your writing into engaging social media posts")

    # Initialize the transformer
    transformer = PostTransformer()

    # API Key handling
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input(
            "OpenAI API Key", 
            value=default_api_key,
            type="password",
            help="Enter your OpenAI API key. You can also set it in the .env file."
        )
        if api_key:
            transformer.set_api_key(api_key)

    # Main interface
    user_text = st.text_area(
        "Enter your text:",
        height=150,
        placeholder="Paste your text here..."
    )

    platform = st.selectbox(
        "Select target platform:",
        ["LinkedIn", "Twitter", "Instagram"]
    )

    if st.button("Transform ✨", disabled=not api_key):
        if not user_text:
            st.warning("Please enter some text to transform!")
            return

        with st.spinner("Transforming your post..."):
            try:
                transformed_post = transformer.transform_post(user_text, platform)
                st.success("Your transformed post is ready!")
                st.text_area("Transformed Post:", value=transformed_post, height=150)
                # Save the transformation
                transformer.save_transformation(user_text, transformed_post, platform)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Add transformation history section
    with st.expander("Transformation History"):
        transformations = transformer.db_session.query(Transformation).order_by(
            Transformation.created_at.desc()
        ).limit(10).all()
        
        for t in transformations:
            st.write(f"**Platform:** {t.platform}")
            st.write("**Original:**")
            st.text(t.original_text)
            st.write("**Transformed:**")
            st.text(t.transformed_text)
            st.write(f"*Created at: {t.created_at}*")
            st.divider()

    # Add example management (for admins)
    with st.sidebar:
        if st.checkbox("Show Example Management"):
            new_example = st.text_area("Add new example:")
            if st.button("Add Example"):
                transformer.add_example(new_example)
                st.success("Example added successfully!")

if __name__ == "__main__":
    main() 