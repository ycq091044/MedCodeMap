from itertools import combinations
import networkx as nx
import pandas as pd
import time
from urllib import request
import sys
import os

__version__ = "1.2"

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
    >> tool.load()
    >> tool.RXCUI_to_SMILES['312055']

    >> tool.add_new_code('RxNorm')
    >> tool.RXCUI_to_RxNorm['312055']
"""

def MedCode():
    print (README)
    
class CodeMapping:
    def __init__(self, *Codes):
        self.Codes = list(Codes)
        # codes Graph
        self.G = nx.Graph()

        if not os.path.exists('./data'):
            os.makedirs('./data')
        
    def load(self):
        tic = time.time()
        print ("----- preparing code mappings -----")
        # NDC, RXCUI, ATC4
        self.load_RXCUI2atc4()
        # RxNorm, RXCUI
        self.load_rxnorm2RXCUI()
        # Name, SMILES
        self.load_drugbank()
        # RxNorm, Name
        self.load_RxNorm2Name()
        # create fully connected graph of Codes (as nodes)
        self.fully_connected_codes()
        print ('load time: {}s'.format(time.time() - tic))
        print ("-----------------------------------------")
        
        
    def load_drugbank(self):
        if not os.path.exists('./data/name2SMILES.csv'):
            name2SMILES = pd.read_csv(request.urlopen('https://drive.google.com/uc?id=199i8mP2gMQNhwUe-2ZNmIr5fhiBbzVlK'))
            name2SMILES.to_csv('./data/name2SMILES.csv', index=False)
            print ('source loaded from https://drive.google.com/uc?id=199i8mP2gMQNhwUe-2ZNmIr5fhiBbzVlK')
        else:
            name2SMILES = pd.read_csv('./data/name2SMILES.csv')
            print ('source loaded from ./data cache')
        self.Name_to_SMILES = self.mapping_from_pd(name2SMILES, 'name', 'moldb_smiles')
        self.G.add_edge('Name', 'SMILES')
    
    def load_RxNorm2Name(self):
        if not os.path.exists('./data/RxNorm2Name.csv'):
            RxNorm2Name = pd.read_csv(request.urlopen('https://drive.google.com/uc?id=1Z11J4st1sI44jPborls9jIxzcpF-GpGt'))
            RxNorm2Name.to_csv('./data/RxNorm2Name.csv', index=False)
            print ('source loaded from https://drive.google.com/uc?id=1Z11J4st1sI44jPborls9jIxzcpF-GpGt')
        else:
            RxNorm2Name = pd.read_csv('./data/RxNorm2Name.csv')
            print ('source loaded from ./data cache')
        self.RxNorm_to_Name = self.mapping_from_pd(RxNorm2Name, 'RxNorm', 'Name')
        self.G.add_edge('RxNorm', 'Name')
        
    def load_RXCUI2atc4(self):
        if not os.path.exists('./data/RXCUI2atc4.csv'):
            RXCUI2atc4 = pd.read_csv(request.urlopen('https://drive.google.com/uc?id=1I2G6fsBDXDiAK95qFWwtnl3Ib2MaLeCx'))
            RXCUI2atc4.to_csv('./data/RXCUI2atc4.csv', index=False)
            print ('source loaded from https://drive.google.com/uc?id=1I2G6fsBDXDiAK95qFWwtnl3Ib2MaLeCx')
        else:
            RXCUI2atc4 = pd.read_csv('./data/RXCUI2atc4.csv')
            print ('source loaded from ./data cache')
        Codes = ['NDC', 'RXCUI', 'ATC4']
        for code1, code2 in combinations(Codes, 2):
            exec("self.{0}_to_{1} = self.mapping_from_pd(RXCUI2atc4, '{0}', '{1}')".format(code1, code2))
            self.G.add_edge(code1, code2)

    def load_rxnorm2RXCUI(self):
        if not os.path.exists('./data/rxnorm2RXCUI.txt'):
            respond = request.urlopen('https://drive.google.com/uc?id=1d2HzsByXrPadvjaKDOEaOt78OkAZOrjC')
            self.RxNorm2RXCUI = eval(respond.read())
            with open('./data/rxnorm2RXCUI.txt', 'w') as outfile:
                print (self.RxNorm2RXCUI, file=outfile)
            print ('source loaded from https://drive.google.com/uc?id=1d2HzsByXrPadvjaKDOEaOt78OkAZOrjC')
        else:
            infile = open('./data/rxnorm2RXCUI.txt', 'r')
            self.RxNorm2RXCUI = eval(infile.read())
            print ('source loaded from ./data cache')
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
            self.add_mapping(code1, code2)
            self.add_mapping(code2, code1)

    def add_mapping(self, code1, code2):
        if code1 != 'SMILES':
            if not hasattr(self, "{}_to_{}".format(code1, code2)):
                if hasattr(self, "{}_to_{}".format(code2, code1)):
                    exec("self.{0}_to_{1} = self.mapping_reverse_dict(self.{1}_to_{0})".format(code1, code2))
                else:
                    for path in nx.all_simple_paths(self.G, source=code1, target=code2):
                        key = path[0]
                        for i in range(len(path) - 2):
                            mid, value = path[i+1: i+3]
                            self.map_combine(key, mid, value)
                    self.G.add_edge(key, value)
            print ("mapping finished: {} -> {}".format(code1, code2))
                
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
        code_pairs = [(new_code, code) for code in self.Codes if code != new_code]
        for code1, code2 in code_pairs:
            if code2 == code1: continue
            self.add_mapping(code1, code2)
            self.add_mapping(code2, code1)
        self.Codes.append(new_code)