import finitewave as fw
import matplotlib.pyplot as plt
import numpy as np


def add_cardiac_tissue(model, n):
    tissue = fw.CardiacTissue2D([n, n])

    tissue.mesh[3 * n // 4 - 8 : 3 * n // 4 + 8, n // 4 - 8 : n // 4 + 32] = 0

    tissue.conductivity = np.ones([n, n], dtype=float)
    tissue.conductivity[3 * n // 4 - 32 : 3 * n // 4 + 8, n // 4 - 8 : n // 4 + 32] = (
        0.1
    )

    plt.imshow(tissue.conductivity * tissue.mesh)
    plt.show()

    model.cardiac_tissue = tissue


# NOTE: Is this really necessary?
def prepacing(model):
    stim_sequence = fw.StimSequence()

    for i in [1, 170, 330, 490, 650]:
        s1 = fw.StimVoltageCoord2D(time=i, volt_value=1, x1=0, x2=-1, y1=0, y2=5)
        stim_sequence.add_stim(s1)

    model.stim_sequence = stim_sequence

    tracker_sequence = fw.TrackerSequence()
    action_pot_tracker = fw.ActionPotential2DTracker()
    action_pot_tracker.step = 1
    n = model.cardiac_tissue.meta["shape"][0]
    action_pot_tracker.cell_ind = [n // 2, n // 2]
    tracker_sequence.add_tracker(action_pot_tracker)
    model.tracker_sequence = tracker_sequence

    model.t_max = 660
    model.run()

    time = np.arange(len(action_pot_tracker.output)) * model.dt

    plt.figure()
    plt.plot(time, action_pot_tracker.output)
    plt.legend(title="Fenton-Karma")
    plt.show()


def s2_pulse(model):
    n = model.cardiac_tissue.meta["shape"][0]
    s2 = fw.StimVoltageCoord2D(
        time=810,
        volt_value=1,
        x1=3 * n // 4 + 8,
        x2=-1,
        y1=n // 4 - 8,
        y2=n // 4,
    )
    model.stim_sequence.add_stim(s2)

    animation_tracker = fw.Animation2DTracker()
    animation_tracker.variable_name = "u"
    animation_tracker.dir_name = "anim_data"
    animation_tracker.step = 20
    animation_tracker.overwrite = True

    model.tracker_sequence.add_tracker(animation_tracker)
    model.t_max = 1000
    model.run(initialize=False)

    animation_tracker.write(cmap="viridis", fps=60)


if __name__ == "__main__":
    model = fw.FentonKarma2D()
    model.dt = 0.01
    model.dr = 0.25

    add_cardiac_tissue(model, n=128)
    prepacing(model)
    s2_pulse(model)
