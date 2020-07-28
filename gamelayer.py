import cocos.scene
from scenario import get_scenario_1
from scenario import get_scenario_2
from scenario import get_scenario_3

import cocos.layer
import cocos.text
import cocos.actions as ac
import cocos.collision_model as cm
from cocos.director import director
from cocos.scenes.transitions import SplitColsTransition, FadeTransition
import random
import actors
import mainmenu


# called by main menu when game is started
def new_game():
    scenario = get_scenario_3()
    background = scenario.get_background()
    hud = HUD()
    game_layer = GameLayer(hud, scenario)
    # returns a Scene that the director will load
    return cocos.scene.Scene(background, game_layer, hud)


# called from game layer when bunker's health decreases to zero
def game_over():
    # create a text label
    w, h = director.get_window_size()
    layer = cocos.layer.Layer()
    text = cocos.text.Label('Game Over',
                            position=(w * 0.5, h * 0.5),
                            font_name='Oswald',
                            font_size=72,
                            anchor_x='center',
                            anchor_y='center')
    layer.add(text)
    scene = cocos.scene.Scene(layer)

    menu_scene = FadeTransition(mainmenu.new_menu())
    show_menu = lambda: director.replace(menu_scene)
    scene.do(ac.Delay(3) + ac.CallFunc(show_menu))
    return scene


class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = director.get_window_size()
        # create some Labels for the score and points
        self.score_text = self._create_text(60, h - 40)
        self.points_text = self._create_text(w - 60, h - 40)

    def _create_text(self, x, y):
        text = cocos.text.Label(font_size=18,
                                font_name='Oswald',
                                anchor_x='center',
                                anchor_y='center')
        text.position = (x, y)
        self.add(text)
        return text

    def update_score(self, score):
        self.score_text.element.text = 'Score: {}'.format(score)

    def update_points(self, points):
        self.points_text.element.text = 'Points: {}'.format(points)


class GameLayer(cocos.layer.Layer):
    # listens for mouse clicks to place turrets
    is_event_handler = True

    def __init__(self, hud, scenario):
        super(GameLayer, self).__init__()
        self.hud = hud
        self.scenario = scenario
        # use setters (defined below) to initialize text labels
        self.score = self._score = 0
        self.points = self._points = 40
        self.turrets = []

        w, h = director.get_window_size()
        cell_size = 32

        # use two collision managers for better performance,
        # as the turret slots never collide with the other
        # Actors

        # collision manager for tanks and bunker
        self.coll_man = cm.CollisionManagerGrid(0, w, 0, h,
                                                cell_size,
                                                cell_size)
        # collision manager for static turret slots
        self.coll_man_slots = cm.CollisionManagerGrid(0, w, 0, h,
                                                      cell_size,
                                                      cell_size)
        for slot in scenario.turret_slots:
            self.coll_man_slots.add(actors.TurretSlot(slot,
                                                      cell_size))

        # unpack tuple into x and y by using *
        self.bunker = actors.Bunker(*scenario.bunker_position)
        self.add(self.bunker)
        self.schedule(self.game_loop)

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, val):
        self._points = val
        # keep HUD updated when points change
        self.hud.update_points(val)

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, val):
        self._score = val
        self.hud.update_score(val)

    def create_enemy(self):
        enemy_start = self.scenario.enemy_start
        # apply a little random variance +/-10 in the x and y
        # so that all enemies don't start in exactly the same place
        x = enemy_start[0] + random.uniform(-10, 10)
        y = enemy_start[1] + random.uniform(-10, 10)
        self.add(actors.Enemy(x, y, self.scenario.enemy_actions))

    def on_mouse_press(self, x, y, buttons, mod):
        slots = self.coll_man_slots.objs_touching_point(x, y)
        if len(slots) and self.points >= 20:
            self.points -= 20
            slot = next(iter(slots))
            turret = actors.Turret(*slot.cshape.center)
            self.turrets.append(turret)
            self.add(turret)

    # overridden to provide extra behavior when bunker or tank
    # is removed from the layer
    def remove(self, obj):
        # if bunker destroyed, player lost and game over scene
        # is transitioned into
        if obj is self.bunker:
            director.replace(SplitColsTransition(game_over()))
        elif isinstance(obj, actors.Enemy) and obj.destroyed_by_player:
            self.score += obj.points
            self.points += 5
        super(GameLayer, self).remove(obj)

    def game_loop(self, _):
        # clear out collision manager
        self.coll_man.clear()

        # for every child node in the layer
        for obj in self.get_children():
            # if it's a tank, add it to the collision manager
            if isinstance(obj, actors.Enemy):
                self.coll_man.add(obj)

        # for every turret
        for turret in self.turrets:
            # Get the first object in the iterator of things it's
            # colliding with
            obj = next(self.coll_man.iter_colliding(turret), None)
            # And collide with it
            turret.collide(obj)

        # for every object (tank) colliding with the bunker
        for obj in self.coll_man.iter_colliding(self.bunker):
            self.bunker.collide(obj)

        # generate a enemy when the random number hits
        if random.random() < 0.005:
            self.create_enemy()
