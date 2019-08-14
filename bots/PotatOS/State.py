import math
import time

from rlbot.agents.base_agent import SimpleControllerState
from util.orientation import Orientation
from util.vec import *
from Util import *

class KickOffState:
    def __init__(self):
        pass

    def valid(self, agent):
        isValid = False
        if Velocity2D(agent.BallDataAgent) == 0.0:
            isValid = True

        return isValid

    def execute(self, agent):
        agent.currentController = kickOffController

        our_position = agent.OurData.position
        ball_position = agent.BallDataAgent.position

        car_to_ball = ball_position - our_position

        return agent.currentController(agent, car_to_ball, 99999)

class chaseState:
    def __init__(self):
        pass

    def valid(self, agent):
        isValid = False
        if not agent.OurData.has_the_ball:
            isValid = True
        return isValid

    def execute(self, agent):

        agent.currentController = chaseController

        # Where's the ball compared to us?
        # target = agent.BallDataAgent.position + 0.3 * agent.BallDataAgent.velocity
        agentLocation = agent.OurData.position

        # How fast is the ball going?
        #print(Distance2D(agent.BallLocation, agent.VehicleLocation))

        # is the ball in the air or not?
        if agent.BallDataAgent.position.z > 150 and len(agent.BouncePoints) != 0:
            # it is
            target = Vec3(agent.BouncePoints[0].physics.location)
            targetvelocity = Velocity2D(agent.BouncePoints[0].physics) + math.sqrt((agent.BouncePoints[0].physics.location.x - agent.OurData.position.x)**2 + (agent.BouncePoints[0].physics.location.y - agent.OurData.position.y)**2)/1.5
        else:
            #it isn't
            target = agent.BallDataAgent.position + 0.3 * agent.BallDataAgent.velocity
            car_to_target = target - agentLocation

            car_orientation = Orientation(agent.OurData.rotation)
            car_direction = car_orientation.forward

            steer_correction_radians = find_correction(car_direction, car_to_target)

            if -0.1 < steer_correction_radians < 0.1:
                targetvelocity = 2300
            else:
                targetvelocity = Velocity2D(agent.BallDataAgent) + Distance2D(agent.BallDataAgent, agent.OurData)/1.3

        car_to_target = target - agentLocation
        # print(targetvelocity)

        return agent.currentController(agent, car_to_target, targetvelocity)

class shootState:
    def __init__(self):
        pass

    def valid(self, agent):
        isValid = False
        if agent.OurData.has_the_ball:
            isValid = True
        return isValid

    def execute(self, agent):

        agent.currentController = shotController

        # Where's the ball compared to us?
        target = agent.TheirGoal.centre
        agentLocation = agent.OurData.position

        car_to_target = target - agentLocation

        return agent.currentController(agent, car_to_target, 9999999)

class GetBoostState:
    def __init__(self):
        pass

    def valid(self, agent):
        pass

    def execute(self, agent):

        agent.currentController = boostController

        highest_pad_score = 0.0

        for pad in agent.FullBoostPads:
            vehicle_to_pad = pad - agent.OurData.position
            distance_to_pad = vehicle_to_pad.length()
            distanceScore = 1 - (distance_to_pad / 3500)

            required_correction = find_correction(Orientation(agent.OurData.rotation).forward,
                                                 vehicle_to_pad)
            correctionScore = 1 - (math.fabs(required_correction) / (math.pi / 2))

            totalScore = (distanceScore * 0.6) + (correctionScore * 0.4)

            if highest_pad_score < totalScore:
                highest_pad_score = totalScore
                currentBestPad = pad

        car_to_pad = currentBestPad - agent.OurData.position

        return agent.currentController(agent, car_to_pad, 0)

