'''wf-api-client - The WebFaction API client'''

import os
from setuptools import setup, find_packages


def file_read(filename):
    try:
        return open(os.path.join(os.path.dirname(__file__), filename)).read()
    except IOError:
        return ''


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='wf-api-client',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='A local client for interfacing to the WebFaction web hosting server API.',
    long_description=file_read('README.rst'),
    url="https://github.com/davidjcox/wf-api-client",
    author='David J Cox',
    author_email='davidjcox.at@gmail.com',
    classifiers=[
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development',
        'Topic :: System',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    install_requires=[],
    keywords='WebFaction webfaction webhosting web hosting API api client',
    zip_safe=False,
)

#EOF - wf-api-client setup