from pathlib import Path

import finitewave as fw
import matplotlib.pyplot as plt
import numpy as np

# number of nodes on the side
n = 400
tissue = fw.CardiacTissue2D([n, n])
tissue.mesh[n // 4 - 64 : n // 4 + 64, n // 2 - 64 : n // 2 + 64] = 0
tissue.conductivity = 0.15 * np.ones([n, n])

# show conductivity of mesh
plt.imshow(tissue.mesh * tissue.conductivity)
plt.show()

# set up stimulation parameters:
stim_sequence = fw.StimSequence()
s2 = fw.StimVoltageCoord2D(60, 1, n // 4, 3 * n // 4, 0, n // 2)
stim_sequence.add_stim(s2)
s3 = fw.StimVoltageCoord2D(
    640, 1, 3 * n // 4 - 64, 3 * n // 4 + 64, 3 * n // 4, 3 * n // 4 + 8
)
stim_sequence.add_stim(s3)

# set up trackers:
tracker_sequence = fw.TrackerSequence()
u_tracker = fw.Animation2DTracker()
u_tracker.variable_name = "u"
u_tracker.dir_name = "data/demo_2"
u_tracker.step = 20
u_tracker.overwrite = True
tracker_sequence.add_tracker(u_tracker)

v_tracker = fw.Animation2DTracker()
v_tracker.variable_name = "v"
v_tracker.dir_name = "data/demo_2"
v_tracker.step = 20
v_tracker.overwrite = True
tracker_sequence.add_tracker(v_tracker)

# create model object and set up parameters:
fenton_karma = fw.FentonKarma2D()
fenton_karma.dt = 0.01
fenton_karma.dr = 0.25
fenton_karma.t_max = 1000

# add the tissue and the stim parameters to the model object:
fenton_karma.cardiac_tissue = tissue
fenton_karma.stim_sequence = stim_sequence
fenton_karma.state_loader = fw.StateLoader("data/s1_state")
fenton_karma.tracker_sequence = tracker_sequence

# run the model:
fenton_karma.run()

# calculate phase:
output_dir = Path("data/phase")
u_path = Path(u_tracker.path, u_tracker.dir_name)
v_path = Path(v_tracker.path, v_tracker.dir_name)
if output_dir.is_dir():
    output_dir.mkdir(parents=True)

n = len(list(u_path.glob("*.npy")))
u_min_val = np.inf
u_max_val = -np.inf
v_min_val = np.inf
v_max_val = -np.inf

for i in range(n):
    u = np.load(u_path / f"{i}.npy")
    u_min_val = min(u_min_val, np.nanmin(u))
    u_max_val = max(u_max_val, np.nanmax(u))

    v = np.load(v_path / f"{i}.npy")
    v_min_val = min(v_min_val, np.nanmin(u))
    v_max_val = max(v_max_val, np.nanmax(u))

for i in range(n):
    u = np.load(u_path / f"{i}.npy")
    v = np.load(v_path / f"{i}.npy")
    u = 2 * (u - u_min_val) / (u_max_val - u_min_val) - 1
    v = 2 * (v - v_min_val) / (v_max_val - v_min_val) - 1
    phase = np.arctan2(u, v)
    np.save(output_dir / f"{i}.npy", phase)

# create video:
fw.Animation2DBuilder().write(
    output_dir,
    clim=(-np.pi, np.pi),
    shape=fenton_karma.cardiac_tissue.mesh.shape,
    cmap="twilight",
    clear=False,
    prog_bar=True,
)
