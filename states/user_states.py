from aiogram.fsm.state import State, StatesGroup

class send_message(StatesGroup):
    content = State()
    confirm = State()

class show_my_messages(StatesGroup):
    messages = State()
    deleting = State()
