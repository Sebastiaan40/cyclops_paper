import os
from pathlib import Path
import numpy as np
import numpy as np
from numba import njit, prange

from finitewave.core.tracker.tracker import Tracker
from finitewave.cpuwave2D.model import AlievPanfilov2D

class VoltageMapTracker(Tracker):
    def __init__(self):
        Tracker.__init__(self)
        self.dir_name = "output"
        self.file_name = "u"
        self.start = 0
        self.step = 1

    def initialize(self, model):
        self.model = model
        t_max = self.model.t_max
        dt = self.step
        t_range = int((t_max - self.start) / dt) + 1

        self.u_map = np.zeros((t_range, *self.model.u.shape))
        if not os.path.exists(Path(self.path).joinpath(self.dir_name)):
            Path(self.path).joinpath(self.dir_name).mkdir(parents=True)

    def _track(self):
        step = self.model.step
        t = step * self.model.dt
        i = int((t - self.start) / self.step)

        if (t % self.step == 0.0) and (t >= self.start):  # Save every self.step steps
            self.u_map[i] = self.model.__dict__["u"]

    def write(self):
        np.save(
            Path(self.path).joinpath(self.dir_name).joinpath(self.file_name), self.u_map
        )

class ModifiedAlievPanfilov2D(AlievPanfilov2D):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def run_ionic_kernel(self):
        """
        Executes the ionic kernel for the Aliev-Panfilov model.
        """
        ionic_kernel_2d(self.u_new, self.u, self.v, self.cardiac_tissue.myo_indexes, self.dt, 
                        self.a, self.k, self.eap, self.mu_1, self.mu_2)

@njit(parallel=True)
def ionic_kernel_2d(u_new, u, v, indexes, dt, a, k, eap, mu_1, mu_2):
    """
    Computes the ionic kernel for the Aliev-Panfilov 2D model.

    Parameters
    ----------
    u_new : np.ndarray
        Array to store the updated action potential values.
    u : np.ndarray
        Current action potential array.
    v : np.ndarray
        Recovery variable array.
    indexes : np.ndarray
        Array of indices where the kernel should be computed (``mesh == 1``).
    dt : float
        Time step for the simulation.
    """

    n_j = u.shape[1]

    for ind in prange(len(indexes)):
        ii = indexes[ind]
        i = int(ii / n_j)
        j = ii % n_j

        v[i, j] = calc_v(v[i, j], u[i, j], dt, a[i, j], k, eap, mu_1, mu_2)

        u_new[i, j] += dt * (- k * u[i, j] * (u[i, j] - a[i, j]) * (u[i, j] - 1.) -
                            u[i, j] * v[i, j])
        
@njit
def calc_v(v, u, dt, a, k, eap, mu_1, mu_2):
    """
    Computes the update of the recovery variable v for the Aliev–Panfilov model.

    This function implements the ordinary differential equation governing the
    evolution of the recovery variable `v`, which models the refractoriness of
    the cardiac tissue. The rate of recovery depends on both `v` and `u`, with a
    nonlinear interaction term involving a cubic expression in `u`.

    Parameters
    ----------
    v : float
        Current value of the recovery variable.
    u : float
        Current value of the transmembrane potential.
    dt : float
        Time step for integration.
    a : float
        Excitability threshold.
    k : float
        Strength of the nonlinear source term.
    eap : float
        Baseline recovery rate.
    mu_1 : float
        Recovery scaling parameter.
    mu_2 : float
        Offset parameter for recovery rate.

    Returns
    -------
    float
        Updated value of the recovery variable `v`.
    """

    v += (- dt * (eap + (mu_1 * v) / (mu_2 + u)) *
            (v + k * u * (u - a - 1.)))
    return v


