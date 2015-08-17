try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'GVASSOC',
    'author': 'Andre M Ribeiro dos Santos',
    'url': '.',
    'download_url': '.',
    'author_email': 'andremrsantos@gmail.com',
    'version': '0.1',
    'install_requires': ['nose', 'numpy', 'scipy'],
    'packages': ['lib'],
    'scripts': [
        'bin/association.py',
        'bin/query.py'
    ],
    'name': 'lib'
}

setup(**config)