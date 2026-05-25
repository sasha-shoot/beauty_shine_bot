from aiogram.fsm.state import State, StatesGroup

class MasterAuth(StatesGroup):
    entering_password = State()

class MasterFlow(StatesGroup):
    hist_date  = State()
    wm_service = State()
    wm_date    = State()
    wm_editing = State()

class DiscountFlow(StatesGroup):
    choosing_service = State()
    choosing_date    = State()
    choosing_time    = State()
    choosing_percent = State()

class MasterAIFlow(StatesGroup):
    asking = State()

class ManicureFlow(StatesGroup):
    choosing_type   = State()
    choosing_length = State()
    choosing_shape  = State()
    choosing_date   = State()
    choosing_time   = State()
    confirming      = State()

class PedicureFlow(StatesGroup):
    choosing_action = State()
    choosing_date   = State()
    choosing_time   = State()
    confirming      = State()

class AIHelperFlow(StatesGroup):
    describing = State()

class CallbackFlow(StatesGroup):
    entering_phone    = State()
    entering_question = State()
