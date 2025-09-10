import numpy as np
import pyvista as pv

from cyclops.visualtools.builders import CycleBuilder, ScalarFieldBuilder
from cyclops.visualtools.widgets.slider import Slider

from analysis.visualization.cmaps import dcmap


class MultiSlider(Slider):
    """Loads data of multiple datasets into a single slider plot, with subplots
    containing each dataset"""

    def __init__(self, data_list, shape):
        """
        Args:
            data_list (list): List of EPM objects.
            shape (tuple[int,int], optional): Grid shape (rows, cols).
                If None, will try to guess a square-ish grid.
        """
        self.data = []
        self.builders = []
        self.configs = {}
        self.actors = []
        self.visible_objects = []
        self.current_time_index = 0

        self.shape = shape
        self.plotter = pv.Plotter(shape=self.shape, border=False)
        self.load_data(data_list)

    def load_data(self):
        pass

    def update_objects(self, timestep):
        """Update all subplots at a given timestep."""
        for i in range(len(self.data)):
            row = i // self.shape[1]
            col = i % self.shape[1]
            self.plotter.subplot(row, col)

            for obj_type in self.visible_objects:
                data = self.data[i].get(obj_type)
                builder = self.builders[i][obj_type]
                cfg = self.configs[obj_type]

                if self.actors[i][obj_type] is None:
                    pv_obj = builder.build(data, cfg, timestep)
                    if pv_obj is not None:
                        self.actors[i][obj_type] = self.plotter.add_mesh(pv_obj, **cfg)
                        self.plotter.reset_camera()
                    else:
                        self.actors[i][obj_type] = None
                else:
                    actor = self.actors[i][obj_type]
                    pv_obj = actor.mapper.GetInput()
                    updated = builder.update(data, cfg, timestep)
                    if updated is not None:
                        self.actors[i][obj_type].mapper.SetInputData(updated)
                    else:
                        self.plotter.remove_actor(self.actors[i][obj_type])
                        self.actors[i][obj_type] = None
        self.plotter.render()

    def show(self):
        """Show the slider with all subplots."""
        self.update_objects(timestep=self.current_time_index)
        self.add_time_slider()
        self.plotter.show()

    def add_time_slider(self):
        """Add a single time slider controlling all subplots."""
        self.plotter.subplot(0, 0)
        self.slider_widget = self.plotter.add_slider_widget(
            self.update_time,
            (self.time_axis[0], self.time_axis[-1]),
            value=self.current_time_index,
            title="Time (ms)",
            interaction_event="always",
            pointa=(0.08, 0.98),
            pointb=(0.98, 0.98),
        )

    def update_time(self, value):
        i = np.argmax(self.time_axis >= value)
        self.current_time_index = i
        self.update_objects(timestep=i)


