#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 01:55:07 2021

@author: ashimsg
"""

###################
# Loading modules #
###################

import numpy as np
import scipy.integrate as integrate
from scipy.integrate import odeint
from scipy.optimize import fsolve
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.colors import LogNorm
from matplotlib.ticker import LogFormatterMathtext
from HiCOLA.Frontend import expression_builder as eb
import HiCOLA.Frontend.numerical_solver as ns
import sympy as sym
import sys
import itertools as it
import time
import os
from HiCOLA.Utilities.Other import support as sp
from configobj import ConfigObj
from HiCOLA.Frontend.read_parameters import read_in_parameters
from argparse import ArgumentParser

to_exec = eb.declare_symbols()
exec(to_exec)

parser = ArgumentParser(prog='Generate_Simulation_Input')
parser.add_argument('input_ini_filenames',nargs=2)

args = parser.parse_args()
print(args)
filenames = args.input_ini_filenames
Horndeski_path = filenames[0]
numerical_path = filenames[1]

read_out_dict = read_in_parameters(Horndeski_path, numerical_path)
odeint_parameter_symbols = [E, phi, phiprime, omegar, omegam]
read_out_dict.update({'odeint_parameter_symbols':odeint_parameter_symbols})



model = read_out_dict['model_name']
K = read_out_dict['K']
G3 = read_out_dict['G3']
G4 = read_out_dict['G4']
cosmology_name = read_out_dict['cosmo_name']
[Omega_r0, Omega_m0, Omega_l0] = read_out_dict['cosmological_parameters']
[U0, phi0, phi_prime0] = read_out_dict['initial_conditions']
[Npoints, z_max, supp_flag, threshold_value, GR_flag] = read_out_dict['simulation_parameters']
parameters = read_out_dict['Horndeski_parameters']
mass_ratio_list = read_out_dict['mass_ratio_list']
symbol_list = read_out_dict['symbol_list']
closure_declaration = read_out_dict['closure_declaration']

closure_dictionary = {'odeint_parameters':odeint_parameter_symbols, 'parameters':symbol_list}

print('phiprime0 is '+str(phi_prime0))
#---Create Horndeski functions---
###################COMMENT/UNCOMMENT
lambdified_functions = eb.create_Horndeski(K,G3,G4,symbol_list,mass_ratio_list)
lambdified_kmou = eb.create_kmouflage(G4, symbol_list, mass_ratio_list)
read_out_dict.update(lambdified_functions)
read_out_dict.update(lambdified_kmou)
######################################


print('Horndeski functions --------------')
print(f'K = {K}')
print(f'G_3 = {G3}')
print(f'G_4 = {G4}')
print('Horndeski parameters--------------')

# #---Run solver and save output---COMMENT/UNCOMMENT
print(model+' model parameters, ' + str(symbol_list)+' = '+str(parameters))
print('Cosmological parameters-----------')
print('Omega_m0 = '+str(Omega_m0))
print('Omega_r0 = '+str(Omega_r0))
print(f'Omega_lambda0 = f{Omega_l0}')
print('Initial conditions----------------')
print(f'Hubble0 = {U0}')
print(f'scalar_prime0 = {phi_prime0}')

background_quantities = ns.run_solver(read_out_dict)
a_arr = background_quantities['a']
UE_arr = background_quantities['Hubble']
phi_arr = background_quantities['scalar']
phi_prime_arr = background_quantities['scalar_prime']
omega_m_arr = background_quantities['omega_m']
omega_r_arr = background_quantities['omega_r']
omega_phi_arr = background_quantities['omega_phi']
omega_lambda_arr = background_quantities['omega_l']
UE_prime_arr = background_quantities['Hubble_prime']
UE_prime_UE_arr = background_quantities['E_prime_E']
coupling_factor_arr = background_quantities['coupling_factor']
chioverdelta_arr = background_quantities['chi_over_delta']

closure_variable = str(closure_dictionary[closure_declaration[0]][closure_declaration[1]])
closure_value = str(background_quantities['closure_value'])
print(f'Closure parameter is {closure_variable} = {closure_value}' )
print('(note: therefore one of the initial conditions or Horndeski model parameters printed above was the guess value)')

print('Files for Hi-COLA numerical simulation being generated.')
###----Intermediate quantities-----
##Note: U = E/E_dS
## U0 = 1/E_dS
print(f'U0 is {U0}')
E_arr = np.array(UE_arr)#/U0 #check whether COLA requires intermediates constructed with E rather than U!
E_prime_arr = np.array(UE_prime_arr)#/U0 #check whether backend requires intermediates constructed with Eprime rather than Uprime!
##Note: E_prime_E is the same as U_prime_U, so that array does not need to be multiplied by anything.

print('testtestsetsetset')
print(lambdified_kmou['kmou_coupling'](1,1, 1))

K0 = parameters[0]
print(lambdified_kmou['kmou_screening'](U0,K0,1,1))

kmou_coupling_arr = []
kmou_screening_arr = []
for phiv in phi_arr:
        kmou_coupling_arr.append(lambdified_kmou['kmou_coupling'](phiv, *parameters))
        kmou_screening_arr.append(lambdified_kmou['kmou_screening'](U0, K0, phiv, *parameters[1:])) #parameters[1:] should exclude K0 parameter

growthfac_arr, growthfracprime_arr = ns.solve_1stgrowth_factor(a_arr, omega_m_arr, UE_prime_UE_arr, kmou_coupling_arr)

directory = read_out_dict['output_directory']

if not os.path.exists(directory):
    os.makedirs(directory)

filename_expansion = directory+f'/{model}_{cosmology_name}_expansion.txt'
filename_force = directory+f'/{model}_{cosmology_name}_force.txt'
filename_full = directory+f'/{model}_{cosmology_name}_full.txt'

abs_directory = os.path.abspath(directory)
loop_counter = 0
while ( os.path.exists(filename_expansion) or os.path.exists(filename_force) ) and loop_counter < 100:
    loop_counter += 1
    filename_expansion = sp.renamer(filename_expansion)
    filename_force = sp.renamer(filename_force)
    filename_full = sp.renamer(filename_full)
if loop_counter >= 100:
    raise Exception("Counter for file renaming loop excessively high, consider changing expansion and force output file names.")
if loop_counter != 0:
    print(f"Warning: expansion or force file with same name found in \"{abs_directory}\", new filenames are \n expansion: {filename_expansion} \n force:{filename_force}")

expansion_datanames = 'a    E    E\'/E'
full_datanames = 'a    E    E\'/E    phi    phi\'    omega_m    omega_r    omega_phi    omega_lambda    Growthfac    Growthfacprime'
force_datanames = 'a    S (zeta/rootgradphi)    beta (coupling_factor)'


sp.write_data_flex([a_arr,E_arr, UE_prime_UE_arr],filename_expansion, expansion_datanames)
sp.write_data_flex([a_arr, E_arr, UE_prime_UE_arr, phi_arr, phi_prime_arr, omega_m_arr, omega_r_arr, omega_phi_arr, omega_lambda_arr, growthfac_arr, growthfracprime_arr], filename_full, full_datanames)
sp.write_data_flex([a_arr,kmou_screening_arr,kmou_coupling_arr],filename_force, force_datanames)

   
print(f'Files generated. Saved in {abs_directory}')