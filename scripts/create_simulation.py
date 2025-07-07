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


def s2_pulse(model):
    n = model.cardiac_tissue.meta["shape"][0]
    s2 = fw.StimVoltageCoord2D(
        time=50,
        volt_value=1,
        x1=3 * n // 4 + 8,
        x2=-1,
        y1=n // 4 - 8,
        y2=n // 4,
    )
    model.stim_sequence.add_stim(s2)


if __name__ == "__main__":
    model = fw.AlievPanfilov2D()
    model.dt = 0.01
    model.dr = 0.25
    model.t_max = 500

    n = 128
    tissue = fw.CardiacTissue2D([n, n])
    tissue.mesh[n // 3 - 8 : n // 3 + 8, n // 3 - 8 : n // 3 + 8] = 0
    tissue.mesh[n // 3 - 8 : n // 3 + 8, n // 3 + 16 : n // 3 + 32] = 0
    model.cardiac_tissue = tissue

    stim_sequence = fw.StimSequence()

    for i in [0, 40, 70]:
        s1 = fw.StimVoltageCoord2D(time=i, volt_value=1, x1=0, x2=-1, y1=0, y2=5)
        stim_sequence.add_stim(s1)

    s2 = fw.StimVoltageCoord2D(time=95, volt_value=1, x1=0, x2=n//3, y1=0, y2=n//3)
    stim_sequence.add_stim(s2)

    model.stim_sequence = stim_sequence

    tracker_sequence = fw.TrackerSequence()
    animation_tracker = fw.Animation2DTracker()
    animation_tracker.variable_name = "u"
    animation_tracker.dir_name = "anim_data"
    animation_tracker.step = 10
    animation_tracker.overwrite = True
    tracker_sequence.add_tracker(animation_tracker)

    action_pot_tracker = fw.ActionPotential2DTracker()
    action_pot_tracker.cell_ind = [n//3 + 10, n // 3 - 8]
    tracker_sequence.add_tracker(action_pot_tracker)

    model.tracker_sequence = tracker_sequence

    model.run()

    time = np.arange(len(action_pot_tracker.output)) * model.dt

    plt.figure()
    plt.plot(time, action_pot_tracker.output)
    plt.legend(title="Aliev-Panfilov")
    plt.xlabel("t[ms]")
    plt.ylabel("E[mV]")
    plt.show()

    animation_tracker.write(cmap="viridis", fps=60)
