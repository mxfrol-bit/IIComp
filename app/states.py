from aiogram.fsm.state import State, StatesGroup


class CharacterCreation(StatesGroup):
    waiting_name = State()
    waiting_age = State()
    waiting_hair = State()
    waiting_body = State()
    waiting_style = State()
