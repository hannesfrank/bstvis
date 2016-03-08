from setuptools import setup, find_packages


setup(
    name='bstvis',
    version='0.2.0',

    description='A visualisation framework for binary search trees and algorithms.',

    author='Hannes Frank',
    author_email='frankhannes@googlemail.com',

    url='https://github.com/hannesfrank/bstvis',

    license='MIT',

    packages=find_packages(exclude=('tests', 'docs')),

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',

        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS'
    ],

    keywords='bst visualisation'
)