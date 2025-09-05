import numpy as np

import cyclops.parsetools as pt
import cyclops.phasetools as ft
from cyclops.parsetools.carto import load_carto_mesh, remove_nonactive_objects, parse_utils

from analyze import analyze

def parse_carto_mesh(case: str, filename: str):
    """
    Parse CARTO mesh from a given case and filename.

    Args:
        case (str): The case identifier.
        filename (str): The mesh filename.

    Returns:
        PolyData: Parsed mesh as a PyVista PolyData object.
    """
    vertices, faces = load_carto_mesh(case, filename)
    vertices, faces = remove_nonactive_objects(vertices, faces)
    vertices = parse_utils.phase_interpolation(vertices)
    polydata = parse_utils.parse_to_polydata(vertices, faces)
    return polydata, polydata["LAT"]

if __name__ == "__main__":
    case = "BR17"
    maps = ["1-LA285"]
    period = 285

    parser = parse_carto_mesh
    parser_args = dict()
    phase_calculator = ft.PhaseField.from_periodic_lat
    phase_calculator_args = dict(period=period)
    methods = ["pm", "epm"]
    th = 0.15 * np.pi
    analyze(
        parser,
        case,
        maps,
        phase_calculator,
        methods,
        th,
        parser_args,
        phase_calculator_args,
    )
