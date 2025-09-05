import os
import pickle
import sys
from pathlib import Path

# Make sure that the project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import numpy as np
import pandas as pd
import cyclops.cycletools as ct
import cyclops.phasetools as ft
import cyclops.visualtools as vt
from cyclops.extended_phasemapping import ExtendedPhaseMapping
from cyclops.parsetools import parse_utils

from analyze import analyze


def parse_finitewave_mesh(case, filename):
    vertices, quads, scalars = load_finitewave_mesh(case, filename)
    return parse_utils.parse_to_polydata(vertices, quads), scalars


def load_finitewave_mesh(case, filename):
    grid_file = parse_utils.get_case_file(case, filename, suffix=".npy")
    grid = np.load(grid_file)[1:-1, 1:-1]
    scalars_file = parse_utils.get_case_file(
        case, filename.replace("mesh", "scalars"), suffix=".npy"
    )
    scalars = np.load(scalars_file)[:, 1:-1, 1:-1]
    scalars[:, grid != 1] = np.nan

    nx, ny = grid.shape
    coords = np.argwhere(grid != -1)
    idx = np.arange(nx * ny).reshape((nx, ny))
    quads = np.stack(
        [
            idx[:-1, :-1].ravel(),  # corner 0
            idx[1:, :-1].ravel(),  # corner 1
            idx[1:, 1:].ravel(),  # corner 2
            idx[:-1, 1:].ravel(),  # corner 3
        ],
        axis=1,
    )  # shape (M, 4)

    hole_indices = idx[grid == 0].flatten()
    quads = quads[~np.isin(quads, hole_indices).any(axis=1)]

    coords = np.stack([coords[:, 0], coords[:, 1], np.zeros(coords.shape[0])], axis=1)
    vertices = pd.DataFrame(coords, columns=["x", "y", "z"])
    quads = pd.DataFrame(quads, columns=[f"vertex_{i}" for i in range(4)])
    scalars = scalars.reshape(scalars.shape[0], -1).T

    return vertices, quads, scalars


if __name__ == "__main__":
    parser = parse_finitewave_mesh
    case = "square"
    maps = [f"mesh{i}" for i in range(1, 5)]
    # maps = [f"mesh{i}" for i in [5, 6, 2, 7]]
    methods = ["pm", "epm"]
    th = 0.04 * np.pi
    analyze(parser, case, maps, methods, th)


    