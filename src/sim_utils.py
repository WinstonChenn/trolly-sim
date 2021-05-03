"""
Winston Chen
5/3/2021
Utilities for trolly problem simulation enviorment setup
"""
import random


class Simulator:
    def __init__(self, n, full_info, seed, track_max=5, pass_max=5):
        """
        n: number of trollies in the simulation
        full_info: wether or not trollies have full information
                   see definition in proposal
        seed: random seed
        track_max: maximum possible number of people tied on one track
        pass_max: maximum possible number of passengers on a trolly
        """
        self.n = n
        self.full_info = full_info
        self.seed = seed
        self.track_max = track_max
        self.pass_max = pass_max

        random.seed(seed)
        # random number of people tied to each track
        self.tracks = [random.randint(0, track_max) for i in range(n)] 
        # n trolly objects need to be manually set later with object calls
        self.trollies = [None for i in range(n)]

    def trolly_track_lookup(self, trolly_idx):
        """
        helper function that returns the 2 track indices belong to the given
        indexed trolly
        """
        if trolly_idx < 0 or trolly_idx >= self.n:
            raise ValueError(f"trolly index out of bound, n={self.n}, trolly_idx={trolly_idx}")
        
        if trolly_idx == self.n-1:
            return (trolly_idx, 0)
        else:
            return (trolly_idx, trolly_idx+1)

    def set_trolly_by_idx(self, idx, trolly_obj):
        self.trollies[idx] = trolly_obj

