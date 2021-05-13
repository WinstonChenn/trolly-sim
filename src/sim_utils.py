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

        # random.seed(seed)
        # random number of people tied to each track
        self.track_nums = [random.randint(0, track_max) for i in range(n)]
        self.trolly_pass_nums = [random.randint(0, pass_max) for i in range(n)]
        # n trolly objects need to be manually set later with object calls
        self.trollies = [None for i in range(n)]

        # accumulators for each trials
        self.total_pass = 0  # total number of passengers
        self.total_track = 0  # total number of people on the track
        self.total_trials = 0  # total number of trials done so far
        # total passengers & track people kileed by each trolly
        self.trolly_kill_dict = [{"pass": 0, "track": 0} for i in range(n)] 

        self.total_pass_kill = 0 # total number of passengers killed
        self.total_track_kill = 0 # total number of people on the track killed
        # total passengers & track people encountered by each trolly
        # (include people from both tracks)
        self.trolly_tot_dict = [{"pass": 0, "track": 0} for i in range(n)]

    def clear_records(self):
        # accumulators for each trials
        self.total_pass = 0  # total number of passengers
        self.total_track = 0  # total number of people on the track
        self.total_trials = 0  # total number of trials done so far
        # total passengers & track people kileed by each trolly
        self.trolly_kill_dict = [{"pass": 0, "track": 0} for i in range(self.n)] 

        self.total_pass_kill = 0  # total number of passengers killed
        self.total_track_kill = 0  # total number of people on the track killed
        # total passengers & track people encountered by each trolly
        # (include people from both tracks)
        self.trolly_tot_dict = [{"pass": 0, "track": 0} for i in range(self.n)]

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

    def trolly_neighbor_lookup(self, trolly_idx):
        """
        helper function that returns the 2 neighbor indices belong to the given
        indexed trolly
        (default_track_neighbor_idx, alternative_tracek_neighbor_idx)
        """
        if trolly_idx < 0 or trolly_idx >= self.n:
            raise ValueError(f"trolly index out of bound, n={self.n}, trolly_idx={trolly_idx}")
        if trolly_idx == 0:
            return (self.n-1, 1)
        elif trolly_idx == self.n-1:
            return (self.n-2, 0)
        else:
            return (trolly_idx-1, trolly_idx+1)

    def set_trolly_by_idx(self, idx, trolly_obj):
        trolly_obj.set_pass_num(self.trolly_pass_nums[idx])
        self.trollies[idx] = trolly_obj

    def batch_set_trollies(self, trolly_arr):
        assert len(trolly_arr) == self.n
        assert None not in trolly_arr
        self.trollies = trolly_arr

    def refresh_track_nums(self):
        """update the number of people on all the tracks """
        self.track_nums = [random.randint(0, self.track_max) for i in range(self.n)]

    def refresh_pass_nums(self):
        """update the number of people on all the tracks """
        self.trolly_pass_nums = [random.randint(0, self.pass_max) for i in range(self.n)]

    def get_tot_tele_loss(self):
        return (self.total_pass_kill + self.total_track_kill) / (self.total_pass + self.total_track)

    def get_tot_dele_loss(self):
        return (self.total_pass_kill) / (self.total_pass)

    def get_tele_loss_by_idx(self, idx_arr):
        tot_kills = 0
        tot_ecounter = 0
        for i in idx_arr:
            tot_kills += self.trolly_kill_dict[i]['pass']
            tot_kills += self.trolly_kill_dict[i]['track']
            tot_ecounter += self.trolly_tot_dict[i]['pass']
            tot_ecounter += self.trolly_tot_dict[i]['track']

        return tot_kills/tot_ecounter

    def get_dele_loss_by_idx(self, idx_arr):
        tot_pass_kills = 0
        tot_pass_ecounter = 0
        for i in idx_arr:
            tot_pass_kills += self.trolly_kill_dict[i]['pass']
            tot_pass_ecounter += self.trolly_tot_dict[i]['pass']

        return tot_pass_kills/tot_pass_ecounter


    def run_trial(self):
        track_chosen_arr = []
        self.total_trials += 1
        self.total_pass += sum(self.trolly_pass_nums)
        self.total_track += sum(self.track_nums)
        for idx, trolly in enumerate(self.trollies):
            # update passanger number
            trolly.set_pass_num(self.trolly_pass_nums[idx])
            (def_idx, alt_idx) = self.trolly_track_lookup(idx)
            trolly.set_track_nums(def_num=self.track_nums[def_idx], \
                                  alt_num=self.track_nums[alt_idx])
            if self.full_info:
                (def_neigh_idx, alt_neigh_idx) = self.trolly_neighbor_lookup(idx)
                def_neigh_pass_num = self.trolly_pass_nums[def_neigh_idx]
                alt_neigh_pass_num = self.trolly_pass_nums[alt_neigh_idx]
            else:
                def_neigh_pass_num = None
                alt_neigh_pass_num = None

            self.trolly_tot_dict[idx]["pass"] += trolly.get_pass_num()
            self.trolly_tot_dict[idx]["track"] += sum(trolly.get_track_nums())

            decision = trolly.make_decision(def_neigh_pass_num, alt_neigh_pass_num)
            track_chosen_arr.append(self.trolly_track_lookup(idx)[decision])

        # record kill stats for individual trolly
        for i, track_idx in enumerate(track_chosen_arr):
            trolly_idx = [i for i, e in enumerate(track_chosen_arr) if e == track_idx]
            assert len(trolly_idx) == 1 or len(trolly_idx) == 2
            assert i == trolly_idx[0] or i == trolly_idx[1]
            if len(trolly_idx) == 2:
                self.trolly_kill_dict[i]["pass"] += self.trolly_pass_nums[i]
            self.trolly_kill_dict[i]['track'] += self.track_nums[track_idx]

        # record total kill stats
        for i, track_idx in enumerate(set(track_chosen_arr)):
            trolly_idx = [i for i, e in enumerate(track_chosen_arr) if e == track_idx]
            assert len(trolly_idx) == 1 or len(trolly_idx) == 2
            if len(trolly_idx) == 2:
                self.total_pass_kill += ((self.trolly_pass_nums[trolly_idx[0]] \
                    + self.trolly_pass_nums[trolly_idx[1]]))
            self.total_track_kill += self.track_nums[track_idx]
        # print(track_chosen_arr)
        # print(self.total_pass_kill, self.total_track_kill)
        # print(self.total_trials, self.total_pass, self.total_track)
        # print(self.trolly_kill_dict)
        # print(self.trolly_tot_dict)
        return self.trolly_kill_dict



