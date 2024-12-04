from setuptools import setup, find_packages
#from graphrag_extra.cli.main import app

setup(
    name='graphrag_extra',
    version='0.1.4',
    py_modules=['graphrag_extra'],
    entry_points ={
        'console_scripts': [
          'graphrag_extra=graphrag_extra.cli.main:app'
        ]
      },
)