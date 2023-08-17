import os
import time
from itertools import combinations
from pathlib import Path
from urllib import request

import networkx as nx
import pandas as pd

__version__ = "1.3"

# README
README = """
---------------------------- Help ---------------------------
Chaoqi Yang @ UIUC, chaoqiy2@illinois.edu
-------------------------------------------------------------
MedCodeMap is a python package for supporting medical code mapping,
including:
- NDC10: the National Drug Codes system, 10-digit version
- NDC11: the National Drug Codes system, 11-digit version
- RXCUI: RxNorm concept unique identifier
- ATC4: Anatomical Therapeutic Chemical code level-4
- Name: drug name, e.g., Lorazepam
- SMILES: drug smiles string

INPUT:
    - a list of code, e.g., 'NDC10', 'NDC11', 'RXCUI', 'Name', 'SMILES'
OUTPUT:
    - any code combination of mapping: tool.[code1]_to_[code2], e.g., tool.RXCUI_to_SMILES
        - code1 and code2 are from the inputed list
        - key: one item from code1 system
        - value: a list of items from code2 system
        - we do not support tool.SMILES_to_[code], since it is meaningless

EXAMPLE:
    >> from MedCodeMap import CodeMapping
    >> tool = CodeMapping('NDC10', 'RXCUI', 'Name', 'SMILES')
    >> tool.load()
    >> tool.RXCUI_to_SMILES['312055']

    >> tool.add_new_code('NDC11')
    >> tool.RXCUI_to_NDC11['312055']
"""


def MedCodeMap():
    print(README)


