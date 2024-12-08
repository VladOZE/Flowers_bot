from aiogram.fsm.state import State, StatesGroup


class SupportStates(StatesGroup):
    Question = State()
    AddMessage = State()


class PersonalOrderStates(StatesGroup):
    Description = State()
    Photo = State()
    Confirmation = State()