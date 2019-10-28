from setuptools import setup

name = 'emuserema'
version = '0.1'
description = 'EMUSEREMA Multiprotocol Session and Redirect Manager'

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name=name,
    version=version,
    description=description,
    url='http://github.com/endreszabo/emuserema',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Systems Administration',
    ],
    author='Endre Szabo',
    author_email='emuserema@end.re',
    license='GPLv2',
    #packages=['emuserema'],
    install_requires = [
        'ruamel.yaml',
    ],
    zip_safe=False
)
