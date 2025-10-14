#!/usr/bin/env python
"""Generate a git commit message using Gemini AI"""

import os
import sys
import warnings

# Suppress warnings from Google libraries BEFORE any imports
os.environ['GRPC_ENABLE_FORK_SUPPORT'] = '1'
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '3'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Redirect stderr during import to suppress ALTS warnings
_stderr_backup = sys.stderr
_devnull = open(os.devnull, 'w')
sys.stderr = _devnull
import google.generativeai as genai
sys.stderr = _stderr_backup
_devnull.close()

warnings.filterwarnings('ignore', message='.*ALTS.*')
warnings.filterwarnings('ignore', category=UserWarning)

from devcommit.utils.logger import Logger, config

from .prompt import generate_prompt

logger_instance = Logger("__gemini_ai__")
logger = logger_instance.get_logger()


def generateCommitMessage(diff: str) -> str:
    """Return a generated commit message using Gemini AI"""
    # Suppress stderr to hide ALTS warnings during API calls
    _stderr = sys.stderr
    _devnull_out = open(os.devnull, 'w')
    
    try:
        # Configure API Key - required, no default
        api_key = config("GEMINI_API_KEY", default=None)
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not set. Please set it as an environment variable "
                "or in your .dcommit file:\n"
                "  export GEMINI_API_KEY='your-api-key'\n"
                "  OR add to ~/.dcommit: GEMINI_API_KEY = your-api-key"
            )
        
        # Suppress stderr during API configuration
        sys.stderr = _devnull_out
        genai.configure(api_key=api_key)
        sys.stderr = _stderr

        # Load Configuration Values with defaults
        max_no = config("MAX_NO", default=1, cast=int)
        locale = config("LOCALE", default="en-US")
        commit_type = config("COMMIT_TYPE", default="general")
        model_name = config("MODEL_NAME", default="gemini-1.5-flash")

        generation_config = {
            "response_mime_type": "text/plain",
            "max_output_tokens": 8192,
            "top_k": 40,
            "top_p": 0.9,
            "temperature": 0.7,
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

        # Send the Diff as Message (suppress stderr during API call)
        # logger.info(f"Diff: {diff}")
        sys.stderr = _devnull_out
        response = chat_session.send_message(diff)
        sys.stderr = _stderr
        
        if response and hasattr(response, "text"):
            return response.text.strip()
        else:
            logger.error("No valid response received from Gemini AI.")
            return "No valid commit message generated."

    except Exception as e:
        logger.error(f"Error generating commit message: {e}")
        return f"Error generating commit message: {str(e)}"
    finally:
        # Restore stderr and close devnull
        sys.stderr = _stderr
        _devnull_out.close()
