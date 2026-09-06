from transitions import Machine
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class GenericState(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"

class WorkflowStateMachine:
    def __init__(self, initial_state: GenericState = GenericState.IDLE):
        self.state = initial_state.value
        self.machine = Machine(
            model=self,
            states=[s.value for s in GenericState],
            initial=self.state,
            auto_transitions=False
        )
        self._register_transitions()

    def _register_transitions(self):
        self.machine.add_transition(
            trigger="activate", 
            source=GenericState.IDLE.value, 
            dest=GenericState.ACTIVE.value,
            after="on_enter_active"
        )
        self.machine.add_transition(
            trigger="suspend", 
            source=GenericState.ACTIVE.value, 
            dest=GenericState.SUSPENDED.value
        )
        self.machine.add_transition(
            trigger="resume", 
            source=GenericState.SUSPENDED.value, 
            dest=GenericState.ACTIVE.value
        )
        self.machine.add_transition(
            trigger="finish", 
            source=[GenericState.ACTIVE.value, GenericState.SUSPENDED.value], 
            dest=GenericState.COMPLETED.value
        )

    def on_enter_active(self):
        logger.info(f"FSM transitioned to {self.state}")
