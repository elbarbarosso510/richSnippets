# Draw an arbitrary photonic device
Playground for drawing weird shapes, workspace for NYUAD students working in the development of an inverse designed AWG. We will generate an extruded strcture from this polygon to be our planar integrated photonic system.

The folder 'varFDTD_AdjointOptimization' contains a script to use adjoint optimization for the design of an MMI with an arbitray shape for the strcture's boundaries defined using a spline passing through a set of control points. The y-coordinate of each control point is one of the N parameters of the optimization. This design apporach uses https://github.com/chriskeraly/lumopt .

### Notes to students:
I dropped a few lines of code that can help you draw an arbitrary polygon using a few parameters. Here I used sinusoidal functions but you can use whatever you can imagine. Try playing with this and think about how you can change it to generate any other possible shape, either a more complex one, or a completely different type of shape. Remember that what you are to design is a system capable of separating various colors (wavelengths) of light. This is often done using an arrayed waveguide grating (AWG), so look for existing shapes of AWGs and see if you can up with a form of equation that could describe the shape of the said existing device. Use as many parameters as you can imagine may be necessary. In the future, we will use that function to run our optimization process.

Also remember that in your application, the system will have optical inputs and outputs that are not part of the optimizable device, so those should somehow constrain your shape. Can you add inouts and outputs to the polygon in the code and show me how that would look?

## Export shape to gds

Add this script at the end of the optimizer code to export the resulting shape to a gds file.

```
gds_export_script = str("f = gdsopen('isolator_export.gds');\
                         cellname = 'TOP';\
                         gdsbegincell(f,cellname);\
                         layer = 1;\
                         layer_pin = '1:10';\
                         layer_devrec = 68;\
                         select('isolator');\
                         poly = get('vertices');\
                         gdsaddpoly(f,layer, poly);\
                         select('wg_left');\
                         gdsaddpath(f, layer_pin, "+str(dev_params['wg01'])+",  ["+str(x_0+0.05e-6)+", get('y'); "+str(x_0-0.05e-6)+", get('y')]); \
                         gdsaddtext(f, 1, "+str(x_0)+", get('y'), 'opt1');\
                         select('wg_right');\
                         gdsaddpath(f, layer_pin, "+str(dev_params['wg02'])+",  ["+str(x_end-0.05e-6)+", get('y'); "+str(x_end+0.05e-6)+", get('y')]); \
                         gdsaddtext(f, 1, "+str(x_end)+", get('y'), 'opt2');\
                         select('mesh');\
                         gdsaddrect(f, layer_devrec, 0,0, get('x span') ,  get('y span'));\
                         gdsendcell(f);\
                         gdsclose(f);\
                        ")

with lumapi.MODE(hide=False) as sim:
    try:
        print('Mode is FDTD = ', isinstance(sim, lumapi.FDTD))
        sim.cd(project_directory)
        RotatorR_TE(sim)
        sim.addpoly(vertices=device_shape(prev_results))
        sim.set('name','isolator')
        sim.set('x', 0.0)
        sim.set('y', 0.0)
        sim.set('z', 0.0)
        sim.set('z span', depth)
        sim.set('material', 'Si (Silicon) - Palik')
        sim.save('final_FDTD')
        # Run Export Script
        sim.eval(gds_export_script)
        input('Press Enter to escape...')
    except LumApiError as err:
        print(C.YELLOW +f"LumAPI Exception {err=}, {type(err)=}" + C.ENDC)
        sim.close()
        raise
    except BaseException as err:
        print(C.RED +f"Unexpected {err=}, {type(err)=}"+ C.ENDC)
        sim.close()
        raise
```
  
