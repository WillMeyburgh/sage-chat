from guru_ai.model.sage import Sage
from guru_ai.model.user_sage_info import UserSageInfo


class Chat:
    def __init__(self, sage: Sage, system_instruction = None):
        self.sage = sage
        self.system_information = system_instruction or sage.system_instruction
        self.prompt = ''
        self.sage_message(self.sage.initial_message)

    def add_message(self, name:str, message:str):
        self.prompt += f'{name}: {message}\n\n'

    def sage_message(self, message: str):
        self.add_message(self.sage.name, message)

    def user_message(self, message: str):
        self.add_message('Wonderer', message)
        
