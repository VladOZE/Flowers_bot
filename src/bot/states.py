from aiogram.fsm.state import State, StatesGroup


class SupportStates(StatesGroup):
    Question = State()
    AddMessage = State()


class FeedbackFormStates(StatesGroup):
    Question = State()
    FirstName = State()
    PhoneOrMail = State()


class PersonalOrderStates(StatesGroup):
    Description = State()
    Photo = State()
    Confirmation = State()


class NewAddressStates(StatesGroup):
    City = State()
    AddressLine = State()


class PersonalInfoStates(StatesGroup):
    FirstName = State()
    PhoneNumber = State()


class RecipientStates(StatesGroup):
    FirstName = State()
    PhoneNumber = State()