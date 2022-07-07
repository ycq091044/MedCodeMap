import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MedCode",
    version="1.1",
    author="Chaoqi Yang",
    author_email="chaoqiy2@illinois.edu",
    description="A package for medical code mapping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ycq091044/MedCode",
    packages=setuptools.find_packages(),
    install_requires=['networkx', 'pandas'],
    entry_points={
        'console_scripts': [
            'MedCode=MedCode:MedCode'
        ],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)