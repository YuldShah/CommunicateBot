from aiogram.fsm.state import State, StatesGroup

class add_admin(StatesGroup):
    name = State()
    admin_id = State()
    confirm = State()
    password = State()

class show_msgs(StatesGroup):
    messages = State()
    replying = State()
    deleting = State()
    banning = State()