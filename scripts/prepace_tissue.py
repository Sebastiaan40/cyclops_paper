import finitewave as fw
import matplotlib.pyplot as plt
import numpy as np

# number of nodes on the side
n = 400
tissue = fw.CardiacTissue2D([n, n])

# set up stimulation parameters:
stim_sequence = fw.StimSequence()

num_of_beats = 10
interval = 200
for i in range(num_of_beats):
    stim_sequence.add_stim(fw.StimVoltageCoord2D(i * interval, 1, 0, -1, 0, 5))

# set up state saver parameters:
state_saver = fw.StateSaver("data/s1_state")

# set up action potential tracker:
tracker_sequence = fw.TrackerSequence()
action_pot_tracker = fw.ActionPotential2DTracker()
action_pot_tracker.cell_ind = [n // 2, n // 2]
tracker_sequence.add_tracker(action_pot_tracker)

# create model object and set up parameters:
fenton_karma = fw.FentonKarma2D()
fenton_karma.dt = 0.01
fenton_karma.dr = 0.25
fenton_karma.t_max = 2000

# add the tissue and the stim parameters to the model object:
fenton_karma.cardiac_tissue = tissue
fenton_karma.stim_sequence = stim_sequence
fenton_karma.state_saver = state_saver
fenton_karma.tracker_sequence = tracker_sequence

# run the model:
fenton_karma.run()

# plot action potential:
time = np.arange(len(action_pot_tracker.output)) * fenton_karma.dt
plt.plot(time, action_pot_tracker.output)
plt.xlabel("t[ms]")
plt.ylabel("E[mV]")
plt.show()
