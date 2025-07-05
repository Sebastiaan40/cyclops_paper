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
        time=810,
        volt_value=1,
        x1=3 * n // 4 + 8,
        x2=-1,
        y1=n // 4 - 8,
        y2=n // 4,
    )
    model.stim_sequence.add_stim(s2)


if __name__ == "__main__":
    model = fw.FentonKarma2D()
    model.dt = 0.01
    model.dr = 0.25
    model.t_max = 400

    # MBR
    model.tau_r = 50
    model.tau_o = 8.3
    model.tau_d = 0.172  # FIX: not in paper
    model.tau_si = 45
    model.tau_v_m = 1000
    model.tau_v_p = 3.33
    model.tau_w_m = 11
    model.tau_w_p = 667
    model.k = 10  # FIX: not in paper
    model.u_c = 0.13
    model.uc_si = 0.85

    n = 128
    tissue = fw.CardiacTissue2D([n, n])
    model.cardiac_tissue = tissue

    stim_sequence = fw.StimSequence()

    s1 = fw.StimVoltageCoord2D(time=0, volt_value=1, x1=0, x2=-1, y1=0, y2=5)
    stim_sequence.add_stim(s1)

    s1 = fw.StimVoltageCoord2D(time=300, volt_value=1, x1=0, x2=-1, y1=0, y2=5)
    stim_sequence.add_stim(s1)

    # s2 = fw.StimVoltageCoord2D(
    #     time=400, volt_value=1, x1=0, x2=3 * n // 4, y1=n // 2 - 5, y2=n // 2 + 5
    # )
    # stim_sequence.add_stim(s2)

    model.stim_sequence = stim_sequence

    tracker_sequence = fw.TrackerSequence()
    animation_tracker = fw.Animation2DTracker()
    animation_tracker.variable_name = "u"
    animation_tracker.dir_name = "anim_data"
    animation_tracker.step = 20
    animation_tracker.overwrite = True
    tracker_sequence.add_tracker(animation_tracker)
    model.tracker_sequence = tracker_sequence

    model.run()

    animation_tracker.write(cmap="viridis", fps=60)
