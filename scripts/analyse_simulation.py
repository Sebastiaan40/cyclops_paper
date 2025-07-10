from pathlib import Path

import cyclops.meshtools as mt
import cyclops.meshtools.filters as mf
import cyclops.parsetools as pt
import cyclops.visualtools as vt
import numpy as np
import pandas as pd
import pyvista as pv
from cyclops.extended_phasemapping import ExtendedPhaseMapping
from natsort import natsorted


def parse_data(sim_files):
    sim_path = Path(sim_files)
    action_pot = np.load(sim_path / "0.npy")
    nx, ny = action_pot.shape
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    points = np.meshgrid(x, y)
    points = np.column_stack(
        (points[0].flatten(), points[1].flatten(), np.zeros_like(points[0].flatten()))
    )

    vertices, triangles = pd.DataFrame(), pd.DataFrame()
    vertices[["x", "y", "z"]] = points

    vertices = pt.group_coords(vertices)
    files = natsorted(sim_path.glob("*.npy"))
    action_potentials = []
    for file in files:
        action_potentials.append(np.load(file).flatten())
    columns = pd.MultiIndex.from_product([["action_potentials"], range(len(files))])
    action_potentials = pd.DataFrame(
        np.column_stack(action_potentials), columns=columns
    )
    vertices = pd.concat((vertices, action_potentials), axis=1)
    mask = np.all(action_potentials == 0, axis=1)
    vertices.loc[mask, "action_potentials"] = np.nan

    polydata = pv.PolyData(points).delaunay_2d()
    faces = polydata.faces.reshape(-1, 4)[:, 1:]
    triangles[["vertex_0", "vertex_1", "vertex_2"]] = faces
    triangles = pt.group_faces(triangles)

    return mt.Mesh(vertices, triangles)


def generate_phases(mesh, time_delay):
    action_pots = mesh.vertices["action_potentials"].to_numpy()
    delayed_action_pots = np.roll(action_pots, time_delay, axis=1)
    action_pots -= np.nanmean(action_pots)
    delayed_action_pots -= np.nanmean(delayed_action_pots)
    return np.arctan2(action_pots, delayed_action_pots)


sim_files = "../data/phase_defect/"
mesh = parse_data(sim_files)
phases = generate_phases(mesh, 100)
mesh.vertices = mesh.vertices.drop("action_potentials", axis=1, level=0)
columns = pd.MultiIndex.from_product([["phases"], range(phases.shape[1])])
mesh.vertices = pd.concat(
    (mesh.vertices, pd.DataFrame(phases, columns=columns)), axis=1
)

mesh_filters = [mf.CellPhaseDiffFilter(0.2 * np.pi)]

sim_name = "phase_defect"
epm = ExtendedPhaseMapping(mesh, mesh_filters)
epm.run()

slider = vt.Slider(epm)
slider.show()
