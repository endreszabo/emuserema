from setuptools import setup

name = 'emuserema'
version = '0.1.post4'
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
    packages=['emuserema'],
    include_package_data=True,
    install_requires=[
        'ruamel.yaml',
    ],
    scripts=[
        'bin/viemuserema',
    ],
    extras_require = {
        'ansible_inventory_plugin': ["ansible"]
    },
    entry_points={
        'console_scripts': [
            'emuserema = emuserema.__main__:main'
        ]
    },
    zip_safe=False
)

