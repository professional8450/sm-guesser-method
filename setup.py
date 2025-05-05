from setuptools import find_packages, setup

setup(
    name='soundmapsolver',
    packages=find_packages(),
    version='1.2.3',
    description='A solver for Soundmap Artist Guesser',
    author='cestovatel',
    install_requires=[  
        'rich',
        'pyperclip',
        'pygame',
        'requests'
    ],
    python_requires='>=3.13', 
)
