from glob import glob

from setuptools import setup

setup(
    name='ansible-server',
    version='1.1.0',
    description='Ansible tool for managing devices',
    author='Ferenc Nandor Janky & Attila Gombos',
    author_email='info@effective-range.com',
    packages=['inventory', 'plugin'],
    data_files=[
        ('configuration', ['ansible.cfg', 'configuration/ssdpPlugin.json']),
        ('plugin', ['plugin/ssdpPlugin.py']),
        ('playbooks', glob('playbooks/*')),
    ],
    install_requires=[
        'ansible',
        'ssdpy',
        'python-context-logger@git+https://github.com/EffectiveRange/python-context-logger.git@latest',
    ],
)
