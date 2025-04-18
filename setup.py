from setuptools import find_packages, setup

setup(
    name='soundmapsolver',
    packages=find_packages(),
    version='1.1',
    description='A solver for Soundmap Artist Guesser',
    author='cestovatel',
    install_requires=[  
        'rich',
        'pyperclip'
    ],
    python_requires='>=3.13', 
)
