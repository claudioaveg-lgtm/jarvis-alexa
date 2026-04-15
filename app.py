import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TV_SERVER_URL = os.environ.get("TV_SERVER_URL")

TV_COMMANDS = {
    "turn on": "KEYCODE_WAKEUP",
    "wake": "KEYCODE_WAKEUP", 
    "turn off": "KEYCODE_SLEEP",
    "netflix": "netflix",
    "pause": "KEYCODE_MEDIA_PAUSE",
    "play": "KEYCODE_MEDIA_PLAY",
    "volume up": "KEYCODE_VOLUME_UP",
    "volume down": "KEYCODE_VOLUME_DOWN",
}

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
            user_input = slots.get("query", {}).get("value", "hello").lower()
            
            # Check for TV commands
            tv_cmd = None
            for phrase, cmd in TV_COMMANDS.items():
                if phrase in user_input:
                    tv_cmd = cmd
                    break
            
            if tv_cmd and TV_SERVER_URL:
                try:
                    requests.post(f"{TV_SERVER_URL}/tv", 
                                json={"command": tv_cmd}, timeout=5)
                    speech = f"Done."
                except:
                    speech = "TV command failed."
            else:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}",
                             "Content-Type": "application/json"},
                    json={"model": "llama-3.3-70b-versatile",
                          "messages": [
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
