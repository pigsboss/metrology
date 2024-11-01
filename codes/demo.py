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
import numexpr as ne
import matplotlib.pyplot as plt
from os import path
from getopt import gnu_getopt

# initialize global variables
cfg_path = './config.yml'
cfg = types.SimpleNamespace()
sensor_r = types.SimpleNamespace()
sensor_r.phases = np.double([0., np.pi*1.5, np.pi, np.pi*1.5])
sensor_r.gains  = np.double([1., 1., 1., 1.])
sensor_g = types.SimpleNamespace()
sensor_g.phases = np.double([0., np.pi*1.5, np.pi, np.pi*1.5])
sensor_g.gains  = np.double([1., 1., 1., 1.])

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
    print('    - Gain stability: {} \u0025'.format(
        100.0*cfgdict['sensor-int']['gain-stability']))
    print('    - Phase stability: {} \u0025'.format(
        100.0*cfgdict['sensor-int']['phase-stability']))
    print('    - Background: {}'.format(
        eval(cfgdict['sensor-int']['background'])))
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
    cfg.r_wavelength   = cfgdict['laser-int-r']['wavelength']
    cfg.r_bandwidth    = cfgdict['laser-int-r']['bandwidth']
    cfg.r_intensity    = eval(cfgdict['laser-int-r']['intensity'])
    cfg.r_imbalance    = eval(cfgdict['laser-int-r']['imbalance'])
    cfg.g_wavelength   = cfgdict['laser-int-g']['wavelength']
    cfg.g_bandwidth    = cfgdict['laser-int-g']['bandwidth']
    cfg.g_intensity    = eval(cfgdict['laser-int-g']['intensity'])
    cfg.g_imbalance    = eval(cfgdict['laser-int-g']['imbalance'])
    cfg.gain_stability = cfgdict['sensor-int']['gain-stability']
    cfg.pha_stability  = cfgdict['sensor-int']['phase-stability']
    cfg.background     = eval(cfgdict['sensor-int']['background'])
    cfg.tof_precision  = cfgdict['sensor-tof']['precision']
    cfg.run_spec_res   = cfgdict['runtime']['spectral-resolution']
    cfg.run_dist_res   = cfgdict['runtime']['distance-resolution']
    cfg.run_param_res  = cfgdict['runtime']['parameter-resolution']

    # set sensors
    global sensor_r, sensor_g
    sensor_r.wavelengths = np.random.normal(
        cfg.r_wavelength,
        np.ones((cfg.run_spec_res,))*cfg.r_bandwidth*.5)
    sensor_r.wavenumbers = np.reshape(
        np.pi*2. / sensor_r.wavelengths, (1, -1, 1))
    sensor_r.phases = np.reshape(np.random.normal(
        sensor_r.phases, cfg.pha_stability), (1, 1, -1))
    sensor_r.gains = np.reshape(np.random.normal(
        sensor_r.gains, cfg.gain_stability), (1, 1, -1))
    sensor_g.wavelengths = np.random.normal(
        cfg.g_wavelength,
        np.ones((cfg.run_spec_res,))*cfg.g_bandwidth*.5)
    sensor_g.wavenumbers = np.reshape(
        np.pi*2. / sensor_g.wavelengths, (1, -1, 1))
    sensor_g.phases = np.reshape(np.random.normal(
        sensor_g.phases, cfg.pha_stability), (1, 1, -1))
    sensor_g.gains = np.reshape(np.random.normal(
        sensor_g.gains, cfg.gain_stability), (1, 1, -1))
    return

def get_sensors_data(opd_in):
    """Get observed data from laser interference sensors.
opd is optical path difference between two arms, in nm.

Sinusoidal wave function:
W(x,t) = A * cos(kx-wt),
where k is wave number, w is angular frequency, W is amplitude
at position x and time t.
Interference of two waves W1 and W2 of similar peak amplitude:
W1(x,t) = A * cos(kx-wt), and
W2(x,t) = A * (1+epsilon) * cos(kx-wt+phi),
where phi is phase difference and epsilon is a small quantity
stands for the imbalance between amplitudes of the two waves.
Intensity of interference fringe formed by W1 and W2 is
I(x,t,phi) = A^2*(
          4   * cos(phi/2)^2 * cos(kx-wt+phi/2)^2 +
  2*epsilon   * cos(phi/2) *   cos(kx-wt+3*phi/4) + 
  2*epsilon   * cos(phi/2) *   cos(phi/4)) +
    epsilon^2 * (1+cos(2kx-2wt+2phi))/2).
Time-averaged of the fringe intensity is
             /T
          1  |
J(phi) = --- | I(x,t,phi) dt
          T  |
             /0
       = A^2 * (
  2           * cos(phi/2)^2 +
  2 * epsilon * cos(phi/2) * cos(phi/4) +
      epsilon^2 / 2
),
where T >> 1/w.
"""
    global sensor_r, sensor_g
    opd = np.reshape(opd_in, (-1,1,1))
    phi = opd * sensor_r.wavenumbers + sensor_r.phases
    data_r = np.random.poisson(
        sensor_r.gains * cfg.r_intensity * np.sum(
            ne.evaluate("2.*cos(phi/2.)**2.+" +
                        "2.*eps*cos(phi/2.)*cos(phi/4.)+" +
                        ".5*eps**2.",
                        local_dict={
                            'eps':cfg.r_imbalance,
                            'phi':phi}),
            axis=1) / cfg.run_spec_res + cfg.background)
    phi = opd * sensor_g.wavenumbers + sensor_g.phases
    data_g = np.random.poisson(
        sensor_g.gains * cfg.g_intensity * np.sum(
            ne.evaluate("2.*cos(phi/2.)**2.+" +
                        "2.*eps*cos(phi/2.)*cos(phi/4.)+" +
                        ".5*eps**2.",
                        local_dict={
                            'eps':cfg.g_imbalance,
                            'phi':phi}),
            axis=1) / cfg.run_spec_res + cfg.background)
    data_tof = np.random.normal(opd, 1e6*cfg.tof_precision)
    return data_r, data_g, data_tof

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
