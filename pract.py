"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

import os

import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "You are a git commit generator, i will send you git diff content and you are to generate commit message or messages from it based on the count passed. if i include count=1, generate one commit, else generate the count number of commit. reply with only the commit message or messages. commit message should be one line long and follow conventional commits",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, I'm ready! Please send me the git diff content and the desired count, and I'll generate the commit messages for you. 😊 \n",
      ],
    },
  ]
)

response = chat_session.send_message(
    "diff --git a/src/utils/logger.py b/src/utils/logger.py \
    deleted file mode 100644 \
    index e69de29..0000000 count=2"
    )

print(response.text)
