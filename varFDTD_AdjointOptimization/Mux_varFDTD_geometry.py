#############################################################################
# Python Module: polsplitter_varFDTD_geometry.py
# Based on: Lumerical Example file: lmopt \ varFDTD_geometry.py
#
##############################################################################

import lumapi
import numpy as np

from params import dev_params


wg01_offset_y = dev_params['in_offset']
dx = dev_params['length'] / (dev_params['num_points']-1)

size_x = dev_params['length']+2*dx+2e-6
size_y = dev_params['width']+2e-6


def sim_init_in(mode):
    in_wg_width = dev_params['wg01']
    out_wg_width = dev_params['wg02']
    spacing = dev_params['spacing']
    wg01_offset_y = dev_params['in_offset']
    dx = dev_params['length'] / (dev_params['num_points']-1)

    finer_mesh_size_x = dev_params['length']+2*dx
    finer_mesh_size_y = dev_params['width']+1e-6
    mesh_x = 40e-9
    mesh_y = 40e-9

    mesh_accuracy = 3
    lam_c = 1.550e-6

    # Clear session
    mode.switchtolayout()
    mode.selectall()
    mode.delete()
    
    # Input Waveguides
    
    mode.addrect()
    mode.set('name', 'input wg')
    mode.set('x span', 3e-6)
    mode.set('y span', in_wg_width)
    mode.set('z span', 220e-9)
    mode.set('y', wg01_offset_y)
    mode.set('x', -(1.5e-6+dev_params['length']/2)-dx + 0.05e-6)
    mode.set('z', 0)
    mode.set('material', 'Si (Silicon) - Palik')
    
    # Output Waveguides
    
    y0 =  3*(out_wg_width+spacing)/2    # Position of the top waveguide port
    dy = -(out_wg_width+spacing)           # Change in the posoition of the ports

    mode.addrect()
    mode.set('name', 'output_01')
    mode.set('x span', 3e-6)
    mode.set('y span', out_wg_width)
    mode.set('z span', 220e-9)
    mode.set('y', y0)
    mode.set('x', 1.5e-6+dev_params['length']/2 + dx - 0.05e-6)
    mode.set('z', 0)
    mode.set('material', 'Si (Silicon) - Palik')
    
    mode.copy() # Copy the last created structure
    mode.set('name', 'output_02')
    mode.set('y', y0 + dy)

    mode.copy() # Copy the last created structure
    mode.set('name', 'output_03')
    mode.set('y', y0 + 2*dy)

    mode.copy() # Copy the last created structure
    mode.set('name', 'output_04')
    mode.set('y', y0 + 3*dy)


    # Substrate

    mode.addrect()
    mode.set('name','sub')
    mode.set('x span',12e-6)
    mode.set('y span',10e-6)
    mode.set('z span',10e-6)
    mode.set('y',0)
    mode.set('x',0)
    mode.set('z',0)
    mode.set('material', 'SiO2 (Glass) - Palik')
    mode.set('override mesh order from material database', 1)
    mode.set('mesh order', 3)
    mode.set('alpha', 0.3)
    
    # varFDTD
    mode.addvarfdtd()
    mode.set('mesh accuracy', mesh_accuracy)
    mode.set('x min', -size_x/2)
    mode.set('x max', size_x/2)
    mode.set('y min', -size_y/2)
    mode.set('y max', size_y/2)
    mode.set('force symmetric y mesh', 1)
    mode.set('y min bc', 'PML')
    mode.set('z', 0)
    
    mode.set('effective index method', 'variational')
    mode.set('can optimize mesh algorithm for extruded structures', 1)
    mode.set('clamp values to physical material properties', 1)
    
    x_t = 0.3e-6+dev_params['length']/2
    y_t = dev_params['in_offset']
    mode.set('x0', -x_t)
    mode.set('y0', y_t)
    mode.set('number of test points', 4)
    mode.set('test points', np.array([[0, 0],[x_t, 0.4e-6], [x_t, -0.4e-6], [x_t, 0]]))
    
    # MESH IN OPTIMIZABLE REGION
    mode.addmesh()
    mode.set('x', 0)
    mode.set('x span',finer_mesh_size_x)
    mode.set('y', 0)
    mode.set('y span',finer_mesh_size_y)
    mode.set('dx', mesh_x)
    mode.set('dy', mesh_y)
    
    # OPTIMIZATION FIELDS MONITOR IN OPTIMIZABLE REGION
    
    mode.addpower()
    mode.set('name','opt_fields')
    mode.set('monitor type','2D Z-normal')
    mode.set('x', 0)
    mode.set('x span', finer_mesh_size_x)
    mode.set('y', 0)
    mode.set('y span', finer_mesh_size_y)
    mode.set('z', 0)

    # SET POWER MONITORS AND SOURCES

    mode.select('varFDTD')
    mode.set('polarization', dev_params['polarization'])

    ## SOURCE
    mode.addmodesource()
    mode.set('direction', 'Forward')
    mode.set('injection axis', 'x-axis')
    mode.set('y', 0)
    mode.set("y span", size_y)
    mode.set('x', -size_x/2+0.5e-6)
    mode.set('center wavelength', lam_c)
    mode.set('wavelength span', 100e-9)
    mode.set('mode selection', 'fundamental mode')  # Can be set to 'fundamental mode' or 'user select'
   
    # fom waveguide top

    mode.addpower()
    mode.set('name', 'fom1')
    mode.set('monitor type', 'Linear Y')
    mode.set('x', finer_mesh_size_x / 2)
    mode.set('y', y0)
    mode.set('y span', 1e-6)
    mode.set('z', 0)

    mode.copy()
    mode.set('name','fom2')
    mode.set('y', y0+dy)

    mode.copy()
    mode.set('name','fom3')
    mode.set('y', y0+2*dy)

    mode.copy()
    mode.set('name','fom4')
    mode.set('y', y0+3*dy)

    # FINALLY SET SIMULATION RESSOURCES
    
    mode.setresource("varFDTD",1,"processes","4")
    mode.setresource("varFDTD",1,"threads","4")


if __name__ == "__main__":
    mode = lumapi.MODE(hide=False)
    sim_init_in(mode)
    input('Press Enter to escape...')

