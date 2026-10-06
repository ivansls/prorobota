from aiogram.fsm.state import State, StatesGroup


class LeadForm(StatesGroup):
    goal = State()
    experience = State()
    desired_position = State()
    comment = State()
