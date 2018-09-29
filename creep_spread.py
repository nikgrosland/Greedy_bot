import math
from sc2.data import ActionResult
from sc2.position import Point2
from sc2.constants import (
    BUILD_CREEPTUMOR_QUEEN,
    BUILD_CREEPTUMOR_TUMOR,
    CREEPTUMOR,
    CREEPTUMORQUEEN,
    CREEPTUMORBURROWED,
    ZERGBUILD_CREEPTUMOR,
)


class creep_control:
    def __init__(self):
        self.used_tumors = []
    async def spread_creep(self):
        """ Iterate over all tumors to spread itself remove used creeps"""
        tumors = self.units(CREEPTUMORQUEEN) | self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED)
        for tumor in tumors:
            if tumor.tag not in self.used_tumors:
                await self.place_tumor(tumor)

    async def place_tumor(self, unit):
        """ Find a nice placement for the tumor and build it if possible, avoid expansion locations
        Makes creep to the enemy base, needs a better value function for the spreading"""
        # Make sure unit can make tumor and what ability it is
        abilities = await self.get_available_abilities(unit)
        if BUILD_CREEPTUMOR_QUEEN in abilities:
            unit_ability = BUILD_CREEPTUMOR_QUEEN
        elif BUILD_CREEPTUMOR_TUMOR in abilities:
            unit_ability = BUILD_CREEPTUMOR_TUMOR
        else:
            return None

        # defining vars
        ability = self._game_data.abilities[ZERGBUILD_CREEPTUMOR.value]
        location_attempts = 30
        spread_distance = 8
        location = unit.position
        # Define random positions around unit
        positions = [
            Point2(
                (
                    location.x + spread_distance * math.cos(math.pi * alpha * 2 / location_attempts),
                    location.y + spread_distance * math.sin(math.pi * alpha * 2 / location_attempts),
                )
            )
            for alpha in range(location_attempts)
        ]
        # check if any of the positions are valid
        valid_placements = await self._client.query_building_placement(ability, positions)
        # filter valid results
        valid_placements = [p for index, p in enumerate(positions) if valid_placements[index] == ActionResult.Success]
        if valid_placements:
            tumors = self.units(CREEPTUMORQUEEN) | self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED)
            if tumors:
                valid_placements = sorted(
                    valid_placements,
                    key=lambda pos: pos.distance_to_closest(tumors) - pos.distance_to(self.enemy_start_locations[0]),
                    reverse=True,
                )
            else:
                valid_placements = sorted(
                    valid_placements, key=lambda pos: pos.distance_to(self.enemy_start_locations[0])
                )
            # this is very expensive to the cpu, need optimization, keeps creep outside expansion locations
            for c_location in valid_placements:
                # 8.5 it doesnt get in the way of the injection
                if all(c_location.distance_to(el) > 8.5 for el in self.expansion_locations):
                    if not tumors:
                        self.actions.append(unit(unit_ability, c_location))
                        break
                    if unit_ability == BUILD_CREEPTUMOR_QUEEN:
                        self.actions.append(unit(unit_ability, c_location))
                        break
                    if c_location.distance_to_closest(tumors) >= 4:
                        self.actions.append(unit(unit_ability, c_location))
                        break

            if unit_ability == BUILD_CREEPTUMOR_TUMOR:  # if tumor
                self.used_tumors.append(unit.tag)
