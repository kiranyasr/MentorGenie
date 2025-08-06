from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import google.generativeai as genai
import markdown2
import pyttsx3
import time

# ---------------------------
# Load API Key
# ---------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ---------------------------
# Configure Gemini
# ---------------------------
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# ---------------------------
# Initialize Flask
# ---------------------------
app = Flask(__name__)

# ---------------------------
# Text-to-Speech using pyttsx3 with Indian voice
# ---------------------------
def text_to_speech(text):
    try:
        engine = pyttsx3.init()

        # 🔊 Set medium-slow speaking rate
        engine.setProperty('rate', 130)

        # 🗣️ List available voices
        voices = engine.getProperty('voices')

        # 🎯 Try to find Microsoft Ravi or Heera or any Indian voice
        selected_voice = None
        for voice in voices:
            if "Ravi" in voice.name or "Heera" in voice.name or "Indian" in voice.name or "en-IN" in str(voice.languages):
                selected_voice = voice.id
                break

        if selected_voice:
            engine.setProperty('voice', selected_voice)
            print(f"✅ Using voice: {selected_voice}")
        else:
            print("⚠️ Ravi or Heera voice not found. Using default.")

        # Save speech to file
        engine.save_to_file(text, 'static/audio/output.mp3')
        engine.runAndWait()
        return True

    except Exception as e:
        print(f"TTS Error: {e}")
        return False

# ---------------------------
# Route: Home Page
# ---------------------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------------------
# Route: Learn Page
# ---------------------------
@app.route("/learn", methods=["GET", "POST"])
def learn():
    html_response = None
    audio_path = None

    if request.method == "POST":
        topic = request.form.get("topic", "").strip()

        if topic:
            prompt = f"""
Explain the topic '{topic}' in a simple, fun, engaging, and clear way for learners of all ages.
Use real-life examples, highlight key points using **bold**, and format it well with bullet points or subheadings if needed.
"""
            try:
                # Retry logic for Gemini rate limits
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        result = model.generate_content(prompt)
                        break
                    except Exception as e:
                        if "Too many concurrent requests" in str(e) and attempt < max_retries - 1:
                            time.sleep(3)
                        else:
                            raise e

                # Process response
                markdown_text = result.text
                clean_text = markdown_text.replace("*", "").replace("#", "").replace("-", "").replace("•", "")
                html_response = markdown2.markdown(
                    markdown_text,
                    extras=["fenced-code-blocks", "tables", "strike", "code-friendly"]
                )

                # Convert to speech
                if text_to_speech(clean_text):
                    audio_path = "audio/output.mp3"

            except Exception as e:
                html_response = f"<p style='color:red;'>❌ Error: {str(e)}</p>"

    return render_template("index.html", response=html_response, audio=audio_path)

# ---------------------------
# Run Flask App
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, port=10000)
