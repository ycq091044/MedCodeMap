# MedCodeMap: Medication Code Mapping Tool

> ### We have renamed the package into "MedCodeMap".

There are many medication/drug taxonomy systems, such as RXCUI, NDC, ATC. I feel it time-consuming and very confusing to map codes between two different systems during working on this **drug recommendation project** https://github.com/ycq091044/SafeDrug. Sometimes, the code mapping resources cannot be accessible as well. To help others onboarding, here we go!

This python package provides an easy-to-use medication code mapping tool. Within the supported drug coding systems, **it provides easy functions to map from one coding system to another coding system**. Currently, we support the following drug coding systems
- ```NDC10```: the National Drug Codes system on 10-digit level
- ```NDC11```: the National Drug Codes system on 11-digit level
- ```RXCUI```: RxNorm concept unique identifier
- ```ATC4```: Anatomical Therapeutic Chemical code level-4
- ```Name```: drug string-based name, e.g., Lorazepam
- ```SMILES```: drug smiles string

For any given combination of coding systems, we will provide the mapping functions. For example
- User Input: ```NDC10```, ```RXCUI```, ```ATC4```
- Output Python Dictionary Object
    - ```NDC10_to_RXCUI```, ```NDC10_to_ATC4```, ```RXCUI_to_NDC10```, ```RXCUI_to_ATC4```, ```ATC4_to_NDC10```, ```ATC4_to_RXCUI```
---
## 1. Package Installation

```bash
# get from PyPI
$ pip install MedCodeMap
```
```bash
# local installation
$ cd ~/MedCodeMap
$ pip3 install dist/MedCodeMap-[VERSION-ID]-py3-none-any.whl
```
To look up for help, directly type "MedCodeMap" in the cmd and the help message will pop up.
```bash
$ MedCodeMap
```
## 2. Quick Usage
### Load all mappings during initialization
```python
from MedCodeMap import CodeMapping
# initialize with a list of supported coding systems
tool = CodeMapping('NDC10', 'RXCUI', 'Name', 'SMILES')
tool.load()

# we are good to go, e.g.,
tool.RXCUI_to_SMILES['312055']
tool.NDC_to_Name['76413-153-06']
...
```
### Want to add more coding systems later?
```python
# add additional coding system
tool.add_new_code("NDC11")

# we are good to go, e.g.,
tool.NDC_to_NDC11['76413-153-06']
```
- check ```test/Example.ipynb``` for examples.
- **Implementation Features --- Minimal Computation.** The tool will require minimum computation cost for generating all necessary combinations within the listed coding systems, and other mapping functions will not be generated. For example, in this demo, ```NDC11_to_RXCUI``` will not be accessible since ```NDC11``` is not listed in the user input (before). Our minimal cost computation relies on that we maintain a graph structure of the listed coding systems and use shortest path method to find the missing mapping.


## 3. Current Data Resources
The current data resources are loaded from Google Drive. We basically borrow the data from
- ```SafeDrug```: https://github.com/ycq091044/SafeDrug/tree/main/data/input
- ```DrugBank```: https://www.dropbox.com/s/angoirabxurjljh/drugbank_drugs_info.csv?dl=0
    
    ```bash
    # Google Drive Link
    https://drive.google.com/uc?id=1I2G6fsBDXDiAK95qFWwtnl3Ib2MaLeCx
    https://drive.google.com/uc?id=1d2HzsByXrPadvjaKDOEaOt78OkAZOrjC
    https://drive.google.com/uc?id=199i8mP2gMQNhwUe-2ZNmIr5fhiBbzVlK
    https://drive.google.com/uc?id=1Z11J4st1sI44jPborls9jIxzcpF-GpGt
    ```

- We are going to integrate more resources for supporting other coding systems, such as SNOMED.
