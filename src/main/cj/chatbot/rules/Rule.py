from typing import List

from cj.chatbot.rules.Action import Action
from cj.chatbot.rules.Decision import Decision
from cj.chatbot.rules.Reactivation import Reactivation


class Rule:
    def __init__(self, decision: Decision, actions: List[Action], reactivation: Reactivation = None):
        self.decision = decision
        self.actions = actions
        self.reactivation = reactivation
        self.deactivated = False

        self.triggeredTimes: List[float] = []    # Timestamps of the time when the rule was triggered.

    def evaluate(self):
        if self.reactivation:
            # If the rule can be reactivated, see if reactivation condition is met
            self.reactivation.tryActivate(self)

        if self.deactivated:
            # Skip this rule if it is already deactivated
            return

        # Test the decision and run actions accordingly
        if self.decision.decide():
            for action in self.actions:
                action.act()
            self.deactivated = True

            # Record properties to the chain
            self.__record()

    def __record(self):
        decision = self.decision.getProperties()
        actions = [a.getProperties() for a in self.actions]

        # TODO: Recording the properties to the TrustManagement
        pass
