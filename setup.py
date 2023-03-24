#!/usr/bin/env python

from setuptools import setup


setup(name='kasli-i2c',
      version='1.0',
      description='Utilities to access the Sinara I2C tree via Kasli, including Sinara EEPROM deployment, firmware flashing for Fastino, Banker',
      author='QUARTIQ',
      url='https://github.com/quartiq/kasli-i2c',
      packages=[
        'kasli_i2c'
      ],
      python_requires='>=3.7, <4',
      install_requires=[
        "pyftdi",
        "requests"
      ],
      setup_requires=[
        'wheel'
      ],
      entry_points={
        'console_scripts': [
          'scan_eem=kasli_i2c.scan_eem:main'
        ]
      }
)