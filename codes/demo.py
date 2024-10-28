#!/usr/bin/env python
import yaml
import numpy as np
import matplotlib.pyplot as plt

# load configuration
with open('config.yml', mode='r') as fp:
    cfg = yaml.safe_load(fp)
print('Configuration loaded.')
print(''.ljust(60,'='))
print('  + Red laser parameters:')
print('    - Typical wavelength: {} \u00b1 {} nm'.format(
    cfg['laser-int-r']['wavelength'],
    cfg['laser-int-r']['bandwidth']))
print('    - Wavelength stability: {} nm'.format(
    cfg['laser-int-r']['stability']))
print('    - Peak intensity: {:g} counts/s'.format(
    eval(cfg['laser-int-r']['intensity'])))
print('    - Power imbalance: {} \u0025'.format(
    100.0 * eval(cfg['laser-int-r']['imbalance'])))
print(''.ljust(60,'-'))
print('  + Green laser parameters:')
print('    - Typical wavelength: {} \u00b1 {} nm'.format(
    cfg['laser-int-g']['wavelength'],
    cfg['laser-int-g']['bandwidth']))
print('    - Wavelength stability: {} nm'.format(
    cfg['laser-int-g']['stability']))
print('    - Peak intensity: {:g} counts/s'.format(
    eval(cfg['laser-int-g']['intensity'])))
print('    - Power imbalance: {} \u0025'.format(
    100.0 * eval(cfg['laser-int-g']['imbalance'])))
print(''.ljust(60,'-'))
print('  + Interference sensor parameters:')
print('    - Amplitude stability: {} \u0025'.format(
    100.0*cfg['sensor-int']['amplitude-stability']))
print('    - Phase stability: {} \u0025'.format(
    100.0*cfg['sensor-int']['phase-stability']))
print(''.ljust(60,'-'))
print('  + ToF sensor parameters:')
print('    - Precision: {} mm'.format(
    cfg['sensor-tof']['precision']))
print(''.ljust(60,'-'))
print('  + Runtime parameters:')
print('    - Spectral resolution: {}'.format(
    cfg['runtime']['spectral-resolution']))
print('    - Parameter resolution: {}'.format(
    cfg['runtime']['parameter-resolution']))
print(''.ljust(60,'='))

# set parameters
r_wavelength  =      cfg['laser-int-r']['wavelength']
r_bandwidth   =      cfg['laser-int-r']['bandwidth']
r_intensity   = eval(cfg['laser-int-r']['intensity'])
r_imbalance   = eval(cfg['laser-int-r']['imbalance'])
g_wavelength  =      cfg['laser-int-g']['wavelength']
g_bandwidth   =      cfg['laser-int-g']['bandwidth']
g_intensity   = eval(cfg['laser-int-g']['intensity'])
g_imbalance   = eval(cfg['laser-int-g']['imbalance'])
amp_stability =      cfg['sensor-int']['amplitude-stability']
pha_stability =      cfg['sensor-int']['phase-stability']
tof_precision =      cfg['sensor-tof']['precision']
run_spec_res  =      cfg['runtime']['spectral-resolution']
run_para_res  =      cfg['runtime']['parameter-resolution']

