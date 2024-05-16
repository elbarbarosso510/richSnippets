import numpy as np
import scipy as sp
import lumapi
import os
import matplotlib.pyplot as pp

from lumopt.utilities.wavelengths import Wavelengths
from lumopt.geometries.polygon import FunctionDefinedPolygon
from lumopt.utilities.materials import Material
from lumopt.figures_of_merit.modematch import ModeMatch
from lumopt.optimizers.generic_optimizers import ScipyOptimizers
from lumopt.optimization import Optimization


# Load Base simulation functions
from Mux_varFDTD_geometry import sim_init_in
from params import dev_params

init_sim = sim_init_in

# Save the project directory for the final figure export
project_directory = os.getcwd()
wavelengths = Wavelengths(start=1500e-9, stop=1600e-9, points=5)
num_points = dev_params['num_points']

in_wg_width = dev_params['wg01']
out_wg_width = dev_params['wg02']
spacing = dev_params['spacing']

y1 = in_wg_width /2     # Start of the side boundary
y2 =  (4*out_wg_width+3*spacing)/2 # End of the side boundary

initial_points_x = np.linspace(-dev_params['length']/2, dev_params['length']/2, num_points)
initial_points_y = np.linspace(y1, y2, num_points)

dx = dev_params['length'] / (num_points-1)

def plot_spliter(params):
    n_interpolation_points = 100
    pp.plot(initial_points_x, params)
    pp.plot(initial_points_x, -params)
    polygon_points = opt_device(params)

    pp.plot(polygon_points[:, 0], polygon_points[:, 1])
    pp.show()

def opt_device(params):
    n_interpolation_points = 100

    points_x1 = np.concatenate(([initial_points_x.min() - dx], initial_points_x,
                                [(initial_points_x.max()) + dx]))
    polygon_points_x = np.linspace(min(points_x1), max(points_x1), n_interpolation_points)

    # Top edge
    points_y1 = np.concatenate(([y1], params, [y2]))
    interpolator = sp.interpolate.interp1d(points_x1, points_y1, kind='cubic')
    polygon_points_y1 = interpolator(polygon_points_x)

    # Bottom edge
    polygon_points_y2 = -polygon_points_y1

    # Zip coordinates into a list of tuples, reflect and reorder. Need to be passed ordered in a CCW sense
    polygon_points_up = [(x, y) for x, y in zip(polygon_points_x, polygon_points_y1)]
    polygon_points_down = [(x, y) for x, y in zip(polygon_points_x, polygon_points_y2)]
    polygon_points = np.array(polygon_points_up[::-1] + polygon_points_down)

    return polygon_points

print("Initial points: ", initial_points_y)
x = np.linspace(start=0, stop=1, num=initial_points_x.size)

# Boundaries
bounds = [(0.0e-6, dev_params['width']+1e-6)] * initial_points_y.size

# Load from 2D results if available
try:
    prev_results = np.loadtxt('2D_parameters.txt')
    print("Loaded prev. results: ",prev_results)
except:
    print("Couldn't find the file containing 2D optimization parameters. Starting with default parameters")
    prev_results = initial_points_y

plot_spliter(prev_results)

# Set device and cladding materials, as well as as device layer thickness
eps_in = Material(name='Si (Silicon) - Palik', mesh_order=2)
eps_out = Material(name='SiO2 (Glass) - Palik', mesh_order=3)
depth = 220.0e-9

# Initialize FunctionDefinedPolygon class
polygon = FunctionDefinedPolygon(func=opt_device,
                                 initial_params=prev_results,
                                 bounds=bounds,
                                 z=0.0,
                                 depth=depth,
                                 eps_out=eps_out, eps_in=eps_in,
                                 edge_precision=5,
                                 dx=1.0e-9)

# Define figure of merit
fom1 = ModeMatch(monitor_name='fom1',
                 mode_number='fundamental mode',    
                 direction='Forward',
                 target_T_fwd=lambda wl: np.ones(wl.size),
                 norm_p=1)

fom2 = ModeMatch(monitor_name='fom2',
                 mode_number='fundamental mode',    
                 direction='Forward',
                 target_T_fwd=lambda wl: np.ones(wl.size),
                 norm_p=1)

fom3 = ModeMatch(monitor_name='fom3',
                 mode_number='fundamental mode',   
                 direction='Forward',
                 target_T_fwd=lambda wl: np.ones(wl.size),
                 norm_p=1)

fom4 = ModeMatch(monitor_name='fom4',
                 mode_number='fundamental mode',    
                 direction='Forward',
                 target_T_fwd=lambda wl: np.ones(wl.size),
                 norm_p=1)


optimizer_1 = ScipyOptimizers(max_iter=30,
                              method='L-BFGS-B',
                              # scaling_factor = scaling_factor,
                              pgtol=1.0e-4,
                              ftol=1.0e-4,
                              # target_fom = 0.0,
                              scale_initial_gradient_to=0.0)

opt1 = Optimization(base_script=init_sim,
                    wavelengths=wavelengths,
                    fom=fom1,
                    geometry=polygon,
                    optimizer=optimizer_1,
                    use_var_fdtd=True,
                    hide_fdtd_cad=False,
                    use_deps=True,
                    plot_history=True,
                    store_all_simulations=False)

opt2 = Optimization(base_script=init_sim,
                    wavelengths=wavelengths,
                    fom=fom2,
                    geometry=polygon,
                    optimizer=optimizer_1,
                    use_var_fdtd=True,
                    hide_fdtd_cad=False,
                    use_deps=True,
                    plot_history=True,
                    store_all_simulations=False)

opt3 = Optimization(base_script=init_sim,
                    wavelengths=wavelengths,
                    fom=fom3,
                    geometry=polygon,
                    optimizer=optimizer_1,
                    use_var_fdtd=True,
                    hide_fdtd_cad=False,
                    use_deps=True,
                    plot_history=True,
                    store_all_simulations=False)

opt4 = Optimization(base_script=init_sim,
                    wavelengths=wavelengths,
                    fom=fom4,
                    geometry=polygon,
                    optimizer=optimizer_1,
                    use_var_fdtd=True,
                    hide_fdtd_cad=False,
                    use_deps=True,
                    plot_history=True,
                    store_all_simulations=False)
                   
opt = opt1 + opt2 + opt3 + opt4
results = opt.run()
print(results)

# Save parameters to file
np.savetxt('../2D_parameters.txt', results[1])

# Export generated structure
#gds_export_script = str("")

# with lumapi.MODE(hide=False) as sim:
#     sim.cd(project_directory)
#     y_branch_init_inTE(sim)
#     sim.addpoly(vertices=splitter(results[1]))
#     sim.set('x', 0.0)
#     sim.set('y', 0.0)
#     sim.set('z', 0.0)
#     sim.set('z span', depth)
#     sim.set('material', 'Si (Silicon) - Palik')
#     sim.save("y_branch_2D_FINAL")
#     # sim.eval(gds_export_script)
