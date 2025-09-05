"""Performs finite wave simulation using Aliev Panfilov cell model for a 2D square."""

from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np
import finitewave as fw

from setup import square_setup
from custom_fw_classes import VoltageMapTracker, ModifiedAlievPanfilov2D

root = Path(__file__).parent.parent.parent
path = root.joinpath(f"dgm_database/fw_sim/Seba")

# root = Path(__file__).parent
# path = root.joinpath("output")

# Simulation configurations
# test = 1  # complete rotation around a functional block
# test = 2  # complete rotation around scar
# test = 3  # complete rotation around hole
# test = 4  # compelte rotation around a hybrid phase barrier
# test = 5  # simple parallel activation around a scar
# test = 6  # complex parallel activation around a scar
# test = 7  # near-complete rotation around a scar

test = 4

# for test in range(1, 8):
# for test in [1, 6]:
for test in [test]:
    # Parameters
    # time
    dt = 0.01  # t[ms] = 12.9*t
    dt_output = 0.5
    t_max = 400
    t_start = 30  # end prepacing time
    t_stable = 28  # block removal timing
    t_extra_stim = [i*2*t_stable for i in range(1, 10)]
    t_ablation = 189 - 28  # ablation timing

    # space
    dr = 0.5  # arbitrary unit
    ni, nj = 39, 39
    scale = 5
    SC_eps = 4 # scar radius
    ST_eps = 4 # stimulus radius
    H_eps = 2 * SC_eps  # hole_radius

    # conduction
    cond = 0.2 # cond[dr_unit/ms] = cond / 12.9 = 0.016

    # Rescale dimensions
    ni *= scale
    nj *= scale
    cond *= scale
    SC_eps *= scale
    ST_eps *= scale
    H_eps *= scale
    ni = int(ni)
    nj = int(nj)

    # Create model object
    aliev_panfilov = ModifiedAlievPanfilov2D()
    aliev_panfilov.a = np.ones([ni, nj])*0.15
    aliev_panfilov.dt = dt
    aliev_panfilov.dr = dr
    aliev_panfilov.t_max = t_max + t_start

    # Tissue
    tissue = fw.CardiacTissue2D([ni, nj])
    tissue.mesh = np.ones(tissue.mesh.shape)
    tissue.add_boundaries()
    tissue.conductivity = np.ones(tissue.mesh.shape) * cond
    aliev_panfilov.cardiac_tissue = tissue

    # Setup scars, stimuli and ablations
    (
        scars_matrix,
        temp_scars_matrix,
        stimuli_matrix,
        extra_stimuli_matrix,
        ablation_matrix,
    ) = square_setup(test, aliev_panfilov, H_eps, SC_eps, ST_eps)

    # Show simulation setup
    fig, ax = plt.subplots()
    matrix = tissue.mesh
    for i, m in enumerate(
        [
            scars_matrix,
            temp_scars_matrix,
            stimuli_matrix,
            extra_stimuli_matrix,
            ablation_matrix,
            aliev_panfilov.a,
            aliev_panfilov.cardiac_tissue.conductivity
        ]
    ):
        matrix = matrix + (i + 2) * m
    ax.imshow(matrix, cmap="rainbow")
    # plt.show()

    # Set up stimulation parameters
    stim_sequence = fw.StimSequence()
    stim_sequence.add_stim(
        fw.StimVoltageMatrix2D(0, 1, np.ones_like(tissue.mesh))
    )  # prepacing
    stim_sequence.add_stim(fw.StimVoltageMatrix2D(t_start, 1, stimuli_matrix))
    for t in t_extra_stim:
        stim_sequence.add_stim(
            fw.StimVoltageMatrix2D(t_start + t_stable + t, 1, extra_stimuli_matrix)
        )

    # Set up animation tracker
    umap_tracker = VoltageMapTracker()
    umap_tracker.path = path
    umap_tracker.step = dt_output
    umap_tracker.start = t_start
    umap_tracker.dir_name = "square"
    umap_tracker.file_name = f"scalars{test}".replace(".", "_")
    tracker_sequence = fw.TrackerSequence()
    tracker_sequence.add_tracker(umap_tracker)


    # Adjust scar command
    class AdjustScar(fw.Command):
        def __init__(self, time, temp_scar, tag):
            super().__init__(time)
            self.temp_scar = temp_scar
            self.tag = tag

        def execute(self, model):
            model.cardiac_tissue.mesh[np.nonzero(scars_matrix)] = 2
            model.cardiac_tissue.mesh[np.nonzero(self.temp_scar)] = self.tag

            tissue.add_boundaries()
            model.compute_weights()

    # Create command sequence
    command_sequence = fw.CommandSequence()
    command_sequence.add_command(
        AdjustScar(t_start, temp_scars_matrix, 2)
    )  # add temp block
    command_sequence.add_command(
        AdjustScar(t_start + t_stable, temp_scars_matrix, 1)
    )  # remove temp block
    command_sequence.add_command(
        AdjustScar(t_start + t_stable + t_ablation, ablation_matrix, 2)
    )  # ablate

    # Add the sequence to the model
    aliev_panfilov.cardiac_tissue = tissue
    aliev_panfilov.stim_sequence = stim_sequence
    aliev_panfilov.tracker_sequence = tracker_sequence
    aliev_panfilov.command_sequence = command_sequence
    aliev_panfilov.initialize()
    aliev_panfilov.run(initialize=False)

    # Save data
    umap_tracker.write()
    np.save(path.joinpath(f"square/mesh{test}".replace(".", "_")), tissue.mesh)
