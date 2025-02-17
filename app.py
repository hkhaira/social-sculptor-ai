import streamlit as st
from langchain_pipeline import PostTransformer

def main():
    st.set_page_config(
        page_title="SocialSculptor",
        page_icon="✨",
        layout="centered"
    )

    st.title("✨ SocialSculptor")
    st.subheader("Transform your writing into engaging social media posts")

    # Initialize the transformer
    transformer = PostTransformer()

    # API Key handling
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("OpenAI API Key", type="password")
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
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 