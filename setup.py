from setuptools import find_packages
from setuptools import setup

with open('requires.txt') as f:
    required = f.read().splitlines()

setup(
    name='ad-mysql',
    namespace_packages=['activities_python'],
    python_requires='>=2.7.1',
    version="1.0",
    install_requires=required,
    description='MySQL Adapter',
    packages=find_packages(exclude=['tests', 'tests.*']),
    scripts=['worker/activities-worker'],
    zip_safe=True,
    setup_requires=['pytest-runner'],
    tests_require=['flake8', 'pytest', 'responses'],
)
