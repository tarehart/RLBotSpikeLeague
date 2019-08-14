import math, time

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation
from util.vec import Vec3
from State import *
from util.structs import *
from Util import *

class PotatOS(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up
        self.OurData = CarData()
        self.OpponentData = CarData()
        self.BallDataAgent = BallData()
        self.TheirGoal = GoalData()
        self.FullBoostPads = []
        self.BouncePoints = []

        self.start = time.time()
        self.currentState = KickOffState()
        self.currentController = kickOffController

        self.controller_state = SimpleControllerState()

    def checkState(self):
        if KickOffState().valid(self):
            self.currentState = KickOffState()
        elif shootState().valid(self):
             self.currentState = shootState()
        elif self.getFuzzyScore() >= 2.0:
            self.currentState = GetBoostState()
        else:
            self.currentState = chaseState()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        self.preprocessing(packet)
        self.checkState()
        return self.currentState.execute(self)

    def getFuzzyScore(self):
        fuzzy_score = 0
        # Boost
        fuzzy_score += max(min(1.0 - (self.OurData.boost_value/50), 1.0), 0.0)

        # self_distance_from_ball = Distance2D(self.BallDataAgent, self.OurData)
        # fuzzy_score += max(min((self_distance_from_ball/1000), 1.0), 0.0)

        ball_distance_from_halfway = -sign(self.team) * self.BallDataAgent.position.y
        fuzzy_score += max(min(ball_distance_from_halfway/5120, 1.0), 0.0)

        opponent_distance_from_ball = Distance2D(self.BallDataAgent, self.OpponentData)
        your_distance_from_ball = Distance2D(self.BallDataAgent, self.OurData)

        if your_distance_from_ball > opponent_distance_from_ball:
            fuzzy_score += max(min(opponent_distance_from_ball/2000, 1.0), 0.0)

        # print(fuzzy_score)
        return fuzzy_score

    def preprocessing(self, packet):
        # Let's get some data, boys!
        # First, our car!

        self.OurData.position = Vec3(packet.game_cars[self.index].physics.location)
        self.OurData.rotation = packet.game_cars[self.index].physics.rotation
        self.OurData.velocity = Vec3(packet.game_cars[self.index].physics.velocity)
        self.OurData.angular_velocity = Vec3(packet.game_cars[self.index].physics.angular_velocity)
        self.OurData.boost_value = packet.game_cars[self.index].boost
        self.OurData.has_wheel_contact = packet.game_cars[self.index].has_wheel_contact
        self.OurData.is_supersonic = packet.game_cars[self.index].is_super_sonic

        #What's the other guy's index?
        opponent_index = -1
        for x in range(packet.num_cars):
            if x != self.index:
                opponent_index = x

        #Now let's find out some stuff about him.

        self.OpponentData.position = Vec3(packet.game_cars[opponent_index].physics.location)
        self.OpponentData.rotation = packet.game_cars[opponent_index].physics.rotation
        self.OpponentData.velocity = Vec3(packet.game_cars[opponent_index].physics.velocity)
        self.OpponentData.angular_velocity = Vec3(packet.game_cars[opponent_index].physics.angular_velocity)
        self.OpponentData.boost_value = packet.game_cars[opponent_index].boost
        self.OpponentData.has_wheel_contact = packet.game_cars[opponent_index].has_wheel_contact

        # Now the ball.

        self.BallDataAgent.position = Vec3(packet.game_ball.physics.location)
        self.BallDataAgent.rotation = packet.game_ball.physics.rotation
        self.BallDataAgent.velocity = Vec3(packet.game_ball.physics.velocity)
        self.BallDataAgent.angular_velocity = Vec3(packet.game_ball.physics.angular_velocity)

        #Who has the ball right now?
        self.OurData.has_the_ball = (self.BallDataAgent.position - self.OurData.position).length() < 200
        self.OpponentData.has_the_ball = (self.BallDataAgent.position - self.OpponentData.position).length() < 200

        # Where's their goal?
        self.TheirGoal.centre = Vec3(0, -sign(self.team)*(5120+200), 0)

        # Finally, get me a list of every single active boost pad on the field right now.
        self.FullBoostPads.clear()
        # print(len(self.fullBoostPads))
        field_info = self.get_field_info()

        for i in range(field_info.num_boosts):
            pad = field_info.boost_pads[i]
            packetPad = packet.game_boosts[i]
            if packetPad.timer <= 0:
                self.FullBoostPads.append(Vec3(pad.location))

        # experimental ball path prediction stuff

        self.BallPredictionData = self.get_ball_prediction_struct()

        self.BouncePoints.clear()

        for i in range(0, self.BallPredictionData.num_slices-1):
            currentSlice = self.BallPredictionData.slices[i]
            nextSlice = self.BallPredictionData.slices[i+1]

            if (currentSlice.physics.velocity.z <= 0 and 0 < nextSlice.physics.velocity.z):
                self.BouncePoints.append(currentSlice)

        # if self.BallDataAgent is not None and len(self.BouncePoints) > 5:
        #
        #     self.renderer.begin_rendering()
        #
        #     for i in range(0, 5):
        #         slice = self.BouncePoints[i]
        #         time_to_landing = slice.game_seconds - packet.game_info.seconds_elapsed
        #
        #
        #         self.renderer.draw_string_3d(slice.physics.location, 2, 2, str(time_to_landing), self.renderer.white())
        #     self.renderer.end_rendering()

