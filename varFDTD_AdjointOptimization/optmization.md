# Adjoint based optmization of a 1x4 Mux in Silicon

Your base structure is a Silicon plannar device with heigth 220 nm. One input port amd 4 output ports, each 460 nm wide. 
You want to optimize the power so that all outputs have equal power. We don't care about the phase at this point.


**Problem:** If power in all outputs has the same weigth in the optimization cost function, given that the total power is limited,
maximizing the power in one port has the same optimal fom than distributing it equally among all ports (We can only add optimization fucntions). 
*How to avoid this?*

### Workaround:
- Set the simulation symmetric vertically.
- Set only one output mode covering two waveguides. 
- Select the in phase mode as the output mode (or outphase, but only one).
- Optimize

