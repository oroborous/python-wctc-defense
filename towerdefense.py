import pyglet.resource
from cocos.director import director
from mainmenu import new_menu

if __name__ == '__main__':
    # add images to resource path
    pyglet.resource.path.append('assets')
    pyglet.resource.reindex()
    pyglet.font.add_file('assets/Oswald-Regular.ttf')

    director.init(caption='WCTC Defense')
    director.run(new_menu())
