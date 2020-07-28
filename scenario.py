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
    def __init__(self, tmx_file, map_layer, turrets, bunker, enemy_start):
        self.tmx_file_name = tmx_file
        self.map_layer_name = map_layer
        self.turret_slots = turrets
        self.bunker_position = bunker
        self.enemy_start = enemy_start
        self._enemy_actions = None

    @property
    def enemy_actions(self):
        # allows private attribute to be accessed
        # like a public attribute
        # for example: scenario.enemy_actions
        return self._enemy_actions

    @enemy_actions.setter
    def enemy_actions(self, action_list):
        # Make the "anchor" action a delay of no seconds
        self._enemy_actions = ac.Delay(0)
        # Uses the overloaded + operator to make a chain of
        # actions
        for step in action_list:
            self._enemy_actions += step

    def get_background(self):
        # This contains all the maps in multiple layers
        tmx_map_layers = cocos.tiles.load('assets/{}.tmx'.format(self.tmx_file_name))
        # Select the chosen layer
        bg = tmx_map_layers[self.map_layer_name]
        bg.set_view(0, 0, bg.px_width, bg.px_height)
        return bg


def get_scenario_1():
    # x/y positions of turret placement spot (where to place their centers)
    turret_slots = [(96, 320), (288, 288), (448, 320), (96, 96), (320, 96), (512, 96)]
    bunker_position = (48, 400)
    # start 80 pixels offscreen
    enemy_start = (-80, 176)
    sc = Scenario('level1', 'map1', turret_slots, bunker_position, enemy_start)
    # first move must add an extra half a tile, plus the 80 pixels from offscreen
    sc.enemy_actions = [RIGHT, move(544 + 16 + 80, 0), LEFT, move(0, 224), LEFT, move(-512, 0)]
    return sc


def get_scenario_2():
    # x/y positions of turret placement spot (where to place their centers)
    turret_slots = [(64, 160), (192, 128), (192, 192), (352, 160), (160, 352), (512, 352), (512, 160)]
    bunker_position = (464, 48)
    # start 80 pixels offscreen
    enemy_start = (-80, 48)
    sc = Scenario('level2', 'map1', turret_slots, bunker_position, enemy_start)
    # first move must add an extra half a tile, plus the 80 pixels from offscreen
    sc.enemy_actions = [RIGHT, move(256 + 16 + 80, 0), LEFT, move(0, 224), LEFT, move(-192, 0),
                        RIGHT, move(0, 160), RIGHT, move(512, 0), RIGHT, move(0, -352), RIGHT,
                        move(-128, 0), LEFT, move(0, -64)]
    return sc


def get_scenario_3():
    turret_slots = [(288, 288), (128, 192), (384, 128), (544, 192)]
    bunker_position = (592, 112)
    enemy_start = (-80, 112)
    sc = Scenario('level3', 'map1', turret_slots, bunker_position, enemy_start)
    sc.enemy_actions = [
        RIGHT, move(192 + 16 + 80, 0), LEFT, move(0, 256), RIGHT, move(256, 0), RIGHT,
        move(0, -256), LEFT, move(160, 0)
    ]
    return sc
