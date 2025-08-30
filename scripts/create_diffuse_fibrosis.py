from pathlib import Path

import finitewave as fw
import matplotlib.pyplot as plt
import numpy as np

n = 400
# create mesh
np.random.seed(42)  # a seed is set to make the results reproducible
tissue = fw.CardiacTissue2D((n, n))
tissue.add_pattern(fw.Diffuse2DPattern(0.3))
tissue.conductivity =0.3

# set up stimulation parameters:
stim_sequence = fw.StimSequence()
stim_sequence.add_stim(fw.StimVoltageCoord2D(60, 1, n // 5, 4 * n // 5, 0, 3 * n // 4))

# set up trackers:
tracker_sequence = fw.TrackerSequence()
u_tracker = fw.Animation2DTracker()
u_tracker.variable_name = "u"
u_tracker.dir_name = "data/diffuse_fibrosis/u"
u_tracker.step = 20
u_tracker.overwrite = True
tracker_sequence.add_tracker(u_tracker)

v_tracker = fw.Animation2DTracker()
v_tracker.variable_name = "v"
v_tracker.dir_name = "data/diffuse_fibrosis/v"
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
# adjust the number of threads if needed
fenton_karma.run(num_of_theads=15)

# calculate phase:
output_dir = Path("data/diffuse_fibrosis/phase")
u_path = Path(u_tracker.path, u_tracker.dir_name)
v_path = Path(v_tracker.path, v_tracker.dir_name)
if not output_dir.is_dir():
    output_dir.mkdir(parents=True)


track_u = []
track_v = []
x, y = 200, 200

u_ref = 0.4
v_ref = 0.1
timesteps = len(list(u_path.glob("*.npy")))
for i in range(timesteps):
    u = np.load(u_path / f"{i}.npy") - u_ref
    v = np.load(v_path / f"{i}.npy") - v_ref
    track_u.append(u[x, y].copy())
    track_v.append(v[x, y].copy())
    phase = np.arctan2(u, v)
    phase[tissue.mesh != 1] = np.nan
    np.save(output_dir / f"{i}.npy", phase)

# visually confirm that the orbit in phase space goes around the origin
plt.plot(track_u, track_v)
plt.show()

# create video:
fw.Animation2DBuilder().write(
    output_dir,
    clim=(-np.pi, np.pi),
    shape=fenton_karma.cardiac_tissue.mesh.shape,
    cmap="twilight",
    clear=False,
    prog_bar=True,
    fps=100,
)
