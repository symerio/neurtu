from setuptools import setup, find_packages

from neurtu import __version__


setup(
    name='neurtu',
    description='A simple benchmarking tool',
    long_description=open('README.rst').read(),
    version=__version__,
    author='Roman Yurchak',
    author_email='roman.yurchak@symerio.com',
    packages=find_packages(),
    url='https://github.com/symerio/neurtu',
    install_requires=['memory_profiler', 'psutil', 'tqdm'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Software Development',
                 'Operating System :: POSIX',
                 'Operating System :: Unix'],
    license='BSD')
