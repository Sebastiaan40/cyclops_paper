import numpy as np

import cyclops.parsetools as pt
import cyclops.phasetools as ft

from analyze import analyze

if __name__ == "__main__":
    # case = "rat/rec_psgui"
    # maps = ["data_psgui.mat"]

    case = "rat/R80/original"
    maps = [
        "masked_data_RG_80nM.mat",
        "masked_data_RG_80nM_280618.mat",
        "masked_organised_4s.mat",
    ][:1]

    # case = "rat/R80/scripts/"
    # maps = [
    #     "data_RG_80nM_organized_4s.mat",
    #     "data_RG_80nM_organized_4s01.mat",
    #     "data_RG_80nM_organized_4s02.mat",
    #     "data_RG_80nM_organized_4s03.mat",
    #     "data_RG_80nM_organized_4s04.mat",
    #     "data_RG_80nM_4s.mat",
    #     "data_RG_80nM_4s01.mat",
    #     "data_RG_80nM_4s02.mat",
    #     "data_RG_80nM_4s03.mat",
    #     "data_RG_80nM_4s04.mat",
    #     "data_RG_80nM_10s.mat",
    # ]

    # case = "rat/R80/Rotigaptide 2 280618/Processed_data/"
    # maps = [
    #     "ddata_RG_vf_280618.mat",
    #     "data_RG_10nM_280618.mat",
    #     "data_RG_50nM_280618.mat",
    #     "data_RG_30nM_280618.mat",
    #     "data_RG_80nM_280618.mat",
    # ]

    # case = "rat/R80/RG4/Processed_data/"
    # maps = [
    #     "data_RG_0nM.mat",
    #     "data_RG_10nM.mat",
    #     "data_RG_30nM.mat",
    #     "data_RG_50nM.mat",
    #     "data_RG_80nM.mat",
    # ]

    # case = "rat/R80/RG 220818/"
    # maps = [
    #     "10s.mat ",
    #     "10s2.mat",
    #     "10s3.mat",
    #     "10s4.mat",
    #     "10s5.mat",
    #     "10s6.mat ",
    #     "10s7.mat",
    #     "organised 4s.mat",
    #     "organised 4s01.mat",
    #     "organised 4s02.mat",
    #     "organised 4s03.mat",
    #     "organised 4s04.mat",
    # ]

    # case = "rabbit/3.2sec"
    # maps = ["ratio_data33_2023_02_22_smoothed_mask.mat"]

    parser = pt.parse_vf_optical
    phase_calculator = ft.PhaseField.from_signals
    parser_args = dict()
    methods = ["pm", "epm"]
    th = 0.5 * np.pi
    analyze(parser, case, maps, phase_calculator, methods, th, parser_args)
