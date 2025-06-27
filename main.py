import finitewave as fw
import matplotlib.pyplot as plt


class UpdateMesh(fw.Command):
    """
    Update the mesh of the cardiac tissue during the simulation.
    """

    def __init__(self, time, updated_mesh):
        """
        Initialize the command with the time and the updated mesh.

        Args:
            time (int): The time at which the mesh is updated.
            updated_mesh (numpy.ndarray): The updated mesh.
        """
        super().__init__(time)
        self.updated_mesh = updated_mesh

    def execute(self, model):
        model.cardiac_tissue.mesh = self.updated_mesh
        model.compute_weights()


def main():
    # set up the tissue:
    n = 256
    tissue = fw.CardiacTissue2D([n, n])
    tissue.mesh[n // 2, : n // 2] = 2

    mesh_without_block = tissue.mesh.copy()
    mesh_without_block[n // 2, : n // 2] = 1

    # set up stimulation parameters:
    stim_sequence = fw.StimSequence()
    stim_sequence.add_stim(
        fw.StimVoltageCoord2D(time=0, volt_value=1, x1=0, x2=n // 2, y1=0, y2=5)
    )
    # stim_sequence.add_stim(fw.StimVoltageCoord2D(time=50, volt_value=1,
    #                                              x1=n//2, x2=n, y1=0, y2=n))

    command_sequence = fw.CommandSequence()
    command_sequence.add_command(UpdateMesh(45, mesh_without_block))

    # create model object:
    model = fw.AlievPanfilov2D()
    # set up numerical parameters:
    model.dt = 0.01
    model.dr = 0.3
    model.t_max = 10

    # add the tissue and the stim parameters to the model object:
    model.cardiac_tissue = tissue
    model.stim_sequence = stim_sequence
    model.command_sequence = command_sequence

    model.run()
    u_10 = model.u.copy()

    model.t_max = 46
    model.run(initialize=False)
    u_46 = model.u.copy()

    model.t_max = 150
    model.run(initialize=False)
    u_150 = model.u.copy()

    fig, axs = plt.subplots(ncols=3)
    axs[0].imshow(u_10, cmap="hot")
    axs[1].imshow(u_46, cmap="hot")
    axs[2].imshow(u_150, cmap="hot")
    plt.show()


if __name__ == "__main__":
    main()
