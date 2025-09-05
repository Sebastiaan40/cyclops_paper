import numpy as np

from draw_util import draw_circle


def square_setup(test, model, H_eps, SC_eps, ST_eps):
    mesh = model.cardiac_tissue.mesh
    ni, nj = mesh.shape
    scars_matrix = np.zeros((ni, nj), dtype=int)
    temp_scars_matrix = np.zeros((ni, nj), dtype=int)
    ablation_matrix = np.zeros((ni, nj), dtype=int)
    stimuli_matrix = np.zeros((ni, nj))
    extra_stimuli_matrix = np.zeros((ni, nj))
    a_matrix = model.a
    cond_matrix = model.cardiac_tissue.conductivity
    a = 0.0
    cond = 0

    # Permanent scar, lowered APD, lower conduction zones
    if test in [2, 5, 6]:
        # draw scar circle
        scars_matrix = draw_circle(scars_matrix, (ni // 2, nj // 2), SC_eps, tag=1)
    if test == 3:
        # draw hole
        model.cardiac_tissue.mesh = draw_circle(
            model.cardiac_tissue.mesh, (ni // 2, nj // 2), SC_eps, tag=0
        )
    if test == 4:
        # draw hybrid phase barrier
        scars_matrix = draw_circle(scars_matrix, (ni // 2, 9 * nj // 16), SC_eps, tag=1)
        model.cardiac_tissue.mesh = draw_circle(
            model.cardiac_tissue.mesh, (ni // 2, 7*nj // 16), SC_eps, tag=0
        )
    if test in [5, 6]:
        scars_matrix = draw_circle(
            scars_matrix, (ni // 2, nj // 2), 1.7 * SC_eps, tag=1
        )
    if test in [7]:
        scars_matrix = draw_circle(
            scars_matrix, (3 * ni // 10, nj // 2), 1.7 * SC_eps, tag=1
        )
        scars_matrix = draw_circle(scars_matrix, (7 * ni // 10, nj // 2), SC_eps, tag=1)

    model.a = a_matrix
    model.cardiac_tissue.conductivity = cond_matrix

    # Temporal scars and stimuli
    if test in [1, 2, 3, 4]:
        # initiate complete rotation
        temp_scars_matrix[: ni // 2, nj // 2] = 1
        stimuli_matrix = draw_circle(
            stimuli_matrix, (ni // 4, nj // 2 - ST_eps - 1), ST_eps
        )
    if test == 5:
        # initiate simple parallel activity
        extra_stimuli_matrix = draw_circle(
            extra_stimuli_matrix, (ni // 4, nj // 2), ST_eps
        )
    if test == 6:
        # initiate complex parallel activity
        extra_stimuli_matrix = draw_circle(
            extra_stimuli_matrix, (ni // 4, nj // 2), ST_eps
        )
        extra_stimuli_matrix = draw_circle(
            extra_stimuli_matrix, (3 * ni // 4, nj // 2), ST_eps
        )
    if test == 7:
        # initiate near-complete rotation
        temp_scars_matrix[4 * ni // 10 : 7 * ni // 10, nj // 2] = 1
        stimuli_matrix = draw_circle(
            stimuli_matrix, (ni // 2, nj // 2 - ST_eps - 1), ST_eps
        )

    # Ablation matrix

    return (
        scars_matrix,
        temp_scars_matrix,
        stimuli_matrix,
        extra_stimuli_matrix,
        ablation_matrix,
    )
