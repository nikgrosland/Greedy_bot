from sc2.constants import (SPINECRAWLER, SPAWNINGPOOL, BARRACKS, GATEWAY)

class BuildSpines:

    def __init__(self, ai):
        self.ai = ai
        self.lairs = None

    async def should_handle(self, iteration):

        if not self.ai.pools.ready:
            return False

        base = self.ai.townhalls
        return (
            len(self.ai.spines) + self.ai.already_pending(SPINECRAWLER) < 1
            and len(base.ready) >= 2
            and self.ai.time <= 360
            or (
                self.ai.close_enemy_production
                and self.ai.time <= 300
                and len(self.ai.spines) + self.ai.already_pending(SPINECRAWLER) < 3
            )
        )

    async def handle(self, iteration):
        await self.ai.build(
            SPINECRAWLER,
            near=self.ai.townhalls.closest_to(self.ai._game_info.map_center).position.towards(
                self.ai._game_info.map_center, 9
            ),
        )
        return True
