from __future__ import absolute_import, division, print_function
from os.path import join as pjoin
from setuptools import setup, find_packages

# Long description will go up on the pypi page
with open('README.md') as file:
    LONG_DESCRIPTION = file.read()
    
# Dependencies.
with open('requirements.txt') as f:
    requirements = f.readlines()
INSTALL_REQUIRES = [t.strip() for t in requirements]

opts = dict(name='reportgeneration-LSSS',
            maintainer='Sindre Vatnehol',
            maintainer_email='sindre.vatnehol@gmail.com',
            description='Tools to read, convert and write annotatons from fisheries acoustics',
#            long_description=LONG_DESCRIPTION,
            url='https://github.com/CRIMAC-WP4-Machine-learning/CRIMAC-reportgeneration-LSSS',
            download_url='',
            license='MIT',
            classifiers=['Development Status :: 3 - Alpha',
                         'Environment :: Console',
                         'Intended Audience :: Science/Research',
                         'License :: OSI Approved :: MIT',
                         'Operating System :: OS Independent',
                         'Programming Language :: Python',
                         'Topic :: Scientific/Engineering'],
            author='Sindre Vatnehol',
            author_email='sindre.vatnehol@gmail.com',
            platforms='OS Independent',
#            version=versioneer.get_version(),
#            cmdclass=versioneer.get_cmdclass(),
            packages=find_packages(),
            install_requires=INSTALL_REQUIRES,
            tests_require='tox',
            scripts=['LSSSintegration/process/LSSSintegration.py','LSSSintegration/writer/metadata_convention.py'],
            dependency_links=['https://github.com/CRIMAC-WP4-Machine-learning/CRIMAC-preprocessing.git']
            )


if __name__ == '__main__':
    setup(**opts)