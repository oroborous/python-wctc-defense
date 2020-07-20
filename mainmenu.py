import cocos.menu
import cocos.scene
import cocos.layer
import cocos.actions as ac
from cocos.director import director
from cocos.scenes.transitions import FadeTRTransition
import pyglet.app

from gamelayer import new_game


class MainMenu(cocos.menu.Menu):
    def __init__(self):
        super(MainMenu, self).__init__('WCTC Defense')

        # use a custom font for menu title
        self.font_title['font_name'] = 'Oswald'
        # use same font for menu items
        self.font_item['font_name'] = 'Oswald'
        self.font_item_selected['font_name'] = 'Oswald'

        # easier to center menu items in window if their
        # anchor points are also in their centers
        self.menu_anchor_y = 'center'
        self.menu_anchor_x = 'center'

        # create list to hold menu items
        items = list()
        # calls on_new_game() when clicked
        items.append(cocos.menu.MenuItem('New Game', self.on_new_game))
        # calls show_fps() when clicked
        # third argument is the initial state of the toggle: True/False
        items.append(cocos.menu.ToggleMenuItem('Show FPS: ', self.show_fps,
                                               director.show_FPS))
        # call pyglet's exit() function
        items.append(cocos.menu.MenuItem('Quit', pyglet.app.exit))

        self.create_menu(items,
                         # action when menu is activated
                         ac.ScaleTo(1.25, duration=0.25),
                         # action when menu is deactivated
                         ac.ScaleTo(1.0, duration=0.25))

    def on_new_game(self):
        director.push(FadeTRTransition(new_game(), duration=2))

    def show_fps(self, value):
        director.show_FPS = value


# called by "main" when game is started
def new_menu():
    scene = cocos.scene.Scene()
    # create a colored background behind the menu
    color_layer = cocos.layer.ColorLayer(205, 133, 63, 255)
    # higher z values go on top of lower z values
    scene.add(MainMenu(), z=1)
    scene.add(color_layer, z=0)
    return scene
