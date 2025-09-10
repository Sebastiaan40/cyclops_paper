import numpy as np
import pyvista as pv

# ------ Example data ------
mesh = pv.Sphere()
scalars = np.linspace(0, 1, mesh.n_points)
scalars[::10] = np.nan
mesh["data"] = scalars

# ------ Create plotter and add mesh (no auto scalar bar) ------
pl = pv.Plotter(window_size=(900, 600))
pl.add_mesh(
    mesh,
    scalars="data",
    cmap="viridis",
    nan_color="lightgray",
    nan_opacity=1.0,
    show_scalar_bar=False,  # we'll add it explicitly so we get the actor handle
)

# ------ Add scalar bar explicitly and request nan annotation ------
# add_scalar_bar returns the vtk scalar bar actor (or a wrapped actor)
sbar = pl.add_scalar_bar(
    title="Data values",
    n_labels=5,
    vertical=False,
    nan_annotation=True,
    width=0.6,   # adjust visual width/height as needed
    height=0.08,
)

# Force a render so VTK creates the 2D actors (important!)
pl.render()

# ------ Helper to attempt to set labels ABOVE the horizontal bar ------
def try_set_labels_above(actor):
    # Try a few possible VTK methods (wrapper variations exist across versions)
    tried = []
    for name in (
        "SetTextPositionToSucceedScalarBar",
        "SetTextPosition",  # usually 0 or 1
    ):
        if hasattr(actor, name):
            tried.append(name)
            meth = getattr(actor, name)
            try:
                if name == "SetTextPosition":
                    # 1 => succeed (i.e. labels on the side that "succeeds" the bar)
                    meth(1)
                else:
                    meth()
                return True, tried
            except Exception as e:
                print(f"Method {name} exists but call failed: {e}")
    return False, tried

# ------ 1) Try direct handle returned by add_scalar_bar ------
success, tried = try_set_labels_above(sbar)
success = False
print("Tried on sbar:", tried, "-> success:", success)

# ------ 2) If not successful, search renderer actors2D for a scalar bar actor ------
if not success:
    ren = pl.renderer
    actors2d = ren.GetActors2D()
    actors2d.InitTraversal()
    a = actors2d.GetNextActor2D()
    found = False
    while a:
        cls = a.GetClassName()
        # debug print of class names (uncomment if you'd like more info)
        # print("actor class:", cls)
        if a.IsA("vtkScalarBarActor") or "ScalarBar" in cls:
            print("Found scalar bar actor in renderer:", cls)
            found = True
            success2, tried2 = try_set_labels_above(a)
            print("Tried on actor from renderer:", tried2, "-> success:", success2)
            if success2:
                success = True
                break
        a = actors2d.GetNextActor2D()

success = False
# ------ 3) Final fallback: if we still couldn't flip labels, add manual text above bar ------
if not success:
    print("Could not find or change the vtkScalarBarActor method on this build. Falling back to manual text placement.")
    # compute scalar bar position/size in normalized viewport coords if possible
    try:
        pos = sbar.GetPosition()       # (x, y)
        pos2 = sbar.GetPosition2()     # (width, height)
        # center above the bar
        text_x = pos[0] + pos2[0] / 2.0
        text_y = pos[1] + pos2[1] + 0.02  # little offset above bar; tweak as needed
        print("Scalar bar pos, pos2:", pos, pos2)
        pl.add_text("NaN", position=(text_x, text_y), font_size=12, color="lightgray")
    except Exception as e:
        print("Fallback manual placement failed:", e)
        # fallback to a simple screen-positioned text near upper center
        pl.add_text("NaN", position=(0.5, 0.92), font_size=12, color="lightgray", viewport=True)

# ------ Show the final plot ------
pl.show()
