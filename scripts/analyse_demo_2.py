from pathlib import Path

import cyclops.meshtools as mt
import cyclops.meshtools.filters as mf
import cyclops.visualtools as vt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvista as pv
import scipy.signal as ss
from cyclops.extended_phasemapping import ExtendedPhaseMapping
from natsort import natsorted

sim_files = "data/demo_2/"
files = natsorted(Path(sim_files).glob("*.npy"))

# set up coordinates of the mesh
nx, ny = np.load(files[0]).shape
x = np.linspace(0, 1, nx)
y = np.linspace(0, 1, ny)
xx, yy = np.meshgrid(x, y)
points = np.column_stack((xx.ravel(), yy.ravel(), np.zeros(xx.size)))
columns = pd.MultiIndex.from_product([["coords"], ["x", "y", "z"]])
vertices = pd.DataFrame(points, columns=columns)

# set up triangulated cells of the mesh
faces = pv.PolyData(points).delaunay_2d().faces.reshape(-1, 4)[:, 1:]
columns = pd.MultiIndex.from_product([["faces"], ["vertex_0", "vertex_1", "vertex_2"]])
triangles = pd.DataFrame(faces, columns=columns)

# load action potentials
jump = 4
start = 2800
list_of_action_pots = []
for file in files[start::jump]:
    list_of_action_pots.append(np.load(file).ravel())

action_pots = np.column_stack(list_of_action_pots)
mask = np.all(action_pots == action_pots[:, 0, None], axis=1)
action_pots[mask] = np.nan

# calculate phases
start= 50
stop = 500
hilbert = ss.hilbert(action_pots - np.nanmean(action_pots))
phases = -1 * np.angle(-1j * hilbert)[:, :stop]

# plot phase and action potential of one point
plt.plot(phases[500])
plt.plot(action_pots[500, :stop])
plt.show()

# create mesh
columns = pd.MultiIndex.from_product([["phases"], range(phases.shape[1])])
vertices = pd.concat((vertices, pd.DataFrame(phases, columns=columns)), axis=1)
mesh = mt.Mesh(vertices, triangles)

# run the extended phasemapping method
mesh_filters = [mf.CellPhaseDiffFilter(0.08 * np.pi)]
epm = ExtendedPhaseMapping(mesh, mesh_filters)
epm.run()

# visualise results
slider = vt.Slider(epm)
slider.boundary_actors = slider.add_boundaries(0)
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
