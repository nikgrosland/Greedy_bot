"""Everything related to building logic for the evolution chamber goes here"""
from sc2.constants import EVOLUTIONCHAMBER


class BuildEvochamber:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Builds the evolution chambers"""
        local_controller = self.ai
        pool = local_controller.pools
        evochamber = local_controller.evochambers
        return (
            pool.ready
            and local_controller.can_afford(EVOLUTIONCHAMBER)
            and (
                len(local_controller.townhalls) >= 3
                or (local_controller.close_enemy_production and len(local_controller.spines.ready) >= 4)
            )
            and len(evochamber) + local_controller.already_pending(EVOLUTIONCHAMBER) < 2
        )

    async def handle(self, iteration):
        """Build it behind the mineral line if there is space, if not uses later placement"""
        local_controller = self.ai
        position = await local_controller.get_production_position()
        base = local_controller.bases
        map_center = local_controller.game_info.map_center
        if position:
            await local_controller.build(EVOLUTIONCHAMBER, position)
            return True
        furthest_base = local_controller.furthest_townhall_to_map_center
        second_base = (base - {furthest_base}).closest_to(furthest_base)
        await local_controller.build(EVOLUTIONCHAMBER, second_base.position.towards_with_random_angle(map_center, -14))
        return True
