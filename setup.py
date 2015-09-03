try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys

requirement_list = [r.strip() for r in open('requirements.txt', 'r').readlines() if r]


setup(name='DeltaMail',
      version='0.0.1',
      install_requires= requirement_list,
      author='Delta Force',
      author_email='delta@nitt.edu',
      packages=['deltamail'],
      entry_points={
          'console_scripts': ['delta-mail=deltamail:console_main'],
      },
      test_suite='tests',
      url='https://github.com/delta/mailer/',
      description='Mailer module',
      classifiers=[
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Topic :: Utilities'
      ],
      )