class CodeMapping:
    def __init__(self, *Codes):
        self.Codes = list(Codes)
        # codes Graph
        self.G = nx.Graph()

        self.path = os.path.join(str(Path.home()), ".cache/medcode/")
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def load(self):
        tic = time.time()
        print("----- preparing code mappings -----")
        # NDC10, RXCUI, ATC4
        self.load_NDC102RXCUI2atc4()
        # NDC11, RXCUI
        self.load_NDC112RXCUI()
        # Name, SMILES
        self.load_drugbank()
        # NDC11, Name
        self.load_NDC112Name()
        # create fully connected graph of Codes (as nodes)
        self.fully_connected_codes()
        print("load time: {}s".format(time.time() - tic))
        print("-----------------------------------------")

    def load_drugbank(self):
        if not os.path.exists(f"{self.path}/name2SMILES.csv"):
            name2SMILES = pd.read_csv(
                request.urlopen(
                    "https://drive.google.com/uc?id=199i8mP2gMQNhwUe-2ZNmIr5fhiBbzVlK"
                )
            )
            name2SMILES.to_csv(f"{self.path}/name2SMILES.csv", index=False)
            print(
                "source loaded from https://drive.google.com/uc?id=199i8mP2gMQNhwUe-2ZNmIr5fhiBbzVlK"
            )
        else:
            name2SMILES = pd.read_csv(f"{self.path}/name2SMILES.csv")
            print(f"source loaded from {self.path} cache")
        self.Name_to_SMILES = self.mapping_from_pd(
            name2SMILES, "name", "moldb_smiles")
        self.G.add_edge("Name", "SMILES")

    def load_NDC112Name(self):
        if not os.path.exists(f"{self.path}/NDC112Name.csv"):
            NDC112Name = pd.read_csv(
                request.urlopen(
                    "https://drive.google.com/uc?id=1Z11J4st1sI44jPborls9jIxzcpF-GpGt"
                ),
                dtype={"NDC11": str, "Name": str},
            )
            NDC112Name.to_csv(f"{self.path}/NDC112Name.csv", index=False)
            # print ('source loaded from https://drive.google.com/uc?id=1Z11J4st1sI44jPborls9jIxzcpF-GpGt')
        else:
            NDC112Name = pd.read_csv(
                f"{self.path}/NDC112Name.csv", dtype={"NDC11": str, "Name": str}
            )
            # print ('source loaded from ./data cache')
        self.NDC11_to_Name = self.mapping_from_pd(NDC112Name, "NDC11", "Name")
        self.G.add_edge("NDC11", "Name")

    def load_NDC102RXCUI2atc4(self):
        if not os.path.exists(f"{self.path}/NDC102RXCUI2atc4.csv"):
            NDC102RXCUI2atc4 = pd.read_csv(
                request.urlopen(
                    "https://drive.google.com/uc?id=1I2G6fsBDXDiAK95qFWwtnl3Ib2MaLeCx"
                ),
                dtype={"NDC10": str, "RXCUI": str, "ATC4": str},
            )
            NDC102RXCUI2atc4.to_csv(
                f"{self.path}/NDC102RXCUI2atc4.csv", index=False)
            # print ('source loaded from https://drive.google.com/uc?id=1I2G6fsBDXDiAK95qFWwtnl3Ib2MaLeCx')
        else:
            NDC102RXCUI2atc4 = pd.read_csv(
                f"{self.path}/NDC102RXCUI2atc4.csv",
                dtype={"NDC10": str, "RXCUI": str, "ATC4": str},
            )
            # print ('source loaded from ./data cache')
        Codes = ["NDC10", "RXCUI", "ATC4"]
        for code1, code2 in combinations(Codes, 2):
            exec(
                "self.{0}_to_{1} = self.mapping_from_pd(NDC102RXCUI2atc4, '{0}', '{1}')".format(
                    code1, code2
                )
            )
            self.G.add_edge(code1, code2)

    def load_NDC112RXCUI(self):
        if not os.path.exists(f"{self.path}/NDC112RXCUI.txt"):
            respond = request.urlopen(
                "https://drive.google.com/uc?id=1d2HzsByXrPadvjaKDOEaOt78OkAZOrjC"
            )
            self.NDC112RXCUI = eval(respond.read())
            with open(f"{self.path}/NDC112RXCUI.txt", "w") as outfile:
                print(self.NDC112RXCUI, file=outfile)
            # print ('source loaded from https://drive.google.com/uc?id=1d2HzsByXrPadvjaKDOEaOt78OkAZOrjC')
        else:
            infile = open(f"{self.path}/NDC112RXCUI.txt", "r")
            self.NDC112RXCUI = eval(infile.read())
            # print ('source loaded from ./data cache')
        self.NDC11_to_RXCUI = {k: [v] for k, v in self.NDC112RXCUI.items()}
        self.G.add_edge("NDC11", "RXCUI")

    def mapping_reverse_dict(self, file):
        Dict = {}
        for k, v in file.items():
            for v_item in v:
                if v_item not in Dict:
                    Dict[v_item] = [str(k)]
                elif str(k) in Dict[v_item]:
                    continue
                else:
                    Dict[v_item].append(str(k))
        return Dict

    def mapping_from_pd(self, file, col1, col2):
        Dict = {}
        for k, v in file[[col1, col2]].astype("str").values:
            if k not in Dict:
                Dict[k] = [v]
            elif v in Dict[k]:
                continue
            else:
                Dict[k].append(v)
        return Dict

    def fully_connected_codes(self):
        for code1, code2 in combinations(self.Codes, 2):
            self.add_mapping(code1, code2)
            self.add_mapping(code2, code1)

    def add_mapping(self, code1, code2):
        if code1 != "SMILES":
            if not hasattr(self, "{}_to_{}".format(code1, code2)):
                if hasattr(self, "{}_to_{}".format(code2, code1)):
                    exec(
                        "self.{0}_to_{1} = self.mapping_reverse_dict(self.{1}_to_{0})".format(
                            code1, code2
                        )
                    )
                else:
                    for path in nx.all_simple_paths(self.G, source=code1, target=code2):
                        key = path[0]
                        for i in range(len(path) - 2):
                            mid, value = path[i + 1: i + 3]
                            self.map_combine(key, mid, value)
                    self.G.add_edge(key, value)
            print("mapping finished: {} -> {}".format(code1, code2))

    def map_combine(self, key, mid, value):

        if hasattr(self, "{}_to_{}".format(key, mid)):
            Dict1 = eval("self.{}_to_{}".format(key, mid))
        else:
            exec(
                "self.{0}_to_{1} = self.mapping_reverse_dict(self.{1}_to_{0})".format(
                    key, mid
                )
            )
            Dict1 = eval("self.{}_to_{}".format(key, mid))

        if hasattr(self, "{}_to_{}".format(mid, value)):
            Dict2 = eval("self.{}_to_{}".format(mid, value))
        else:
            exec(
                "self.{0}_to_{1} = self.mapping_reverse_dict(self.{1}_to_{0})".format(
                    mid, value
                )
            )
            Dict2 = eval("self.{}_to_{}".format(mid, value))

        exec("{}_to_{} = dict()".format(key, value))
        # do not delete "k"
        for k, m in Dict1.items():
            temp = []
            for m_item in m:
                if m_item in Dict2:
                    temp += Dict2[m_item]
            if len(temp) > 1:
                exec("{}_to_{}[k] = list(set(temp))".format(key, value))
        if hasattr(self, "{}_to_{}".format(key, value)):
            exec("self.{0}_to_{1}.update({0}_to_{1})".format(key, value))
        else:
            exec("self.{0}_to_{1} = {0}_to_{1}".format(key, value))

    def add_new_code(self, new_code):
        code_pairs = [(new_code, code)
                      for code in self.Codes if code != new_code]
        for code1, code2 in code_pairs:
            if code2 == code1:
                continue
            self.add_mapping(code1, code2)
            self.add_mapping(code2, code1)
        self.Codes.append(new_code)


if __name__ == "__main__":
    tool = CodeMapping("RXCUI", "SMILES")
    tool.load()
    print(tool.RXCUI_to_SMILES["312055"])
