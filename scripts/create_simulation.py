import finitewave as fw
import numpy as np

if __name__ == "__main__":
    # set up the tissue:
    n = 128
    tissue = fw.CardiacTissue2D([n, n])

    # non-conductive regions
    # tissue.mesh[n // 4 - 16 : n // 4 + 16, n // 4 - 16 : n // 4 + 16] = 0
    tissue.mesh[3 * n // 4 - 8 : 3 * n // 4 + 8, n // 4 - 8 : n // 4 + 8] = 0

    tissue.conductivity = np.ones_like(tissue.mesh)
    tissue.conductivity[3 * n // 4 - 8 : 3 * n // 4 - 6, n // 4 + 8 : n // 2] = 0.1

    # set up stimulation parameters:
    stim_sequence = fw.StimSequence()

    s1 = fw.StimVoltageCoord2D(time=0, volt_value=1, x1=0, x2=-1, y1=0, y2=5)
    s2 = fw.StimVoltageCoord2D(
        time=48,
        volt_value=1,
        x1=3 * n // 4 + 8,
        x2=-1,
        y1=n // 4,
        y2=n // 4 + 8,
    )
    stim_sequence.add_stim(s1)
    stim_sequence.add_stim(s2)

    # set up tracker parameters:
    tracker_sequence = fw.TrackerSequence()
    animation_tracker = fw.Animation2DTracker()
    animation_tracker.variable_name = "u"  # Specify the variable to track
    animation_tracker.dir_name = "anim_data"
    animation_tracker.step = 10
    animation_tracker.overwrite = True  # Remove existing files in dir_name
    tracker_sequence.add_tracker(animation_tracker)

    # create model object:
    model = fw.AlievPanfilov2D()
    # set up numerical parameters:
    model.eap = 0.002
    model.dt = 0.01
    model.dr = 0.3
    model.t_max = 150

    # add the tissue and the stim parameters to the model object:
    model.cardiac_tissue = tissue
    model.stim_sequence = stim_sequence
    model.tracker_sequence = tracker_sequence

    model.run()

    animation_tracker.write(cmap="viridis", fps=60)
