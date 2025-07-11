import shutil

import finitewave as fw

# number of nodes on the side
n = 400
tissue = fw.CardiacTissue2D([n, n])
tissue.conductivity = 0.2

# set up stimulation parameters:
stim_sequence = fw.StimSequence()
stim_sequence.add_stim(fw.StimVoltageCoord2D(70, 1, n // 4, 3 * n // 4, 0, n // 2))

# set up tracker:
tracker_sequence = fw.TrackerSequence()
animation_tracker = fw.Animation2DTracker()
animation_tracker.variable_name = "u"
animation_tracker.dir_name = "data/phase_defect"
animation_tracker.step = 20
animation_tracker.overwrite = True
tracker_sequence.add_tracker(animation_tracker)

# create model object and set up parameters:
fenton_karma = fw.FentonKarma2D()
fenton_karma.dt = 0.01
fenton_karma.dr = 0.25
fenton_karma.t_max = 400

# add the tissue and the stim parameters to the model object:
fenton_karma.cardiac_tissue = tissue
fenton_karma.stim_sequence = stim_sequence
fenton_karma.state_loader = fw.StateLoader("data/s1_state")
fenton_karma.tracker_sequence = tracker_sequence

# run the model:
fenton_karma.run()

# create video:
animation_tracker.write(cmap="viridis", fps=50)
shutil.move("data/animation.mp4", "videos/phase_defect.mp4")
