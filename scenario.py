import cocos.tiles
import cocos.actions as ac

RIGHT = ac.RotateBy(90, 1)
LEFT = ac.RotateBy(-90, 1)


# convenience function to create MoveBy actions
# that will move a sprite at 100 pixels/second
def move(x, y):
    dur = abs(x + y) / 100.0
    return ac.MoveBy((x, y), duration=dur)


class Scenario:
    def __init__(self, map_name, turrets, bunker, enemy_start):
        self.map_name = map_name
        self.turret_slots = turrets
        self.bunker_position = bunker
        self.enemy_start = enemy_start
        self._enemy_actions = None

    @property
    def enemy_actions(self):
        # allows private attribute to be accessed
        # like a public attribute
        # for exampe: scenario.enemy_actions
        return self._enemy_actions

    @enemy_actions.setter
    def enemy_actions(self, action_list):
        # Make the "anchor" action a delay of no seconds
        self._enemy_actions = ac.Delay(0)
        # Uses the overridden + operator to make a chain of
        # actions
        for step in action_list:
            self._enemy_actions += step

    def get_background(self):
        # This contains all the maps in multiple layers
        tmx_map_layers = cocos.tiles.load('assets/{}.tmx'.format(self.map_name))
        # Select the chosen layer
        bg = tmx_map_layers[self.map_name]
        bg.set_view(0, 0, bg.px_width, bg.px_height)
        return bg


def get_scenario():
    # x/y positions of turret placement spot (where to place their centers)
    turret_slots = [(96, 320), (288, 288), (448, 320), (96, 96), (320, 96), (512, 96)]
    bunker_position = (48, 400)
    enemy_start = (-80, 176)
    sc = Scenario('level1', turret_slots, bunker_position, enemy_start)
    sc.enemy_actions = [RIGHT, move(560 + 80, 0), LEFT, move(0, 224), LEFT, move(-512, 0)]
    return sc
