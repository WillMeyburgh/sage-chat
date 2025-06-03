from guru_ai.database import db
from guru_ai.model.sage import Sage
from guru_ai.model.user import User
from guru_ai.model.user_sage_info import UserSageInfo


class Chat:
    def __init__(self, user: User, sage: Sage):
        self.user = user
        self.sage = sage
        self.info = UserSageInfo.get_user_sage_info(user.id, sage.id)
        self.prompt = self.info.prompt_text if self.info else ''
        self.sage_message(self.sage.initial_message)

    @property
    def system_instruction(self):
        if self.info is not None and self.info.system_instruction is not None:
            return self.info.system_instruction
        return self.sage.system_instruction

    def add_message(self, name:str, message:str):
        self.prompt += f'{name}: {message}\n\n'

    def sage_message(self, message: str):
        self.add_message(self.sage.name, message)

    def user_message(self, message: str):
        self.add_message(self.user.name, message)

    def update(self):
        system_instruction=None if self.info is None or self.info.system_instruction is None else self.system_instruction
        UserSageInfo.create_or_update_user_sage_info(
            user_id=self.user.id,
            sage_id=self.sage.id,
            system_instruction=system_instruction,
            prompt_text=self.prompt
        )

    def update_system_instruction(self, ai):
        system_instruction = ai.ask(
            f'''Write a new system instruction for yourself to to use in the future for user,
you'll be given your current system instruction and the last chat you guys had. Write the new system instuction so
you'll remeber key information and your identity

System Instruction:
{self.system_instruction}

Last Chat:
{self.prompt}
''', self.system_instruction)
        
        self.info = UserSageInfo.create_or_update_user_sage_info(
            self.user.id,
            self.sage.id,
            system_instruction=system_instruction,
            prompt_text=''
        )
