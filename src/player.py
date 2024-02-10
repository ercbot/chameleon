import os
import openai

# Using TGI Inference Endpoints from Hugging Face
# api_type = "tgi"
api_type = "openai"

if api_type == "tgi":
    model_name = "tgi"
    client = openai.Client(
        base_url=os.environ['HF_ENDPOINT_URL'] + "/v1/",
        api_key=os.environ['HF_API_TOKEN']
    )
else:
    model_name = "gpt-3.5-turbo"
    client = openai.Client()

class Player:
    def __init__(self, name: str, controller: str, role: str):
        self.name = name
        self.controller = controller
        self.role = role
        self.messages = []

    def collect_input(self, prompt: str) -> str:
        """Store the input and output in the messages list. Return the output."""
        self.messages.append({"role": "user", "content": prompt})
        output = self.respond(prompt)
        self.messages.append({"role": "assistant", "content": output})
        return output

    def respond(self, prompt: str) -> str:
        if self.controller == "human":
            print(prompt)
            return input()

        elif self.controller == "ai":
            chat_completion = client.chat.completions.create(
                model=model_name,
                messages=self.messages,
                stream=False,
            )

            return chat_completion.choices[0].message.content


    def add_message(self, message: str):
        """Add a message to the messages list. No response required."""
        self.messages.append({"role": "user", "content": message})





