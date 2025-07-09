import finitewave as fw
import matplotlib.pyplot as plt
import numpy as np


def simulate_action_pot():
    n = 100
    m = 5
    # create mesh
    tissue = fw.CardiacTissue2D((n, m))

    # set up stimulation parameters
    stim_sequence = fw.StimSequence()
    stim_sequence.add_stim(fw.StimVoltageCoord2D(0, 1, 0, 5, 0, m))

    # create model object and set up parameters
    courtemanche = fw.Courtemanche2D()
    courtemanche.dt = 0.01
    courtemanche.dr = 0.25
    courtemanche.t_max = 500

    # Here, we increase g_Kur by a factor of 3 to better match physiological AP shape
    # with a visible plateau and realistic repolarization.
    courtemanche.gkur_coeff *= 3

    # add the tissue and the stim parameters to the model object
    courtemanche.cardiac_tissue = tissue
    courtemanche.stim_sequence = stim_sequence

    tracker_sequence = fw.TrackerSequence()
    action_pot_tracker = fw.ActionPotential2DTracker()
    # to specify the mesh node under the measuring - use the cell_ind field:
    # eather list or list of lists can be used
    action_pot_tracker.cell_ind = [[50, 3]]
    action_pot_tracker.step = 1
    tracker_sequence.add_tracker(action_pot_tracker)
    courtemanche.tracker_sequence = tracker_sequence

    # run the model:
    courtemanche.run()

    # plot the action potential
    time = np.arange(len(action_pot_tracker.output)) * courtemanche.dt

    return time, action_pot_tracker.output


def curve_action_pot(action_pot):
    rho = 1 + (action_pot - action_pot.min()) / np.ptp(action_pot)
    phi = np.linspace(0, 2 * np.pi, len(action_pot))
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return x, y


if __name__ == "__main__":
    time, action_pot = simulate_action_pot()

    plt.subplot(2, 1, 1)
    plt.plot(time, action_pot)
    plt.legend(title="Courtemanche")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (mV)")
    plt.title("Action Potential")
    plt.grid()

    x, y = curve_action_pot(action_pot)

    plt.subplot(2, 1, 2)
    plt.plot(x, y)
    plt.legend(title="Courtemanche")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (mV)")
    plt.title("Action Potential")
    plt.grid()

    plt.show()
