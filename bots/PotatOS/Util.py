from util.orientation import Orientation
from util.vec import Vec3

import math

def find_correction(current: Vec3, ideal: Vec3) -> float:
    # Finds the angle from current to ideal vector in the xy-plane. Angle will be between -pi and +pi.

    # The in-game axes are left handed, so use -x
    current_in_radians = math.atan2(current.y, -current.x)
    ideal_in_radians = math.atan2(ideal.y, -ideal.x)

    diff = ideal_in_radians - current_in_radians

    # Make sure that diff is between -pi and +pi.
    if abs(diff) > math.pi:
        if diff < 0:
            diff += 2 * math.pi
        else:
            diff -= 2 * math.pi

    return diff


def draw_debug(renderer, car, ball, action_display):
    renderer.begin_rendering()
    # draw a line from the car to the ball
    renderer.draw_line_3d(car.physics.location, ball.physics.location, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()

def sign(x):
    if x <= 0:
        return -1
    else:
        return 1

def Velocity2D(target_object):
    return math.sqrt(target_object.velocity.x ** 2 + target_object.velocity.y**2)

def Distance2D(target_object, our_object):
    difference = target_object.position - our_object.position
    return math.sqrt(difference.x ** 2 + difference.y ** 2)