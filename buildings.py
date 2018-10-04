"""Every logic for building structures go here"""
from sc2.constants import (
    BARRACKS,
    EVOLUTIONCHAMBER,
    EXTRACTOR,
    GATEWAY,
    HATCHERY,
    HIVE,
    INFESTATIONPIT,
    LAIR,
    SPAWNINGPOOL,
    SPINECRAWLER,
    SPORECRAWLER,
    ULTRALISKCAVERN,
    ZERGGROUNDARMORSLEVEL2,
)


class builder:
    def __init__(self):
        self.enemy_flying_dmg_units = False
        self.worker_to_first_base = False

    async def build_cavern(self):
        """Builds the ultralisk cavern, placement can maybe be improved(far from priority)"""
        evochamber = self.evochambers
        if (
            evochamber
            and self.units(HIVE)
            and not self.caverns
            and self.can_afford(ULTRALISKCAVERN)
            and not self.already_pending(ULTRALISKCAVERN)
        ):
            await self.build(
                ULTRALISKCAVERN,
                near=self.townhalls.furthest_to(self.game_info.map_center).position.towards_with_random_angle(
                    self.game_info.map_center, -15
                ),
            )

    async def build_evochamber(self):
        """Builds the evolution chambers, placement can maybe be improved(far from priority),
        also there is some occasional bug that prevents both to be built at the same time,
        probably related to placement"""
        pool = self.pools
        evochamber = self.evochambers
        if (
            pool.ready
            and self.can_afford(EVOLUTIONCHAMBER)
            and len(self.townhalls.ready) >= 3
            and len(evochamber) + self.already_pending(EVOLUTIONCHAMBER) < 2
        ):
            await self.build(
                EVOLUTIONCHAMBER,
                near=self.townhalls.furthest_to(self.game_info.map_center).position.towards_with_random_angle(
                    self.game_info.map_center, -15
                ),
            )

    def build_extractor(self):
        """Couldnt find another way to build the geysers its way to inefficient,
         also the logic can be improved, sometimes it over collect vespene sometime it under collect"""
        if self.vespene < self.minerals * 2:
            if self.townhalls.ready and self.can_afford(EXTRACTOR):
                gas = self.units(EXTRACTOR)
                gas_amount = len(gas)  # so it calculate just once per step
                vgs = self.state.vespene_geyser.closer_than(10, self.townhalls.ready.random)
                for geyser in vgs:
                    drone = self.select_build_worker(geyser.position)
                    if not drone:
                        break
                    if not self.already_pending(EXTRACTOR):
                        if not gas and self.pools:
                            self.actions.append(drone.build(EXTRACTOR, geyser))
                            break
                        if gas_amount == 1 and len(self.townhalls) >= 3:
                            self.actions.append(drone.build(EXTRACTOR, geyser))
                            break
                    if self.time > 960 and gas_amount < 10:
                        self.actions.append(drone.build(EXTRACTOR, geyser))
                        break
                    pit = self.pits
                    if pit and gas_amount + self.already_pending(EXTRACTOR) < 8:
                        self.actions.append(drone.build(EXTRACTOR, geyser))
                        break

    async def build_hatchery(self):
        """Good for now, maybe the 7th or more hatchery can be postponed
         for when extra mining patches or production are needed """
        base_amount = len(self.townhalls)  # so it just calculate once per loop
        if not self.worker_to_first_base and base_amount < 2 and self.minerals > 235:
            self.worker_to_first_base = True
            self.actions.append(self.workers.gathering.first.move(await self.get_next_expansion()))
        if (
            self.townhalls
            and self.can_afford(HATCHERY)
            and not self.close_enemies_to_base
            and not self.already_pending(HATCHERY)
            and not (self.known_enemy_structures.closer_than(50, self.start_location) and self.time < 300)
        ):
            if base_amount <= 4:
                if base_amount == 2:
                    if self.spines:
                        await self.expand_now()
                else:
                    if base_amount == 3:
                        await self.build_macrohatch()
                    else:
                        await self.expand_now()
            elif self.caverns:
                await self.expand_now()

    async def build_macrohatch(self):
        await self.build(
            HATCHERY,
            near=self.townhalls.furthest_to(self.game_info.map_center).position.towards(self.game_info.map_center, 7),
        )

    async def build_pit(self):
        """Builds the infestation pit, placement can maybe be improved(far from priority)"""
        evochamber = self.evochambers
        if (
            evochamber
            and not self.pits
            and self.can_afford(INFESTATIONPIT)
            and not self.already_pending(INFESTATIONPIT)
            and self.units(LAIR).ready
            and self.already_pending_upgrade(ZERGGROUNDARMORSLEVEL2) > 0
            and self.townhalls
        ):
            await self.build(
                INFESTATIONPIT,
                near=self.townhalls.furthest_to(self.game_info.map_center).position.towards_with_random_angle(
                    self.game_info.map_center, -15
                ),
            )

    async def build_pool(self):
        """Builds the spawning pol, placement can maybe be improved(far from priority)
        The logic vs proxies is yet to be tested, maybe it can be more adaptable vs some strategies"""
        base = self.townhalls
        if (not self.already_pending(SPAWNINGPOOL) and not self.pools and self.can_afford(SPAWNINGPOOL)) and (
            (len(base) >= 2) or (self.close_enemy_production and self.time < 300)
        ):
            await self.build(
                SPAWNINGPOOL,
                near=self.townhalls.furthest_to(self.game_info.map_center).position.towards_with_random_angle(
                    self.game_info.map_center, -15
                ),
            )

    async def build_spores(self):
        """Build spores and spines, the spines are ok for now anti proxy are yet to be tested,
         spores needs better placement and logic for now tho"""
        base = self.townhalls
        spores = self.units(SPORECRAWLER)
        if self.pools.ready:
            if not self.enemy_flying_dmg_units:
                if self.known_enemy_units.flying:
                    air_units = [au for au in self.known_enemy_units.flying if au.can_attack_ground]
                    if air_units:
                        self.enemy_flying_dmg_units = True
            else:
                if base:
                    selected_base = base.random
                    if len(spores) < len(base.ready) and not self.already_pending(SPORECRAWLER):
                        if not spores.closer_than(15, selected_base.position) and self.can_afford(SPORECRAWLER):
                            await self.build(SPORECRAWLER, near=selected_base.position)
            if (
                len(self.spines) + self.already_pending(SPINECRAWLER) < 2 <= len(base.ready)
                and self.time <= 360
                or (
                    self.close_enemy_production
                    and self.time <= 300
                    and len(self.spines) + self.already_pending(SPINECRAWLER)
                    < len(self.known_enemy_structures.of_type({BARRACKS, GATEWAY}).closer_than(50, self.start_location))
                )
            ):
                await self.build(
                    SPINECRAWLER,
                    near=self.townhalls.closest_to(self._game_info.map_center).position.towards(
                        self._game_info.map_center, 9
                    ),
                )

    async def all_buildings(self):
        """Builds every building, logic should be improved"""
        await self.build_cavern()
        await self.build_evochamber()
        self.build_extractor()
        await self.build_hatchery()
        await self.build_pit()
        await self.build_pool()
        await self.build_spores()