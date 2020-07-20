import cocos.sprite
import cocos.euclid as eu
import cocos.collision_model as cm
import cocos.actions as ac
import math
import pyglet.image
from pyglet.image import Animation


class Actor(cocos.sprite.Sprite):
    def __init__(self, image, x, y):
        super(Actor, self).__init__(image)
        pos = eu.Vector2(x, y)
        self.position = pos
        # the cshape will be a private property
        # with a special getter
        self._cshape = cm.CircleShape(pos,
                                      self.width * 0.5)

    @property
    def cshape(self):
        # keeps the CShape centered on the sprite when accessed
        self._cshape.center = eu.Vector2(self.x, self.y)
        return self._cshape


# A Hit action
class Hit(ac.IntervalAction):
    # runs for 0.5 seconds
    def init(self, duration=0.5):
        self.duration = duration

    # called several times with t in the (0, 1) range
    # t is the percent of the duration that has elapsed
    def update(self, t):
        # Red overlay gradually fades as t gets closer to 1
        self.target.color = (255, 255 * t, 255 * t)


# load this outside a class/function so it only happens once
raw = pyglet.image.load('assets/explosion.png')
seq = pyglet.image.ImageGrid(raw, 1, 8)
explosion_img = Animation.from_image_sequence(seq, 0.07, False)


# just a sprite, not an actor
class Explosion(cocos.sprite.Sprite):
    def __init__(self, pos):
        super(Explosion, self).__init__(explosion_img, pos)
        self.do(ac.Delay(1) + ac.CallFunc(self.kill))


class Enemy(Actor):
    # initial position and actions come from Scenario
    def __init__(self, x, y, actions):
        super(Enemy, self).__init__('tank.png', x, y)
        self.health = 100
        self.points = 20
        # flag to track whether tank exploded because of turret fire (True), or
        # because it reached the base
        self.destroyed_by_player = False
        self.do(actions)

    def explode(self):
        # an explosion is just a fast sequence of sprites
        self.parent.add(Explosion(self.position))
        self.kill()

    def hit(self):
        self.health -= 25
        # apply Hit interval action
        self.do(Hit())
        # check if tank is dead
        if self.health <= 0 and self.is_running:
            self.destroyed_by_player = True
            self.explode()


class Bunker(Actor):
    def __init__(self, x, y):
        super(Bunker, self).__init__('bunker.png', x, y)
        self.health = 100

    def collide(self, other):
        # did a tank just run into the bunker?
        if isinstance(other, Enemy):
            self.health -= 10
            other.explode()
            if self.health <= 0 and self.is_running:
                self.kill()


# Not an Actor, doesn't need to collide
class Shoot(cocos.sprite.Sprite):
    # Shoot's starting position, the vector it's traveling,
    # and reference to its target
    def __init__(self, pos, travel_path, enemy):
        super(Shoot, self).__init__('shoot.png', position=pos)
        # move from turret's position to tank's position,
        # hit the target, and self destruct
        self.do(ac.MoveBy(travel_path, 0.1) +
                ac.CallFunc(self.kill) +
                ac.CallFunc(enemy.hit))


# only needs a cshape to detect being clicked on
class TurretSlot(object):
    def __init__(self, pos, side):
        # use positional expansion operator ("splat") to unpack x, y from pos
        self.cshape = cm.AARectShape(eu.Vector2(*pos), side * 0.5, side * 0.5)


class Turret(Actor):
    def __init__(self, x, y):
        super(Turret, self).__init__('turret.png', x, y)
        # collision happens between range sprite and tank,
        # meaning that the tank is a valid target for this
        # turret
        self.add(cocos.sprite.Sprite('range.png',
                                     opacity=50,
                                     scale=5))

        self.cshape.r = self.width * 5 / 2
        self.target = None

        # turret is eligible to reload after period has elapsed
        self.period = 2.0
        self.elapsed = 0.0
        self.schedule(self._shoot)

    def _shoot(self, delta_time):
        if self.elapsed < self.period:
            # add elapsed time
            self.elapsed += delta_time
        elif self.target is not None:
            # if Turret has a target, time to fire
            self.elapsed = 0.0
            # calculate vector between Turret and target
            target_path = eu.Vector2(self.target.x - self.x,
                                     self.target.y - self.y)
            # normalize vector (get magnitude of 1), multiple by 20
            # (length of turret barrels), and add to turret's center
            pos = self.cshape.center + target_path.normalized() * 20
            # create a new Shoot and add to the scene
            self.parent.add(Shoot(pos, target_path, self.target))

    def collide(self, other):
        self.target = other
        if self.target is not None:
            # find x and y distance between Turret and target
            x, y = other.x - self.x, other.y - self.y
            # find arc tangent of y/x (considering signs)
            angle = -math.atan2(y, x)
            # convert from radians to degrees
            self.rotation = math.degrees(angle)

            # uncomment to see translation from radians to degrees
            # print('{}\t{}'.format(angle, self.rotation))
