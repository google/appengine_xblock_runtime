"""Set up for App Engine XBlock runtime"""

from setuptools import setup

setup(
    name='appengine_xblock_runtime',
    version='0.1',
    description='App Engine XBlock runtime',
    packages=['appengine_xblock_runtime'],
    install_requires=['XBlock'],
)
