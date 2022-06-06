from itertools import combinations
import networkx as nx
import pandas as pd
import time
from urllib import request
import sys

# README
README = """
---------------------------- Help ---------------------------
Chaoqi Yang @ UIUC, chaoqiy2@illinois.edu
-------------------------------------------------------------
MedCode is a python package for supporting medical code mapping,
including:
- NDC: the National Drug Codes system
- RXCUI: RxNorm concept unique identifier
- ATC4: Anatomical Therapeutic Chemical code level-4
- RxNorm: a second vocabulary for prescription drugs
- Name: drug name, e.g., Lorazepam
- SMILES: drug smiles string

INPUT:
    - a list of code, e.g., 'NDC', 'RXCUI', 'Name', 'SMILES'
OUTPUT:
    - any code combination of mapping: tool.[code1]_to_[code2], e.g., tool.RXCUI_to_SMILES
        - code1 and code2 are from the inputed list
        - key: one item from code1 system
        - value: a list of items from code2 system
        - we do not support tool.SMILES_to_[code], since it is meaningless

EXAMPLE:
    >> from MedCode import CodeMapping
    >> tool = CodeMapping('NDC', 'RXCUI', 'Name', 'SMILES')
    >> tool.load_mapping()
    >> tool.RXCUI_to_SMILES['312055']
"""

def MedCode():
    print (README)
    
class CodeMapping:
    def __init__(self, *Codes):
        self.Codes = Codes
        # codes Graph
        self.G = nx.Graph()
        
    def load_mapping(self):
        tic = time.time()
        print ("----- preparing code mappings -----")
        # NDC, RXCUI, ATC4
        self.load_RXCUI2atc4()
        print ('source 1 loaded from https://drive.google.com/uc?id=1I2G6fsBDXDiAK95qFWwtnl3Ib2MaLeCx')
        # RxNorm, RXCUI
        self.load_rxnorm2RXCUI()
        print ('source 2 loaded from https://drive.google.com/uc?id=1d2HzsByXrPadvjaKDOEaOt78OkAZOrjC')
        # Name, SMILES
        self.load_drugbank()
        print ('source 3 loaded from https://drive.google.com/uc?id=199i8mP2gMQNhwUe-2ZNmIr5fhiBbzVlK')
        # RxNorm, Name
        self.load_RxNorm2Name()
        print ('source 4 loaded from https://drive.google.com/uc?id=1Z11J4st1sI44jPborls9jIxzcpF-GpGt')
        # create fully connected graph of Codes (as nodes)
        self.fully_connected_codes()
        print ('load time: {}s'.format(time.time() - tic))
        print ("-----------------------------------------")
        
        
    def load_drugbank(self):
        name2SMILES = pd.read_csv(request.urlopen('https://drive.google.com/uc?id=199i8mP2gMQNhwUe-2ZNmIr5fhiBbzVlK'))
        self.Name_to_SMILES = self.mapping_from_pd(name2SMILES, 'name', 'moldb_smiles')
        self.G.add_edge('Name', 'SMILES')
    
    def load_RxNorm2Name(self):
        RxNorm2Name = pd.read_csv(request.urlopen('https://drive.google.com/uc?id=1Z11J4st1sI44jPborls9jIxzcpF-GpGt'))
        self.RxNorm_to_Name = self.mapping_from_pd(RxNorm2Name, 'RxNorm', 'Name')
        self.G.add_edge('RxNorm', 'Name')
        
    def load_RXCUI2atc4(self):
        RXCUI2atc4 = pd.read_csv(request.urlopen('https://drive.google.com/uc?id=1I2G6fsBDXDiAK95qFWwtnl3Ib2MaLeCx'))
        Codes = ['NDC', 'RXCUI', 'ATC4']
        for code1, code2 in combinations(Codes, 2):
            exec("self.{0}_to_{1} = self.mapping_from_pd(RXCUI2atc4, '{0}', '{1}')".format(code1, code2))
            self.G.add_edge(code1, code2)
    
    def load_rxnorm2RXCUI(self):
        respond = request.urlopen('https://drive.google.com/uc?id=1d2HzsByXrPadvjaKDOEaOt78OkAZOrjC')
        self.RxNorm2RXCUI = eval(respond.read())
        self.RxNorm_to_RXCUI = {k: [v] for k, v in self.RxNorm2RXCUI.items()}
        self.G.add_edge('RxNorm', 'RXCUI')
        
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
        for k, v in file[[col1, col2]].astype('str').values:
            if k not in Dict:
                Dict[k] = [v]
            elif v in Dict[k]:
                continue
            else:
                Dict[k].append(v)
        return Dict
    
    def fully_connected_codes(self):
        for code1, code2 in combinations(self.Codes, 2):
            if code1 != 'SMILES':
                if not hasattr(self, "{}_to_{}".format(code1, code2)):
                    if hasattr(self, "{}_to_{}".format(code2, code1)):
                        exec("self.{0}_to_{1} = self.mapping_reverse_dict(self.{1}_to_{0})".format(code1, code2))
                    else:
                        shortest_path = nx.shortest_path(self.G, source=code1, target=code2)
                        key = shortest_path[0]
                        for i in range(len(shortest_path) - 2):
                            mid, value = shortest_path[i+1: i+3]
                            self.map_combine(key, mid, value)
                            self.G.add_edge(key, value)
                print ("mapping finished: {} -> {}".format(code1, code2))
            
            if code2 != 'SMILES':
                if not hasattr(self, "{}_to_{}".format(code2, code1)) and (code2 != 'SMILES'):
                    exec("self.{0}_to_{1} = self.mapping_reverse_dict(self.{1}_to_{0})".format(code2, code1))
                print ("mapping finished: {} -> {}".format(code2, code1))
                
                    
    def map_combine(self, key, mid, value):
        
        if hasattr(self, "{}_to_{}".format(key, mid)):
            Dict1 = eval("self.{}_to_{}".format(key, mid))
        else:
            exec("self.{0}_to_{1} = self.mapping_reverse_dict(self.{1}_to_{0})".format(key, mid))
            Dict1 = eval("self.{}_to_{}".format(key, mid))
            
        if hasattr(self, "{}_to_{}".format(mid, value)):
            Dict2 = eval("self.{}_to_{}".format(mid, value))
        else:
            exec("self.{0}_to_{1} = self.mapping_reverse_dict(self.{1}_to_{0})".format(mid, value))
            Dict2 = eval("self.{}_to_{}".format(mid, value))
            
        exec("self.{}_to_{} = dict()".format(key, value))
        for k, m in Dict1.items():
            temp = []
            for m_item in m:
                if m_item in Dict2:
                    temp += Dict2[m_item]
            if len(temp) > 1:
                exec("self.{}_to_{}[k] = list(set(temp))".format(key, value))