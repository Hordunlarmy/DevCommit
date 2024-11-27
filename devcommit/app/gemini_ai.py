#!/usr/bin/env python
"""Generate a git commit message using Gemini AI"""


import google.generativeai as genai

from devcommit.utils.logger import Logger, config

from .prompt import generate_prompt

logger_instance = Logger("__gemini_ai__")
logger = logger_instance.get_logger()


def generateCommitMessage(diff: str) -> str:
    """Return a generated commit message using Gemini AI"""
    try:
        # Configure API Key
        api_key = config("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set.")
        genai.configure(api_key=api_key)

        # Load Configuration Values
        max_no = config("MAX_NO", default=1)
        locale = config("LOCALE", default="en-US")
        commit_type = config("COMMIT_TYPE", default="general")
        model_name = config("MODEL_NAME", default="gemini-1.5-flash")
        if not model_name:
            raise ValueError("MODEL_NAME not set.")

        generation_config = {
            "response_mime_type": "text/plain",
            "max_output_tokens": 8192,
            "top_k": 20,
            "top_p": 0.8,
            "temperature": 0.5,
        }

        # Create Model and Start Chat
        model = genai.GenerativeModel(
            generation_config=generation_config,
            model_name=model_name,
        )

        prompt_text = generate_prompt(8192, max_no, locale, commit_type)
        # logger.info(f"Prompt: {prompt_text}")
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [prompt_text],
                },
            ]
        )

        # Send the Diff as Message
        # logger.info(f"Diff: {diff}")
        response = chat_session.send_message(diff)
        if response and hasattr(response, "text"):
            return response.text.strip()
        else:
            logger.error("No valid response received from Gemini AI.")
            return "No valid commit message generated."

    except Exception as e:
        logger.error(f"Error generating commit message: {e}")
        return f"Error generating commit message: {str(e)}"
