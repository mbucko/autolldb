from typing import Tuple, List
from openai import OpenAI


class LlmWrapper:
    def __init__(self, system_content: str, api_key: str):
        self.system_content = system_content
        self.client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
        self.messages_history: List[dict] = [
            {"role": "system", "content": system_content}
        ]

    def ask(self, prompt: str) -> Tuple[bool, str]:
        try:
            self.messages_history.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model="llama-3.1-sonar-huge-128k-online",
                messages=self.messages_history,
            )

            content = response.choices[0].message.content

            self.messages_history.append({"role": "assistant", "content": content})

            return True, content
        except Exception as e:
            return False, str(e)

    def get_conversation_history(self) -> str:
        """Return the conversation history as a formatted string"""
        history = ""
        for message in self.messages_history:
            history += f"{message['content']}\n\n"
        return history.strip()
