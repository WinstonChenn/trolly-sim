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
        self.def_track_num = None
        self.alt_track_num = None

        random.seed(seed)

    def set_pass_num(self, num):
        """set the number of passengers on the agent"""
        self.pass_num = num

    def set_track_nums(self, def_num, alt_num):
        """
        num1: number of people on default track
        num2: number of people on the alternative track
        """
        self.def_track_num = def_num
        self.alt_track_num = alt_num

    def get_pass_num(self):
        return self.pass_num

    def get_track_nums(self):
        return (self.def_track_num, self.alt_track_num)

    def check_info(self):
        if (self.pass_num is None) or (self.def_track_num is None) \
           or (self.alt_track_num is None):
            raise ValueError("Insufficient Information")


class RandomAgent(BaseAgent):
    def __str__(self):
        return "RandomAgent"

    def make_decision(self, def_neigh_pass_num=None, alt_neigh_pass_num=None):
        self.check_info()
        return random.randint(0, 1)


class AlwaysDoNothingAgent(BaseAgent):
    def __str__(self):
        return "AlwaysDoNothingAgent"

    def make_decision(self, def_neigh_pass_num=None, alt_neigh_pass_num=None):
        self.check_info()
        return 0


class AlwaysSwitchAgent(BaseAgent):
    def __str__(self):
        return "AlwaysSwitchAgent"

    def make_decision(self, def_neigh_pass_num=None, alt_neigh_pass_num=None):
        self.check_info()
        return 1


class TrackLifeAgent(BaseAgent):
    def __str__(self):
        return "TrackLifeAgent"

    def make_decision(self, def_neigh_pass_num=None, alt_neigh_pass_num=None):
        self.check_info()
        if self.def_track_num > self.alt_track_num:
            return 1
        else:
            return 0


class StatAgent(BaseAgent):
    def __str__(self):
        return "StatAgent"

    def make_decision(self, def_neigh_pass_num=None, alt_neigh_pass_num=None):
        self.check_info()
        if def_neigh_pass_num and alt_neigh_pass_num:
            E_def_neigh_pass_num = def_neigh_pass_num
            E_alt_neighbor_pass_num = alt_neigh_pass_num
        else:
            E_def_neigh_pass_num = np.sum([i for i in range(self.pass_max+1)])/self.pass_max
            E_alt_neighbor_pass_num = np.sum([i for i in range(self.pass_max+1)])/self.pass_max

        E_loss_stay = (2*self.def_track_num+self.pass_num+E_def_neigh_pass_num)/2
        E_loss_switch = (2*self.alt_track_num+self.pass_num+E_alt_neighbor_pass_num)/2

        if E_loss_stay > E_loss_switch:
            return 1
        else:
            return 0
