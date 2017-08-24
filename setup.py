from setuptools import setup

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name = 'configmate',
    version = '0.1.0',
    description = 'Python YAML loader where values can be calculated with a simple expression syntax',
    long_description = readme,
    license = 'MIT',
    author = 'Warren Moore',
    author_email = 'warren@wamonite.com',
    url = 'https://github.com/wamonite/configmate',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ],
    packages = ['configmate'],
    package_data = {
        '': [
            'LICENSE',
        ],
    },
    install_requires = [
        'pyaml',
    ],
    extras_require = {
        'AWS':  [
            'boto3'
        ]
    },
    zip_safe = False
)
