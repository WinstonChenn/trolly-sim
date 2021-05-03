"""
Winston Chen
5/3/2021
Utilities for trolly agents' logic setup
"""
import random
import numpy as np


class BaseAgent:
    def __init__(self, seed, pass_max=5, track_max=5):
        self.pass_max = pass_max
        self.track_max = track_max

        self.pass_num = None
        self.track_num = None
        self.neighbor_track_num = None

        # additional information
        self.neighbor_pass_num_1 = None # neighbor trolly that can run into current one
        self.neighbor_pass_num_2 = None # neighbor trolly that can be run into by the current one
        random.seed(seed)

    def set_pass_num(self, num):
        self.pass_num = num

    def set_neighbor_pass_num(self, neighbor_1, neighbor_2):
        self.neighbor_pass_num_1 = neighbor_1
        self.neighbor_pass_num_2 = neighbor_2

    def set_track_num(self, num):
        self.track_num = num

    def set_neighor_track_num(self, num):
        self.neighbor_track_num = num

    def check_info(self, full_info):
        if (self.pass_num is None) or (self.track_num is None) \
           or (self.neighbor_track_num is None):
            raise ValueError("Insufficient Information")
        if full_info and (self.neighbor_pass_num_1 is None or
                          self.neighbor_pass_num_2 is None):
            raise ValueError("Missing neighbor passanger information")


class RandomAgent(BaseAgent):
    def make_decision(self, full_info):
        self.check_info(full_info)
        return random.randint(0, 1)


class AlwaysDoNothingAgent(BaseAgent):
    def make_decision(self, full_info):
        self.check_info(full_info)
        return 0


class AlwaysSwitchAgent(BaseAgent):
    def make_decision(self, full_info):
        self.check_info(full_info)
        return 1


class TrackLifeAgent(BaseAgent):
    def make_decision(self, full_info):
        self.check_info(full_info)
        if self.track_num > self.neighbor_track_num:
            return 1
        else:
            return 0


class StatAgetn(BaseAgent):
    def make_decision(self, full_info):
        self.check_info(full_info)
        if full_info:
            E_neighbor_pass_num_1 = self.neighbor_pass_num_1
            E_neighbor_pass_num_2 = self.neighbor_pass_num_2
        else:
            E_neighbor_pass_num_1 = np.sum([i for i in range(self.pass_max+1)])/self.pass_max
            E_neighbor_pass_num_2 = np.sum([i for i in range(self.pass_max+1)])/self.pass_max

        E_loss_stay = (2*self.track_num + self.pass_num + E_neighbor_pass_num_1)/2
        E_loss_switch = (2*self.neighbor_track_num + self.pass_num + E_neighbor_pass_num_2)/2

        if E_loss_stay > E_loss_switch:
            return 1
        else:
            return 0
