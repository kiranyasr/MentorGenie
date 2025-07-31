from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import google.generativeai as genai
import markdown2

# Load environment variables from .env file
load_dotenv()

# Get your Google API Key from .env
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Initialize Flask app
app = Flask(__name__)

# ---------------------------
# Route: Home (Welcome Page)
# ---------------------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------------------
# Route: Learn (Topic Input)
# ---------------------------
@app.route("/learn", methods=["GET", "POST"])
def learn():
    html_response = None

    if request.method == "POST":
        topic = request.form.get("topic", "").strip()

        if topic:
            prompt = f"""
Explain the topic '{topic}' in a simple, fun, engaging, and clear way for learners of all ages.
Use real-life examples, highlight key points using **bold**, and format it well with bullet points or subheadings if needed.
"""

            try:
                result = model.generate_content(prompt)
                markdown_text = result.text
                html_response = markdown2.markdown(
                    markdown_text, extras=["fenced-code-blocks", "tables", "strike", "code-friendly"]
                )

            except Exception as e:
                html_response = f"<p style='color:red;'>❌ Error: {str(e)}</p>"

    return render_template("index.html", response=html_response)


# ---------------------------
# Run the Flask App
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, port=10000)
