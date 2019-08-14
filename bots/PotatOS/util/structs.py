import math, time
from util.vec import *

class CarData:
    def __init__(self):
        self.position = Vec3(0, 0, 0)
        self.rotation = 0
        self.velocity = Vec3(0, 0, 0)
        self.angular_velocity = Vec3(0, 0, 0)
        self.boost_value = 0
        self.has_wheel_contact = False
        self.has_the_ball = False
        self.is_supersonic = False

class BallData:
    def __init__(self):
        self.position = Vec3(0, 0, 0)
        self.rotation = 0
        self.velocity = Vec3(0, 0, 0)
        self.angular_velocity = Vec3(0, 0, 0)

class GoalData:
    def __init__(self):
        self.position = Vec3(0, 0, 0)
        self.distance_to_post = 893