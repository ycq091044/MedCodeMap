# MedCode: Medication Code Mapping Tool

There are many medication/drug taxonomy systems, such as RxNorm, NDC, ATC. I feel it time-consuming and very confusing to map codes between two different systems during working on this **drug recommendation project** https://github.com/ycq091044/SafeDrug. Sometimes, the code mapping resources cannot be accessible as well. To help others onboarding, here we go!

This python package provides an easy-to-use medication code mapping tool. Within the supported drug coding systems, **it provides easy functions to map from one coding system to another coding system**. Currently, we support the following drug coding systems
- ```NDC```: the National Drug Codes system
- ```RXCUI```: RxNorm concept unique identifier
- ```ATC4```: Anatomical Therapeutic Chemical code level-4
- ```RxNorm```: a second vocabulary for prescription drugs
- ```Name```: drug string-based name, e.g., Lorazepam
- ```SMILES```: drug smiles string

For any given combination of coding systems, we will provide the mapping functions. For example
- User Input: ```NDC```, ```RXCUI```, ```ATC4```
- Output Python Dictionary Object
    - ```NDC_to_RXCUI```, ```NDC_to_ATC4```, ```RXCUI_to_NDC```, ```RXCUI_to_ATC4```, ```ATC4_to_NDC```, ```ATC4_to_RXCUI```
---
## 1. Package Installation

```bash
# get from PyPI
$ pip install MedCode
```
```bash
# local installation
$ cd ~/MedCode
$ pip3 install dist/MedCode-0.1-py3-none-any.whl
```
To look up for help, directly type "MedCode" in the cmd and the help message will pop up.
```bash
$ MedCode
```
## 2. Quick Usage
```python
from MedCode import CodeMapping
# initialize with a list of supported coding systems
tool = CodeMapping('NDC', 'RXCUI', 'Name', 'SMILES')
tool.load_mapping()

# we are good to go, e.g.,
tool.RXCUI_to_SMILES['312055']
tool.NDC_to_Name['76413-153-06']
...
```
- check ```test/Example.ipynb``` for examples.
- **Implementation Features --- Minimal Computation.** The tool will require minimum computation cost for generating all necessary combinations within the listed coding systems, and other mapping functions will not be generated. For example, in this demo, ```NDC_to_RxNorm``` will not be accessible since ```RxNorm``` is not listed in the user input. Our minimal cost computation relies on that we maintain a graph structure of the listed coding systems and use shortest path method to find the missing mapping.


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
