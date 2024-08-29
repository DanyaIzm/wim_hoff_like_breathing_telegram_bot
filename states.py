from aiogram.fsm.state import State, StatesGroup


class BreathCycle(StatesGroup):
    rounds_amount_selection = State()
    seconds_to_hold_amount_selection = State()
    pre_breathing = State()
    primary_breath_holding = State()
    deep_breath = State()
    secondary_breath_holding = State()
    round_end = State()
