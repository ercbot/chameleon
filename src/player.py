from prompts import fetch_prompt

class Player:
    def __init__(self, name: str, controller: str, role: str):
        self.name = name
        self.controller = controller
        self.role = role
        self.messages = []

    def collect_input(self, prompt: str) -> str:
        """Store the input and output in the messages list. Return the output."""
        self.messages.append(prompt)
        output = self.respond(prompt)
        self.messages.append(output)
        return output

    def respond(self, prompt: str) -> str:
        if self.controller == "human":
            print(prompt)
            return input()

        elif self.controller == "ai":
            return "I am an AI and I am responding to the prompt."

    def add_message(self, message: str):
        """Add a message to the messages list. No response required."""
        self.messages.append(message)





