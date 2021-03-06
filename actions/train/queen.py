"""Everything related to training queens goes here"""
from sc2.constants import LAIR, QUEEN


class TrainQueen:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.hatchery = None

    async def should_handle(self, iteration):
        """It possibly can get better but it seems good enough for now"""
        local_controller = self.ai
        self.hatchery = local_controller.townhalls.exclude_type(LAIR).noqueue.ready
        return (
            self.hatchery
            and local_controller.pools.ready
            and len(local_controller.queens) < len(self.hatchery) + 1
            and not local_controller.already_pending(QUEEN)
            and local_controller.can_train(QUEEN, larva=False)
        )

    async def handle(self, iteration):
        """Execute the action of training queens"""
        self.ai.add_action(self.hatchery.random.train(QUEEN))
        return True
