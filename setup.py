from setuptools import setup, find_packages
setup(
    name='namastox',
    version='0.0.1',
    license='GNU GPLv3 or posterior',
    description='',
    url='https://github.com/phi-grib/namastox',
    download_url='https://github.com/phi-grib/namastox.git',
    author='Manuel Pastor',
    author_email='manuel.pastor@upf.edu',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['namastox=src.namastox_scr:main'],
    },
    # If any package contains *.txt or *.rst files, include them:
    package_data={'namastox': ['*.yaml', 'documentation.docx']},
    install_requires=['appdirs']
)
