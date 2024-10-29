#!/usr/bin/env python
"""Laser metrology demonstration.
Syntax:
  demo.py [-c CONFIG_PATH]

Default config path: ./config.yml
"""

import sys
import types
import yaml
import numpy as np
import matplotlib.pyplot as plt
from os import path
from getopt import gnu_getopt

# initialize global variables
cfg_path = './config.yml'
cfg = types.SimpleNamespace()
sensor_int_dtype = np.dtype([
    ('A','u8'),
    ('B','u8'),
    ('C','u8'),
    ('D','u8')])
sensor_r = types.SimpleNamespace()
sensor_r.dtype = sensor_int_dtype
sensor_r.phases = np.double([0., np.pi*1.5, np.pi, np.pi*1.5])
snesor_r.amplitudes = np.double([1., 1., 1., 1.])
sensor_g = types.SimpleNamespace()
sensor_g.dtype = sensor_int_dtype
sensor_g.phases = np.double([0., np.pi*1.5, np.pi, np.pi*1.5])
sensor_g.amplitudes = np.double([1., 1., 1., 1.])

def load_config(cfg_path):
    """Load configuration file.
"""
    # load configuration
    with open(cfg_path, mode='r') as fp:
        cfgdict = yaml.safe_load(fp)
    print('Configuration loaded from {}'.format(cfg_path))
    print(''.ljust(60,'='))
    print('  + Red laser parameters:')
    print('    - Typical wavelength: {} \u00b1 {} nm'.format(
        cfgdict['laser-int-r']['wavelength'],
        cfgdict['laser-int-r']['bandwidth']))
    print('    - Wavelength stability: {} nm'.format(
        cfgdict['laser-int-r']['stability']))
    print('    - Peak intensity: {:g} counts/s'.format(
        eval(cfgdict['laser-int-r']['intensity'])))
    print('    - Power imbalance: {} \u0025'.format(
        100.0 * eval(cfgdict['laser-int-r']['imbalance'])))
    print(''.ljust(60,'-'))
    print('  + Green laser parameters:')
    print('    - Typical wavelength: {} \u00b1 {} nm'.format(
        cfgdict['laser-int-g']['wavelength'],
        cfgdict['laser-int-g']['bandwidth']))
    print('    - Wavelength stability: {} nm'.format(
        cfgdict['laser-int-g']['stability']))
    print('    - Peak intensity: {:g} counts/s'.format(
        eval(cfgdict['laser-int-g']['intensity'])))
    print('    - Power imbalance: {} \u0025'.format(
        100.0 * eval(cfgdict['laser-int-g']['imbalance'])))
    print(''.ljust(60,'-'))
    print('  + Interference sensor parameters:')
    print('    - Amplitude stability: {} \u0025'.format(
        100.0*cfgdict['sensor-int']['amplitude-stability']))
    print('    - Phase stability: {} \u0025'.format(
        100.0*cfgdict['sensor-int']['phase-stability']))
    print(''.ljust(60,'-'))
    print('  + ToF sensor parameters:')
    print('    - Precision: {} mm'.format(
        cfgdict['sensor-tof']['precision']))
    print(''.ljust(60,'-'))
    print('  + Runtime parameters:')
    print('    - Spectral resolution: {}'.format(
        cfgdict['runtime']['spectral-resolution']))
    print('    - Distance resolution: {} nm'.format(
        cfgdict['runtime']['distance-resolution']))
    print('    - Parameter resolution: {}'.format(
        cfgdict['runtime']['parameter-resolution']))
    print(''.ljust(60,'='))
    
    # set parameters
    global cfg
    cfg.r_wavelength  = cfgdict['laser-int-r']['wavelength']
    cfg.r_bandwidth   = cfgdict['laser-int-r']['bandwidth']
    cfg.r_intensity   = eval(cfgdict['laser-int-r']['intensity'])
    cfg.r_imbalance   = eval(cfgdict['laser-int-r']['imbalance'])
    cfg.g_wavelength  = cfgdict['laser-int-g']['wavelength']
    cfg.g_bandwidth   = cfgdict['laser-int-g']['bandwidth']
    cfg.g_intensity   = eval(cfgdict['laser-int-g']['intensity'])
    cfg.g_imbalance   = eval(cfgdict['laser-int-g']['imbalance'])
    cfg.amp_stability = cfgdict['sensor-int']['amplitude-stability']
    cfg.pha_stability = cfgdict['sensor-int']['phase-stability']
    cfg.tof_precision = cfgdict['sensor-tof']['precision']
    cfg.run_spec_res  = cfgdict['runtime']['spectral-resolution']
    cfg.run_dist_res  = cfgdict['runtime']['distance-resolution']
    cfg.run_param_res = cfgdict['runtime']['parameter-resolution']

    # set sensors
    global sensor_r, sensor_g
    sensor_r.wavelengths = np.random.normal(
        cfg.r_wavelength,
        np.ones((cfg.run_spec_res,))*cfg.r_bandwidth*.5)
    sensor_r.wavenumbers = np.reshape(
        np.pi*2. / sensor_r.wavelengths, (1, -1))
    sensor_g.wavelengths = np.random.normal(
        cfg.g_wavelength,
        np.ones((cfg.run_spec_res,))*cfg.g_bandwidth*.5)
    sensor_g.wavenumbers = np.reshape(
        np.pi*2. / sensor_g.wavelengths, (1, -1))
    return

def read_sensors(opd):
    """Read observed data from laser interference sensors.
opd is optical path difference between two arms, in nm.
"""
    global sensor_r, sensor_g
    opd = np.reshape(opd, (-1,1))
    mesh_r = opd * sensor_r.wavenumbers
    
    mesh_g = opd * sensor_g.wavenumbers
    
if __name__ == "__main__":
    opts, args = gnu_getopt(sys.argv[1:], 'hc:')
    for opt, val in opts:
        if opt == '-h':
            print(__doc__)
            sys.exit()
        elif opt == '-c':
            cfg_path = path.normpath(path.realpath(val))
        else:
            assert False, 'unhandled option'
    load_config(cfg_path)
