from analysis.visualization.custom_cyclops_classes import EPMMultiSlider, PhaseFieldMultiSlider

def multi_slider(epms, scalar_name, show="comparison"):
    if show == "comparison":
        slider = EPMMultiSlider(epms)
        # slider.visible_objects = ["phasefield"]
        slider.visible_objects = ["phasefield", "critical_cycles"]
        # slider.visible_objects = ["phasefield", "critical_cycles", "noncritical_cycles"]
    elif show == "phasefield":
        slider = PhaseFieldMultiSlider(epms, scalar_name)
        
    slider.plotter.link_views()
    slider.plotter.camera_position = "xy"
    slider.plotter.camera.zoom(1.5)
    return slider


