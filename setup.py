
from setuptools import setup, find_packages

setup(
    name='slashbot',
    version='0.0.2',
    license='MIT',
    author="Eric Brassell",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/ebrassell/slashbot',
    keywords='slack bot slash slackbot lambda',
    install_requires=['requests>=2.0.0'
      ],
    py_modules=['slashbot'],

)
