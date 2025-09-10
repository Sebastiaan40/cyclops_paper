import numpy as np

import cyclops.parsetools as pt
import cyclops.phasetools as ft
from cyclops.parsetools.carto import (
    load_carto_mesh,
    remove_nonactive_objects,
    parse_utils,
)

from analysis.methods.multi_epm import multi_epm
from analysis.visualization.plots import multi_slider


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
    faces = faces[np.isin(faces, np.argwhere(~np.isnan(vertices["LAT"])).all(axis=1))]
    polydata = parse_utils.parse_to_polydata(vertices, faces)
    return polydata, polydata["LAT"]


if __name__ == "__main__":
    # show simulations
    show = "phasefield"
    methods = ["pm"]
    scalar_name = "Interpolated LAT (ms)"

    # show pm and epm detections
    # show = "comparison"
    # methods = ["pm", "epm"]
    # scalar_name = None

    case = "BR17"
    maps = ["1-LA285"]
    period = 285

    parser = parse_carto_mesh
    parser_args = dict()
    phase_calculator = ft.PhaseField.from_periodic_lat
    phase_calculator_args = dict(period=period)
    th = 0.1 * np.pi
    epms = multi_epm(
        parser,
        case,
        maps,
        phase_calculator,
        methods,
        th,
        parser_args,
        phase_calculator_args,
    )
    slider = multi_slider(epms, scalar_name, show)
    slider.configs["phasefield"]["cmap"] = "rainbow"
    slider.configs["phasefield"]["clim"] = [
        np.nanmin(epms[0].phasefield["scalars"]),
        -np.nanmin(epms[0].phasefield["scalars"]),
    ]
    slider.show()
