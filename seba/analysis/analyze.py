import os
import pickle
import sys
from pathlib import Path

# Make sure that the project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import cyclops.cycletools as ct
import cyclops.phasetools as ft
from cyclops.extended_phasemapping import ExtendedPhaseMapping
from custom_cyclops_classes import EPMMultiSlider


def analyze(
    parser,
    case,
    maps,
    phase_calculator,
    methods,
    th,
    parser_args={},
    phase_calculator_args={},
):
    epms = []
    for map in maps:
        for method in methods:
            filepath = (
                Path(__file__).parent.parent / f"pickle/{case}/{method}/{map}.pkl"
            )
            print(filepath)
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    epm = pickle.load(f)
            else:
                polydata, scalars = parser(case, map, **parser_args)
                phasefield = phase_calculator(polydata, scalars, **phase_calculator_args)
                
                if method == "pm":
                    phasefield_filters = []
                    cycle_extractors = [ct.extract_face_cycles]
                elif method == "epm":
                    phasefield_filters = [
                        ft.NaNFilter(),
                        ft.PhaseDiffFilter(th),
                    ]
                    cycle_extractors = [
                        ct.extract_face_cycles,
                        ct.extract_boundary_cycles,
                    ]

                epm = ExtendedPhaseMapping(
                    phasefield, phasefield_filters, cycle_extractors
                )
                epm.run()

                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "wb") as f:
                    pickle.dump(epm, f)

            epms.append(epm)

    slider = EPMMultiSlider(epms)

    # slider.visible_objects = ["phasefield"]
    slider.visible_objects = ["phasefield", "critical_cycles"]
    # slider.visible_objects = ["phasefield", "critical_cycles", "noncritical_cycles"]
    slider.plotter.link_views()
    slider.plotter.camera_position = "xy"
    slider.plotter.camera.zoom(1.5)
    slider.show()
