from setuptools import setup


setup(name="expy",
      version=0.1,      
      packages=["expy"],
      install_requires=["ml_logger"],
      entry_points={'console_scripts': ['expy = expy.expy:main']
      })
