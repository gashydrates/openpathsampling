#!/usr/local/bin/env python

"""
Part of a tutorial program illustrating how to set up a simple MD simulation with OpenMM

DESCRIPTION
setting up an nvt equilibration with position constraints

@author Antonia Mey <antonia.mey@fu-berlin.de>



"""

#=============================================================================================
# PARAMETERS
#=============================================================================================

from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
from sys import stdout
import numpy as np
import time

#=============================================================================================
# PARAMETERS
#=============================================================================================

temperature = 300.0 * kelvin # temperature
collision_rate = 1.0 / picoseconds # collision rate for Langevin dynamics
timestep = 2.0 * femtoseconds # timestep for Langevin integrator
nequib_steps = 100 #number of nvt equilibration steps with position constraints on Alanine
#platform = openmm.Platform.getPlatformByName("Cuda") # platform to use

max_iterations = 10 # number of iterations of nsteps_per_interation of dynamics to run
nsteps_per_iteration = 1000 # number of steps of dynamics per iteration
Alanine_atoms = 22
platform = openmm.Platform.getPlatformByName("CPU") # platform to use

#=============================================================================================
# Main simulation body
#=============================================================================================

start_time = time.time()
pdb = PDBFile('data/Alanine_solvated.pdb')
forcefield = ForceField('amber99sbildn.xml', 'tip3p.xml')
system = forcefield.createSystem(pdb.topology, nonbondedMethod=PME, nonbondedCutoff=1*nanometer, constraints=HBonds)
integrator = LangevinIntegrator(temperature, collision_rate, timestep)
simulation = Simulation(pdb.topology, system, integrator, platform)
simulation.context.setPositions(pdb.positions)
print simulation.context.getPlatform().getName()  #Prints the name of the platform, openCL is selected by default

#Dirty Position Constraints for NVT
Alanine_masses = np.zeros(Alanine_atoms, numpy.double)
Alanine_masses = Quantity(Alanine_masses, dalton)
for i in range(Alanine_atoms):
	Alanine_masses[i]= system.getParticleMass(i)
	system.setParticleMass(i, 0.0)

#now positions are constraint of the Alanine and the NVT equilibration can be run
simulation.reporters.append(StateDataReporter('data/nvtInfo.dat', 100, step=True, potentialEnergy=True, temperature=True, separator=' '))
#simulation.reporters.append(PDBReporter('nvt.pdb', 50)) #write out every 50 steps to a pdb file
simulation.step(nequib_steps)

#now we are ready for the production run first we need to revert the masses though
for i in range(Alanine_atoms):
	system.setParticleMass(i,Alanine_masses[i].value_in_unit(dalton))

#tracking data
for iteration in range(max_iterations):
	simulation.step(nsteps_per_iteration)
  	state = simulation.context.getState(getEnergy=True, enforcePeriodicBox = True)
    	print "Iteration %5d / %5d | kinetic %8.3f kJ/mol | potential %8.3f kJ/mol" % (iteration, max_iterations, state.getKineticEnergy() / kilojoules_per_mole, state.getPotentialEnergy() / kilojoules_per_mole)
	
end_time = time.time()
print "total time "+str(end_time-start_time)	

