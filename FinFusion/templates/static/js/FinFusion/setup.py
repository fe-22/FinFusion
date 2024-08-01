from setuptools import setup

setup(
    name='FinFusion',
    version='1.0',
    packages=['app'],
    include_package_data=True,
    install_requires=['flask', 'flask_sqlalchemy', 'openpyxl'],
    entry_points={
        'console_scripts': ['finfusion=app:app']
    }
)