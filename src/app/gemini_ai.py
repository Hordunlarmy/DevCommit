#!/usr/bin/env python
"""Generate a git commit message using Gemini AI"""


import google.generativeai as genai

from .. import Logger, config
from .prompt import generate_prompt

logger_instance = Logger("__main__")
logger = logger_instance.get_logger()


def generateCommitMessage(diff: str) -> str:
    """Return a generated commit message using Gemini AI"""

    genai.configure(api_key=config('GEMINI_API_KEY'))
    LOCALE = config('LOCALE')
    COMMIT_TYPE = config('COMMIT_TYPE')

    generation_config = {
        "response_mime_type": "text/plain",
        "max_output_tokens": 8192,
        "top_k": 64,
        "top_p": 0.95,
        "temperature": 5,
    }

    try:
        model = genai.GenerativeModel(
            generation_config=generation_config,
            model_name=config('MODEL_NAME'),
        )

        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [generate_prompt(8192, LOCALE, COMMIT_TYPE)],
                },
            ]
        )
    except Exception as e:
        logger.error(f"Error: {e}")

    response = chat_session.send_message(diff)

    return (response.text)