def shotController(agent, targetLocation, targetVelocity):
    controller_state = SimpleControllerState()
    car_orientation = Orientation(agent.OurData.rotation)
    car_direction = car_orientation.forward

    steer_correction_radians = find_correction(car_direction, targetLocation)

    # Throttle

    controller_state.throttle = 1

    # Boost

    controller_state.boost = False

    # Steering
    if steer_correction_radians > 0.07:
        # Positive radians in the unit circle is a turn to the left.
        turn = -1.0  # Negative value for a turn to the left.
        action_display = "turn left"
    elif steer_correction_radians < -0.07:
        turn = 1.0
        action_display = "turn right"
    else:
        turn = 0.0

    # Flips and stuff
    time_difference = time.time() - agent.start
    if time_difference > 2.2 and steer_correction_radians < 0.07 and steer_correction_radians > -0.07 and math.fabs(agent.TheirGoal.centre.y - agent.OurData.position.y) <5800\
            and agent.OurData.position.x < 3696 and agent.OurData.position.x > -3696:
        agent.start = time.time()
        controller_state.jump = False
        controller_state.use_item = False
        controller_state.pitch = 0
    elif time_difference <= 0.3:
        controller_state.jump = True
        controller_state.pitch = 1
        controller_state.yaw = turn
    elif time_difference >= 0.3 and time_difference <= 0.35:
        controller_state.jump = False
        controller_state.pitch = -1
        controller_state.yaw = turn
    elif time_difference >= 0.35 and time_difference <= 0.45:
        controller_state.pitch = -1
        controller_state.yaw = turn
    elif time_difference >= 0.45 and time_difference <= 0.49:
        controller_state.pitch = -1
        controller_state.jump = True
    elif time_difference >= 0.49 and time_difference <= 0.52:
        controller_state.use_item = True
    elif time_difference >= 0.52:
        agent.controller_state.use_item = False
        controller_state.yaw = turn

    controller_state.steer = turn

    return controller_state

def chaseController(agent, targetLocation, targetVelocity):
    controller_state = SimpleControllerState()
    car_orientation = Orientation(agent.OurData.rotation)
    car_direction = car_orientation.forward
    currentvelocity = Velocity2D(agent.OurData)

    steer_correction_radians = find_correction(car_direction, targetLocation)

    if steer_correction_radians > 0.1:
        # Positive radians in the unit circle is a turn to the left.
        turn = -1.0  # Negative value for a turn to the left.
        action_display = "turn left"
    elif steer_correction_radians < -0.1:
        turn = 1.0
        action_display = "turn right"
    else:
        turn = 0.0

    if currentvelocity < targetVelocity:
        controller_state.throttle = 1.0
    else:
        controller_state.throttle = 0.0
    controller_state.steer = turn
    controller_state.yaw = turn

    if targetVelocity > 1400 and currentvelocity > 1300 and not agent.OurData.is_supersonic:
        controller_state.boost = True
    else:
        controller_state.boost = False

    return controller_state

def kickOffController(agent, targetLocation, targetVelocity):
    controller_state = SimpleControllerState()
    car_orientation = Orientation(agent.OurData.rotation)
    car_direction = car_orientation.forward

    steer_correction_radians = find_correction(car_direction, targetLocation)

    #Throttle

    controller_state.throttle = 1

    #Boost

    controller_state.boost = True

    #Steering
    if steer_correction_radians > 0.1:
        # Positive radians in the unit circle is a turn to the left.
        turn = -1.0  # Negative value for a turn to the left.
        action_display = "turn left"
    elif steer_correction_radians < -0.1:
        turn = 1.0
        action_display = "turn right"
    else:
        turn = 0.0

    #Flips and stuff
    time_difference = time.time() - agent.start
    if time_difference > 2.2 and steer_correction_radians < 0.2 and steer_correction_radians > -0.2 and Distance2D(agent.BallDataAgent, agent.OurData) < 700:
        agent.start = time.time()
    elif time_difference <= 0.1:
        controller_state.jump = True
        controller_state.pitch = -1
    elif time_difference >= 0.1 and time_difference <= 0.15:
        controller_state.jump = False
        controller_state.pitch = -1
    elif time_difference > 0.15 and time_difference < 1:
            controller_state.jump = True
            controller_state.yaw = turn
            controller_state.pitch = -1

    controller_state.steer = turn

    return controller_state

def boostController(agent, targetLocation, targetSpeed):
    controller_state = SimpleControllerState()
    car_orientation = Orientation(agent.OurData.rotation)
    car_direction = car_orientation.forward

    steer_correction_radians = find_correction(car_direction, targetLocation)

    if steer_correction_radians > 0.1:
        # Positive radians in the unit circle is a turn to the left.
        turn = -1.0  # Negative value for a turn to the left.
        action_display = "turn left"
    elif steer_correction_radians < - 0.1:
        turn = 1.0
        action_display = "turn right"
    else:
        turn = 0.0
        action_display = "straight ahead"

    controller_state.throttle = 1.0

    # if not agent.OurData.is_supersonic:
    #     controller_state.boost = 1
    # else:
    controller_state.boost = 0

    controller_state.steer = turn
    controller_state.yaw = turn

    return controller_state




