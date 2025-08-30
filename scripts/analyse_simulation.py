from pathlib import Path

import cyclops.cycletools as ct
import cyclops.phasetools as ft
import cyclops.visualtools as vt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvista as pv
from cyclops.extended_phasemapping import ExtendedPhaseMapping

data_dir = Path("data/near_complete_rotation")

u_path = data_dir / "u"
phase_path = data_dir / "phase"

# load action potentials and phases
list_of_phases = []
list_of_action_potentials = []

step = 4
start = 2800
stop = len(list(u_path.glob("*.npy")))
for i in range(start, stop, step):
    list_of_action_potentials.append(np.load(u_path / f"{i}.npy").ravel())
    list_of_phases.append(np.load(phase_path / f"{i}.npy").ravel())

phases = np.column_stack(list_of_phases)
action_potentials = np.column_stack(list_of_action_potentials)
phases = np.tanh((-1 * phases) % (2 * np.pi) - np.pi) * np.pi

# plot phase and action potential of one point
plt.plot(phases[500], label="phase", marker=".")
plt.plot(action_potentials[500, :stop], label="normalized action potential")
plt.xlabel("timesteps")
plt.legend()
plt.savefig("paper/figures/ap_phase.svg")
plt.show()

# create phase field
nx, ny = np.load(u_path / "0.npy").shape
polydata = pv.ImageData(dimensions=(nx, ny, 1), spacing=(1, 1, 1)).extract_surface()
phasefield = ft.PhaseField(polydata, phases)

phasefield_filters = [ft.NaNFilter(), ft.PhaseDiffFilter(0.05 * np.pi)]
cycle_extractors = [ct.extract_face_cycles, ct.extract_boundary_cycles]
epm = ExtendedPhaseMapping(phasefield, phasefield_filters, cycle_extractors)
epm.run()

# visualise results
slider = vt.Slider(epm)
slider.show()

# Create phase density map
data = [epm.critical_cycles]
nodes = (
    pd.concat(data)
    .groupby("time_axis")["nodes"]
    .apply(lambda nodes: [x for xs in nodes for x in xs])
)

nodes_per_time_step = nodes.apply(np.unique).to_list()
point_ids, count = np.unique(np.concatenate(nodes_per_time_step), return_counts=True)
all_points = np.zeros(nx * ny)
all_points[point_ids] = np.log(count)
plt.imshow(all_points.reshape(nx, ny))
plt.show()
