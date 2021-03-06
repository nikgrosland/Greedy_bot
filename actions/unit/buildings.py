"""Everything related to cancelling buildings goes here"""
from sc2.constants import CANCEL, HATCHERY


class Buildings:
    """Ok for now but can be improved, it works every time
     but it should prevent cancelled buildings to be replaced right after"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return (
            local_controller.time < 300
            if local_controller.close_enemy_production
            else local_controller.structures.not_ready
        )

    async def handle(self, iteration):
        """Make the cancelling general"""
        local_controller = self.ai
        for building in local_controller.structures.not_ready.filter(
            lambda x: x.type_id not in local_controller.tumors
        ):
            if (
                building.health_percentage < building.build_progress - 0.5
                or building.health_percentage < 0.05
                and building.build_progress > 0.1
            ) or (building.type_id == HATCHERY and local_controller.close_enemy_production):
                local_controller.add_action((building(CANCEL)))
