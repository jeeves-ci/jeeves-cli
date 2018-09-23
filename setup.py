from setuptools import setup


setup(
    zip_safe=True,
    name='jeeves-cli',
    version='0.1',
    author='adaml',
    author_email='adam.lavie@gmail.com',
    packages=[
        'jeeves_cli',
        'jeeves_cli.commands',
    ],
    license='LICENSE',
    description='The grand Jeeves CLI.',
    entry_points={
        'console_scripts': [
            'jvc = jeeves_cli.cli:_jvc'
        ]
    },
    install_requires=[
        'click==6.7',
        'docker==2.1',
        'pyyaml==3.13',
    ]
)
