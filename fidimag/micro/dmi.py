import fidimag.extensions.micro_clib as micro_clib
import numpy as np
from .energy import Energy
from fidimag.common.constant import mu_0
import fidimag.common.helper as helper
# import gc


class DMI(Energy):

    """

    Compute the Dzyaloshinskii-Moriya interaction in the micromagnetic
    framework. Currently, there are supported the following types of DMI:

        bulk    :: The energy density associated to this DMI type is:

                        w = D * M \cdot ( \nabla \times M)

                   which is found in B20 compunds or materials with
                   crystallographic class T.  Using a finite differences
                   discretisation, this term turns into an expression similar
                   to the atomistic DMI with DMI vector D_ij = -D r_ij, where
                   r_ij is the vector from the i-th mesh site to the j-th
                   neighbour

        interfacial :: The energy density of this DMI is, according to the
                       convention of Rohart et al [PRB 88, 184422 (2013)]

                            w = D * ( L_{xz}^{(x)} + L_{yz}^{(y)} )

                       where L are Lifshitz invariants. This DMI is found in
                       systems with their interface in contact with a heavy
                       metal (larger spin orbit coupling). A finite differences
                       discretisation turns this term into the equivalent
                       atomistic interfacial DMI term (with a different sign).
                       Since this DMI type is defined for interfacial systems,
                       the interaction is only defined with respect to
                       neighbouring sites in the xy plane and not between
                       layers in the z direction.

        D_2d        :: The energy density of this DMI is

                            w = D * ( L_{xz}^{(y)} + L_{yz}^{(x)} )

                       where L are Lifshitz invariants. This DMI is for
                       materials with symmetry class D_{2d}. Structures
                       known as anti-skyrmions are stabilised with this
                       DMI type

        custom      :: Pass n number of DMI constants as the main argument and
                       specify a dmi_vector array of length 18 * n. This array
                       has the dmi vector components for every NN in the order

                        [D1x(-x) D1y(-x) D1z(-x) D1x(+x) D1y(+x) ... D1z(+z)
                         D2x(-x) D2y(-x) ...                         D2z(+z)
                         ...
                         ]

    ARGUMENTS: ----------------------------------------------------------------

    D       :: DMI vector norm which can be specified as an int, float, (X * n)
               or spatially dependent scalar field function. The units are
               Joules / ( meter **2 ).

               int, float: D will have the same magnitude for every NN of the
               spins at every mesh node, given by this magnitude

               (n) array or list: D for every DMI constant

    OPTIONAL ARGUMENTS: -------------------------------------------------------

    dmi_type        :: 'bulk' or 'interfacial' or 'D_2d'
    name            :: Interaction name

    """

    def __init__(self, D, name='DMI', dmi_type='bulk', dmi_vector=None):
        """
        """
        self.D = D
        self.name = name
        self.jac = True
        self.dmi_type = dmi_type
        self.dmi_vector = dmi_vector

        # Number of NNs for the calculation of the corresponding DMI
        # Interfacial or D_2d are 2D so we use 4 ngbs
        types = ['bulk', 'interfacial', 'D_n', 'C_n', 'D_2d', 'custom']
        if self.dmi_type not in types:
            raise Exception(
                "Unsupported DMI type: {}, " +
                "available options:\n  {}".format(self.dmi_type, *types)
                )


        # if self.dmi_type == 'D_n' or self.dmi_type == 'C_n':
        #     if not self.D2:
        #         raise Exception("For C_n and D_n symmetry, you must also pass a D2 value"
        #                          " as this material class has multiple DMI constants")

    def setup(self, mesh, spin, Ms, Ms_inv):
        super(DMI, self).setup(mesh, spin, Ms, Ms_inv)

        if self.dmi_type == 'bulk':
            self.dmi_vector = np.array([-1., 0, 0,
                                        1., 0, 0,
                                        0, -1., 0,
                                        0, 1., 0,
                                        0, 0, -1.,
                                        0, 0, 1.
                                        ])

        elif self.dmi_type == 'interfacial':
            self.dmi_vector = np.array([0, -1., 0,  # -x
                                        0, 1., 0,   # +x
                                        1., 0, 0,   # -y
                                        -1., 0, 0,  # +y
                                        0, 0, 0,    # -z
                                        0, 0, 0     # +z
                                        ])

        elif self.dmi_type == 'D_2d':
            self.dmi_vector = np.array([1., 0, 0,   # -x
                                        -1., 0, 0,  # +x
                                        0, -1., 0,  # -y
                                        0, 1., 0,   # +y
                                        0, 0, 0,    # -z
                                        0, 0, 0     # +z
                                        ])

        elif self.dmi_type == 'D_n':
            self.dmi_vector = np.array([1.0, 0, 0,  # D1 components
                                        -1, 0, 0,
                                        0, -1, 0,
                                        0, 1, 0,
                                        0, 0, 0,
                                        0, 0, 0,
                                        0, 0, 0,    # D2 components
                                        0, 0, 0,
                                        0, 0, 0,
                                        0, 0, 0,
                                        0, 0, 1,
                                        0, 0, -1,
                                        ])

        elif self.dmi_type == 'C_n':
            self.dmi_vector = np.array([0, -1., 0,  # -x
                                        0, 1., 0,   # +x
                                        1., 0, 0,   # -y
                                        -1., 0, 0,  # +y
                                        0, 0, 0,    # -z
                                        0, 0, 0,    # +z
                                        1, 0, 0,    # D2 components
                                        -1, 0, 0,
                                        0, -1, 0,
                                        0, 1, 0,
                                        0, 0, 0,
                                        0, 0, 0,
                                        ])
        elif self.dmi_type == 'custom':
            self.dmi_vector = np.array(self.dmi_vector)
            # Example:
            # self.DMI_vector = [ 0, 0, D1,  # DMI 1
            #                     0, 0, -D1,
            #                     0, 0, 0,
            #                     0, 0, 0,
            #                     0, 0, 0,
            #                     0, 0, 0,
            #                     0, 0, 0,   # DMI 2
            #                     0, 0, 0,
            #                     0, D2, 0,
            #                     0, -D2, 0,
            #                     0, 0, 0,
            #                     0, 0, 0,
            #                   ]
            n_Ds = len(self.dmi_vector) // 18

            if len(self.dmi_vector) % 18 != 0:
                raise Exception('The DMI vector length must be a mult of 18: '
                                ' N of DMIs times 3 * number of ngbs = 18')

            if n_Ds > 1:
                self.Ds = helper.init_vector(self.D, self.mesh, dim=n_Ds)
            else:
                self.Ds = helper.init_scalar(self.D, self.mesh)

            self.n_dmis = n_Ds

        if self.dmi_type == 'C_n' or self.dmi_type == 'D_n':
            self.Ds = helper.init_vector(self.D, self.mesh, dim=2)
            self.n_dmis = 2
        else:
            self.Ds = helper.init_scalar(self.D, self.mesh)
            self.n_dmis = 1

    def compute_field(self, t=0, spin=None):
        if spin is not None:
            m = spin
        else:
            m = self.spin

        micro_clib.compute_dmi_field(m,
                                     self.field,
                                     self.energy,
                                     self.Ms_inv,
                                     self.Ds,
                                     self.n_dmis,
                                     self.dmi_vector,
                                     self.dx,
                                     self.dy,
                                     self.dz,
                                     self.n,
                                     self.neighbours
                                     )

        return self.field
