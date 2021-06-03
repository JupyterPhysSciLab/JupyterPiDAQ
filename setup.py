import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="JupyterPiDAQ",
    url = "https://github.com/JupyterPhysSciLab/JupyterPiDAQ",
    version="0.6.0",
    description="Data Acquisition in Jupyter notebook on Raspberry Pi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jonathan Gutow",
    author_email="gutow@uwosh.edu",
    license="GPL-3.0+",
    packages=setuptools.find_packages(exclude=("dist","build","dev_testing",)),
    #package_data={'javascript': ['javascript/*.js']},
    data_files=[
    	('javascript',['jupyterpidaq/javascript/JupyterPiDAQmnu.js'])
    ],
    include_package_data=True,
    install_requires=[
        # 'python>=3.6',
        #RPi.GPIO is required by pi-plates, not sure why not included in the
        # pi-plates setup.py.
        'RPi.GPIO>=0.7.0',
        'Adafruit-PureIO>=1.1.5',
        'Adafruit-ADS1x15>=1.0.2',
        'pi-plates>=6.0',
        'numpy>=1.13',
        'matplotlib>=1.0',
        'plotly>=4.14.3',
        'jupyter>=1.0.0',
        'jupyter-contrib-nbextensions>=0.5.1',
        'pandas>=1.0.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: JavaScript',
        'Operating System :: OS Independent'
    ]
)