class EPMMultiSlider(MultiSlider):
    def __init__(self, epm_list):
        self.time_axis = epm_list[0].phasefield.time_axis
        n = len(epm_list)
        rows = int(np.floor(np.sqrt(n)))
        cols = int(np.ceil(n / rows))
        shape = (rows, cols)
        super().__init__(epm_list, shape)

    def load_data(self, epm_list):
        """
        Load EPM data of multiple datasets into the slider.

        Args:
            epm_list (list): List of EPM objects.
        """
        max_tc = 0
        for i, epm in enumerate(epm_list):
            if epm.critical_cycles["top_charge"].abs().max() > max_tc:
                max_tc = epm.critical_cycles["top_charge"].abs().max()
                self.current_time_index = epm.critical_cycles[
                    epm.critical_cycles["top_charge"].abs() == max_tc
                ]["time_axis"].to_numpy()[0]

            if i == 0:
                name = "phasefield"
                self.configs[name] = {
                    "scalars": "phases",
                    "interpolate_before_map": False,
                    "clim": [-np.pi, np.pi],
                    "scalar_bar_args": {"nan_annotation": True},
                    "show_scalar_bar": False,
                    "opacity": 1,
                    "cmap": "viridis",
                }
                self.visible_objects.append(name)

                name = "critical_cycles"
                self.configs[name] = {
                    "color": None,
                    "cmap": "bwr",
                    "scalars": "top_charge",
                    "show_scalar_bar": False,
                    "line_width": 7.5,
                }
                self.visible_objects.append(name)

                name = "noncritical_cycles"
                self.configs[name] = {
                    "color": "gray",
                    "cmap": None,
                    "scalars": None,
                    "line_width": 7.5,
                }
                self.visible_objects.append(name)

                name = "wavefront_cycles"
                self.configs[name] = {
                    "color": "green",
                    "cmap": None,
                    "scalars": None,
                    "line_width": 7.5,
                }
                self.visible_objects.append(name)

            coords = epm.phasefield.polydata.points

            # store actors/configs for each subplot
            sub_data = {}
            sub_builders = {}
            sub_actors = {}

            # phasefield
            name = "phasefield"
            sub_data[name] = epm.phasefield
            sub_builders[name] = ScalarFieldBuilder()
            sub_actors[name] = None

            # critical cycles
            name = "critical_cycles"
            sub_data[name] = (epm.critical_cycles, coords)
            sub_builders[name] = CycleBuilder()
            sub_actors[name] = None

            # noncritical cycles
            name = "noncritical_cycles"
            sub_data[name] = (epm.noncritical_cycles, coords)
            sub_builders[name] = CycleBuilder()
            sub_actors[name] = None

            # wavefront cycles
            name = "wavefront_cycles"
            sub_data[name] = (epm.wavefront_cycles, coords)
            sub_builders[name] = CycleBuilder()
            sub_actors[name] = None

            self.data.append(sub_data)
            self.builders.append(sub_builders)
            self.actors.append(sub_actors)
        self.configs["critical_cycles"]["clim"] = [-max_tc, max_tc]
        self.configs["critical_cycles"]["cmap"] = dcmap(
            self.configs["critical_cycles"]["cmap"], int(max_tc * 2 + 1)
        )

    def update_objects(self, timestep):
        super().update_objects(timestep)

        if timestep == self.current_time_index:
            scalar_names = [
                _
                for _ in self.visible_objects
                if self.configs[_]["scalars"] is not None
            ][::-1]
            for i, scalar_name in enumerate(scalar_names):
                dummy = pv.Sphere(theta_resolution=4, phi_resolution=4)
                dummy["dummy"] = np.linspace(0, 1, dummy.n_points)  # values 0→1
                dummy["dummy"][0] = np.nan
                if scalar_name == "critical_cycles":
                    fmt = "%.1f"
                    n_labels = int(self.configs["critical_cycles"]["clim"][1] * 2 + 1)
                    nan_annotation = False
                else:
                    fmt = "%.2f"
                    n_labels = 5
                    nan_annotation = True
                row, col = self.shape
                self.plotter.subplot(row - 1, col - 1 - i)
                actor = self.plotter.add_mesh(
                    dummy,
                    scalars="dummy",
                    cmap=self.configs[scalar_name]["cmap"],
                    clim=self.configs[scalar_name]["clim"],  # desired range
                    opacity=0.0,  # invisible
                    show_scalar_bar=False,
                    
                )
                scalar_bar_actor = self.plotter.add_scalar_bar(
                    title=["Phase Index", "Phase"][i],
                    mapper=actor.mapper,
                    vertical=False,  # bar on the right
                    position_x=0.1,  # move it outside right
                    position_y=0.1,  # vertical placement
                    width=0.8,
                    height=0.05,  # size
                    title_font_size=80,
                    label_font_size=40,
                    fmt=fmt,
                    n_labels=n_labels,
                    nan_annotation=nan_annotation
                )


class PhaseFieldMultiSlider(MultiSlider):
    def __init__(self, epm_list, scalar_name="Voltage", scalars="scalars"):
        self.scalars = scalars
        self.scalar_name = scalar_name
        self.time_axis = epm_list[0].phasefield.time_axis
        n = len(epm_list)
        rows = 1
        cols = n
        shape = (rows, cols)
        super().__init__(epm_list, shape)

    def load_data(self, epm_list):
        min_scalar, max_scalar = 0, 0
        for i, epm in enumerate(epm_list):
            phasefield = epm.phasefield
            min_scalar_, max_scalar_ = (
                np.nanmin(phasefield[self.scalars]),
                np.nanmax(phasefield[self.scalars]),
            )
            if min_scalar_ < min_scalar:
                min_scalar = min_scalar_
            if max_scalar_ > max_scalar:
                max_scalar = max_scalar_

            if i == 0:
                name = "phasefield"
                self.configs[name] = {
                    "scalars": self.scalars,
                    "interpolate_before_map": False,
                    "scalar_bar_args": {"nan_annotation": True},
                    "show_scalar_bar": False,
                    "opacity": 1,
                    "cmap": "hot",
                }
                self.visible_objects.append(name)

            # store actors/configs for each subplot
            sub_data = {}
            sub_builders = {}
            sub_actors = {}

            # phasefield
            name = "phasefield"
            sub_data[name] = phasefield
            sub_builders[name] = ScalarFieldBuilder()
            sub_actors[name] = None

            self.data.append(sub_data)
            self.builders.append(sub_builders)
            self.actors.append(sub_actors)

        self.configs["phasefield"]["clim"] = [min_scalar, max_scalar]

    def update_objects(self, timestep):
        super().update_objects(timestep)
        self.plotter.add_scalar_bar(
            title=self.scalar_name,
            position_x=0.1,  # move it outside right
            position_y=0.1,  # vertical placement
            width=0.8,
            height=0.05,  # size
            title_font_size=40,
            label_font_size=20,
            fmt=f"%.2f",
            n_labels=5,
            nan_annotation=True
        )
