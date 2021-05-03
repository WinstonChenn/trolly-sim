# Multi-agent trolly problem simulation
## Problem Setup: 
There are n AI-trolleys with malfunctioning brakes barreling down n parallel railway tracks. Ahead of them on the tracks, there are random numbers of people tied up on each of the tracks. Each AI-trolly can independently make the decision to:
  1. stay in the same track 
  2. switch to a neighboring track. 

For each option they chose, there will be two possible outcomes: 
  1. They are the only trolly on that track, and they only kill the people tied on that track.
  2. They run into a neighboring trolly or a neighboring trolly runs into them. Passengers on both trolleys and the people tied on the track are all killed.

