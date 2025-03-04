---
title: Social Sculptor
emoji: ✨
colorFrom: red
colorTo: purple
sdk: streamlit
sdk_version: 1.42.1
app_file: app.py
pinned: false
license: mit
short_description: Transform your writing into engaging social media posts
---
<!-- The YAML above is required for Hugging Face Spaces. -->

# ✨ Social Sculptor

[![Demo](https://img.shields.io/badge/Demo-Hugging%20Face-yellow)](https://huggingface.co/spaces/hkhaira/social-sculptor)

Transform your writing into engaging social media posts using AI.

## Features

- Transform plain text into platform-optimized social media posts
- Support for multiple platforms (LinkedIn, Twitter, Instagram)
- AI-powered content enhancement while preserving original tone
- Platform-specific post history and examples
- Easy-to-use web interface
- Persistent storage of transformations and examples

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd social-sculptor
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On Unix or MacOS
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment:
   - Create a `.env` file in the project root
   - Add your OpenAI API key (optional, can also be entered in UI):
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Enter your OpenAI API key in the sidebar (if not set in .env)
2. Enter your text in the input area
3. Select your target platform (LinkedIn, Twitter, or Instagram)
4. Click "Transform" to generate an optimized post
5. View your transformation history in the expander below
6. Copy and use the transformed post on your chosen platform

## Admin Features

- Access example management through the sidebar
- Add new platform-specific examples to improve transformations
- View transformation history for each platform

## Data Storage

- All transformations and examples are automatically stored in a local SQLite database
- The database file (`social_sculptor.db`) is created in your project directory
- To start fresh, simply delete the database file (it will be recreated on next run)


## Running Tests

To run the test suite, execute the following command in your terminal:
```bash
pytest tests/
```

## License

[MIT - LICENSE](LICENSE)