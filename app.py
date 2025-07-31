from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API Key from .env
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Setup Flask
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    if request.method == "POST":
        topic = request.form["topic"]
        prompt = f"Explain the topic '{topic}' in a simple, fun, clear way for learners of all ages."

        try:
            result = model.generate_content(prompt)
            response = result.text
        except Exception as e:
            response = f"Error: {str(e)}"

    return render_template("index.html", response=response)

if __name__ == "__main__":
    app.run(debug=True, port=10000)
