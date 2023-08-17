import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MedCodeMap",
    version="1.3",
    author="Chaoqi Yang",
    author_email="chaoqiy2@illinois.edu",
    description="A package for medical code mapping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ycq091044/MedCodeMap",
    packages=setuptools.find_packages(),
    install_requires=["networkx", "pandas"],
    entry_points={
        "console_scripts": ["MedCodeMap=MedCodeMap:MedCodeMap"],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
