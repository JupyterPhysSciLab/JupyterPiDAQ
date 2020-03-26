import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="JupyterPiDAQ",
    version="0.5.0",
    description="Data Acquisition in Jupyter notebook on Raspberry Pi",
    long_description=long_description,
    author="Jonathan Gutow",
    author_email="jgutow@new.rr.com",
    license="GPL-3.0+",
    packages=setuptools.find_packages(),
    package_data={'javascript': ['*.js']},
    include_package_data=True,
    install_requires=[
        # 'python>=3.6',
        'Adafruit-ADS1x15>=1.0.2',
        'numpy>=1.13',
        'matplotlib>=1.0',
        'jupyter>=1.0.0',
        'jupyter-contrib-nbextensions>=0.5.1',
        'pandas>=0.22.0'
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
