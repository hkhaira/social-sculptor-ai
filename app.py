import streamlit as st
from langchain_pipeline import PostTransformer
import os
from dotenv import load_dotenv
import threading


def main():
    # Load environment variables
    load_dotenv()
    default_api_key = os.getenv("OPENAI_API_KEY", "")
    api_key = default_api_key

    st.set_page_config(
        page_title="Social Sculptor",
        page_icon="✨",
        layout="centered",
        initial_sidebar_state="collapsed"  # set sidebar closed by default
    )

    st.title("✨ Social Sculptor")
    st.subheader("Transform your writing into engaging social media posts")

    # Initialize the transformer
    transformer = PostTransformer()

    # Initialize platform in session state if not present
    if "platform" not in st.session_state:
        st.session_state.platform = "LinkedIn"

    if "show_success" not in st.session_state:
        st.session_state.show_success = False

    def update_platform():
        st.session_state.platform = st.session_state.platform_selector

    # Platform selection with callback
    platform = st.selectbox("Select target platform:",
                            ["LinkedIn", "Twitter", "Instagram"],
                            key="platform_selector",
                            on_change=update_platform,
                            index=["LinkedIn", "Twitter", "Instagram"
                                   ].index(st.session_state.platform))

    # Update transformer platform
    transformer.set_platform(st.session_state.platform)

    with st.sidebar:
        # st.header("SETTINGS", anchor=False)
        st.markdown("<h1 style='text-align: center;'>Settings</h1>",
                    unsafe_allow_html=True)

        # Add temperature slider in sidebar
        st.subheader("LLM Temperature")
        temperature = st.slider(
            "More conservative (0.0) to more creative (1.0)",
            min_value=0.0,
            max_value=1.0,
            value=0.88,
            step=0.01)

        st.divider()
        st.subheader("Training Examples")

        # Check and clear if needed - BEFORE creating the text area
        if "clear_text" in st.session_state and st.session_state.clear_text:
            st.session_state.example_text = ""
            st.session_state.clear_text = False

        # Initialize example_text if not present
        if "example_text" not in st.session_state:
            st.session_state.example_text = ""

        # Create the text area
        new_example = st.text_area(
            "Your Example:",
            key="example_text",
            help=
            "Provide examples to train the AI on your writing style for generating improved posts."
        )

        # Handle the button click and state updates
        if st.button("Add Example"):
            st.session_state.show_success = False  # Reset success message
            if not new_example or not new_example.strip():
                st.error("Please enter some text for the example!")
            else:
                try:
                    transformer.add_example(new_example)
                    st.session_state.clear_text = True
                    st.session_state.show_success = True
                    try:
                        st.rerun()
                    except Exception:
                        pass  # Ignore rerun exception during testing
                except Exception as e:
                    st.error(f"Failed to add example: {str(e)}")

        # Show success message
        if st.session_state.show_success:
            st.success("Example added successfully!")

        example_model = transformer.PLATFORM_MODELS[platform][0]
        all_examples = transformer.db_session.query(example_model).all()
        top5_examples = transformer.db_session.query(example_model).order_by(
            example_model.created_at.desc()).limit(5).all()
        st.write(f"Total examples for {platform}: **{len(all_examples)}**")
        # Add this after the Add Example button (temporary for debugging)
        with st.expander("Preview Examples"):
            for ex in top5_examples:
                # Get first two lines of content
                preview_lines = ex.content.split('\n')[:2]
                st.text('\n'.join(preview_lines))
                st.divider()

        st.divider()
        st.subheader("Hugging Face Dataset")
        
        # Show dataset stats
        if st.button("Sync Dataset with Hugging Face"):
            with st.spinner("Syncing dataset..."):
                try:
                    transformer.hf_dataset_manager.push_to_hub()
                    st.success("Dataset successfully pushed to Hugging Face!")
                except Exception as e:
                    st.error(f"Failed to sync dataset: {str(e)}")
        
        # Option for automatic syncing
        enable_auto_sync = st.toggle("Enable automatic syncing", value=False)
        
        if enable_auto_sync:
            st.info("Dataset will be automatically synced after each transformation")

    # Set the API key using the environment variable
    transformer.set_api_key(api_key, temperature)  # pass temperature value

    # Main interface
    user_text = st.text_area("Enter your text:",
                             height=150,
                             placeholder="Paste your text here...")

    if st.button("Transform ✨", disabled=not api_key):
        if not user_text:
            st.warning("Please enter some text to transform!")
            return

        with st.spinner("Transforming your post..."):
            try:
                transformed_post = transformer.transform_post(user_text, platform)
                st.success("Your transformed post is ready!")
                
                # Auto-sync if enabled
                if "enable_auto_sync" in st.session_state and st.session_state.enable_auto_sync:
                    with st.spinner("Syncing with Hugging Face..."):
                        def sync_in_background():
                            try:
                                transformer.hf_dataset_manager.push_to_hub()
                            except Exception as e:
                                print(f"Auto-sync failed: {str(e)}")
                        
                        # Run sync in background thread to avoid blocking UI
                        threading.Thread(target=sync_in_background).start()
                
                # Calculate dynamic height based on content length
                # Assuming average of 50 characters per line, 20px per line
                min_height = 150
                max_height = 600
                content_length = len(transformed_post)
                calculated_height = min(
                    max(min_height, (content_length // 50) * 20), max_height)

                # Create a container to maintain state
                result_container = st.container()

                with result_container:
                    st.subheader("Transformed Post:")
                    # Add custom CSS to control height
                    st.markdown(f"""
                        <style>
                        .stCodeBlock {{
                            max-height: {calculated_height}px !important;
                        }}
                        .stCodeBlock pre {{
                            white-space: pre-wrap !important;
                            word-wrap: break-word !important;
                            overflow-x: hidden !important;
                        }}
                        code {{
                            white-space: pre-wrap !important;
                            word-wrap: break-word !important;
                        }}
                        </style>
                        """,
                                unsafe_allow_html=True)
                    st.code(transformed_post, language=None)

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
