import numpy as np
import pyvista as pv

from cyclops.visualtools.builders import CycleBuilder, ScalarFieldBuilder
from cyclops.visualtools.widgets.slider import Slider


class EPMMultiSlider(Slider):
    """Loads EPM data of multiple datasets into a single slider plot, with subplots 
    containing each dataset"""

    def __init__(self, epm_list, shape=None):
        """
        Args:
            epm_list (list): List of EPM objects.
            shape (tuple[int,int], optional): Grid shape (rows, cols). 
                If None, will try to guess a square-ish grid.
        """
        self.epm_list = epm_list
        # compute common time axis (assume same for all EPMs)
        self.time_axis = epm_list[0].phasefield.time_axis
        n = len(epm_list)
        if shape is None:
            # pick closest square
            rows = int(np.floor(np.sqrt(n)))
            cols = int(np.ceil(n / rows))
            shape = (rows, cols)
        self.shape = shape

        # create multi-subplot plotter
        self.plotter = pv.Plotter(shape=self.shape, border=False)
        self.data = []
        self.builders = []
        self.configs = {}
        self.actors = []
        self.visible_objects = []
        self.current_time_index = 0

        self.load_epm_list(epm_list)

    def load_epm_list(self, epm_list):
        """
        Load EPM data of multiple datasets into the slider.

        Args:
            epm_list (list): List of EPM objects.
        """
        for i, epm in enumerate(epm_list):
            if i == 0:
                name = "phasefield"
                self.configs[name] = {
                    "scalars": "phases",
                    "interpolate_before_map": False,
                    "clim": [-np.pi, np.pi],
                    "scalar_bar_args": {"nan_annotation": True},
                    "opacity": 1,
                    "cmap": "viridis",
                }
                self.visible_objects.append(name)

                name = "critical_cycles"
                self.configs[name] = {
                    "color": None,
                    "cmap": "bwr",
                    "scalars": "top_charge",
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

            row = i // self.shape[1]
            col = i % self.shape[1]
            self.plotter.subplot(row, col)

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

    def update_objects(self, timestep):
        """Update all subplots at a given timestep."""
        for i in range(len(self.epm_list)):
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
        self.update_objects(timestep=0)
        self.add_time_slider()
        self.plotter.show()

    def add_time_slider(self):
        """Add a single time slider controlling all subplots."""
        self.slider_widget = self.plotter.add_slider_widget(
            self.update_time,
            (self.time_axis[0], self.time_axis[-1]),
            value=self.time_axis[0],
            title="Time (ms)",
            interaction_event="always",
            pointa=(0.08, 0.92),
            pointb=(0.98, 0.92),
        )

    def update_time(self, value):
        i = np.argmax(self.time_axis >= value)
        self.current_time_index = i
        self.update_objects(timestep=i)
