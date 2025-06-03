import os
from google.genai import Client, types

from sage_chat.chat import Chat

class AI:
    __SINGLETON = None

    @classmethod
    def get(cls) -> "AI":
        if cls.__SINGLETON is None:
            cls.__SINGLETON = AI()
        return cls.__SINGLETON

    def __init__(self):
        self.client = Client(api_key=os.environ['GEMINI_API_KEY'])

    def ask(self, text: str, system_instruction: str = None):
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction),
            contents=text
        )
        return response.text

    def message(self, chat: Chat, message: str) -> str:
        chat.user_message(message)
        
        response = self.ask(chat.prompt, chat.sage.system_instruction)

        chat.sage_message(response)

        return response
