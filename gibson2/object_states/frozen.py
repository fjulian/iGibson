from gibson2.object_states.temperature import Temperature
from gibson2.object_states.object_state_base import CachingEnabledObjectState, BooleanState

_DEFAULT_FREEZE_TEMPERATURE = 0.0


class Frozen(CachingEnabledObjectState, BooleanState):
    def __init__(self, obj, freeze_temperature=_DEFAULT_FREEZE_TEMPERATURE):
        super(Frozen, self).__init__(obj)
        self.freeze_temperature = freeze_temperature

    @staticmethod
    def get_dependencies():
        return CachingEnabledObjectState.get_dependencies() + [Temperature]

    def _set_value(self, new_value):
        return self.obj.states[Temperature].set_value(self.freeze_temperature)

    def _compute_value(self):
        return self.obj.states[Temperature].get_value() <= self.freeze_temperature

    # Nothing needs to be done to save/load Frozen since it will happen due to temperature caching.
    def _dump(self):
        return None

    def _load(self, data):
        return