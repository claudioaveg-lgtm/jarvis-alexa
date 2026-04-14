import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route("/alexa", methods=["POST"])
def alexa():
    body = request.get_json()
    request_type = body.get("request", {}).get("type", "")

    if request_type == "LaunchRequest":
        speech = "Jarvis online. What do you need?"
        end = False
    elif request_type == "IntentRequest":
        intent = body["request"]["intent"]["name"]
        if intent in ["AMAZON.StopIntent", "AMAZON.CancelIntent"]:
            speech = "Jarvis shutting down."
            end = True
        else:
            slots = body["request"]["intent"].get("slots", {})
            user_input = slots.get("query", {}).get("value", "hello")
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [
                    {"role": "system", "content": "You are Jarvis. Keep responses under 40 words."},
                    {"role": "user", "content": user_input}
                ]}
            )
            speech = resp.json()["choices"][0]["message"]["content"]
            end = True
    else:
        speech = "Jarvis ready."
        end = True

    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": speech},
            "shouldEndSession": end
        }
    })

if __name__ == "__main__":
    app.run(port=5000)
