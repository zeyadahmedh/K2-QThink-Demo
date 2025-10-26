import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai

# Configure Flask app
app = Flask(__name__, static_folder='../static')

# ---!!! START OF CONFIGURATION !!!---

# STEP 1: Get your API key from https://aistudio.google.com/
# STEP 2: PASTE YOUR NEW, SECRET GOOGLE AI KEY HERE.
# IMPORTANT: For Vercel, use the "GOOGLE_API_KEY" Environment Variable.

LOCAL_GOOGLE_KEY = "AIzaSyDh_aKCSIKm6G_URD111DibZSrAyuD-Di8" # <-- PASTE YOUR KEY HERE

# ---!!! END OF CONFIGURATION !!!---

# This code first tries to find a Vercel Environment Variable.
# If it can't, it falls back to your local key.
API_KEY = os.environ.get("GOOGLE_API_KEY", LOCAL_GOOGLE_KEY)

# Configure the Google AI client
if API_KEY and API_KEY != "PASTE_YOUR_NEW_SECRET_API_KEY_HERE":
    genai.configure(api_key=API_KEY)

# The Gemini model doesn't use a combined "system" and "user" prompt in the same string.
# We will prepend the instructions to the user's prompt.
SYSTEM_INSTRUCTIONS = """You are Kuantum-2, an expert AI model specialized in quantum computing and modern physics. Your purpose is to answer complex questions, explain quantum concepts in clear terms, and generate code (primarily Python with Qiskit, Cirq, or Pennylane) for quantum algorithms.

When asked for code, always provide a complete, runnable example.
When asked for concepts, be precise and use analogies where helpful.
You are a helpful assistant dedicated to advancing quantum education."""


def call_gemini_api(prompt):
    """
    Calls the Google Gemini API.
    """
    if not API_KEY or "PASTE_YOUR_NEW_SECRET_API_KEY_HERE" in API_KEY:
        return "Error: API_KEY is missing. Please add your Google AI API key to the `LOCAL_GOOGLE_KEY` variable in `api/app.py`."

    try:
        # Initialize the model
        # For a list of available models, see: https://ai.google.dev/models/gemini
        model = genai.GenerativeModel('gemini-2.5-pro')
        # Combine system instructions with the user's prompt
        full_prompt = f"{SYSTEM_INSTRUCTIONS}\n\nUser: {prompt}\nKuantum-2:"

        # Generate content
        response = model.generate_content(full_prompt)

        # Extract the text from the response
        return response.text

    except Exception as e:
        # Handle potential API errors, such as configuration issues or blocked content
        print(f"Gemini API call failed: {e}")
        return f"Error: The request to the Gemini AI service failed. Details: {str(e)}"


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({"error": "No prompt provided"}), 400

        prompt = data['prompt']
        ai_response = call_gemini_api(prompt)

        # Check if the response is an error message
        if ai_response.startswith("Error:"):
            # Use 500 for server-side errors (like API key issues)
            return jsonify({"error": ai_response}), 500

        return jsonify({"response": ai_response})

    except Exception as e:
        print(f"Error in /api/chat: {e}")
        return jsonify({"error": "An unexpected error occurred on the server."}), 500


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)


if __name__ == '__main__':
    app.run(debug=True, port=5000)