from aiogram.fsm.state import State, StatesGroup


class ModelCreation(StatesGroup):
    waiting_name = State()
    waiting_age = State()
    waiting_hair_color = State()
    waiting_hair_length = State()
    waiting_appearance = State()
    waiting_style = State()
    waiting_niche = State()


class ProductUpload(StatesGroup):
    waiting_title = State()
    waiting_category = State()
    waiting_description = State()
    waiting_photos = State()


# Backward compatibility: old modules are not included in main router, but imports will not break.
class CharacterCreation(StatesGroup):
    waiting_name = State()
    waiting_age = State()
    waiting_hair = State()
    waiting_body = State()
    waiting_style = State()
