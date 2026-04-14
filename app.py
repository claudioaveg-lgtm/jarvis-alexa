import os
import requests
from flask import Flask
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from flask_ask_sdk.skill_adapter import SkillAdapter

app = Flask(__name__)
sb = SkillBuilder()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

class LaunchHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.speak(
            "Jarvis online. What do you need?"
        ).set_should_end_session(False).response

class AskIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AskIntent")(handler_input)
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        user_input = slots.get("query").value if slots.get("query") else "hello"

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are Jarvis, a helpful AI assistant. Keep all responses under 40 words."},
                    {"role": "user", "content": user_input}
                ]
            }
        )
        speech = response.json()['choices'][0]['message']['content']

        return handler_input.response_builder.speak(speech).response

class StopHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.CancelIntent")(handler_input))
    def handle(self, handler_input):
        return handler_input.response_builder.speak("Jarvis shutting down.").response

sb.add_request_handler(LaunchHandler())
sb.add_request_handler(AskIntentHandler())
sb.add_request_handler(StopHandler())

skill_adapter = SkillAdapter(
    skill=sb.create(),
    skill_id="amzn1.ask.skill.8041df65-7884-4fef-ad63-ba33cc0470c4",
    app=app
)

@app.route("/alexa", methods=["POST"])
def invoke_skill():
    return skill_adapter.dispatch_request()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
