import os
import re

import pandas as pd

from MedCode.code.base import BaseCode
from MedCode.utils import cache_path


class ICD9Proc(BaseCode):
    pass


def prepare_icd9proc():
    """ https://bioportal.bioontology.org/ontologies/ICD9CM """
    raw_data = pd.read_csv(os.path.join(cache_path, "ICD9CM.csv"))
    raw_data["code"] = raw_data["Class ID"].apply(lambda x: x.split("/")[-1])
    raw_data["vocab"] = raw_data["Class ID"].apply(lambda x: x.split("/")[-2])
    raw_data["name"] = raw_data["Preferred Label"]
    raw_data["parent_code"] = raw_data["Parents"].apply(lambda x: x.split("/")[-1] if not pd.isna(x) else "")
    raw_data["parent_vocab"] = raw_data["Parents"].apply(lambda x: x.split("/")[-2] if not pd.isna(x) else "")
    # exclude non icd9 codes
    raw_data = raw_data[raw_data.vocab == "ICD9CM"]
    raw_data = raw_data[raw_data.parent_vocab == "ICD9CM"]
    # exclude icd9cm codes
    # icd9cm codes: 001-999.99, icd9proc: 00.00-99.99
    raw_data = raw_data[raw_data.code.apply(lambda x: len(re.split("\.|-", x)[0]) <= 2)]
    data = raw_data[["code", "name", "parent_code"]].set_index("code").to_dict("index")
    return data


if __name__ == "__main__":
    import networkx as nx

    data = prepare_icd9proc()
    print(len(data))
    icd9proc = ICD9Proc(data)
    print(len(icd9proc.graph.nodes))
    print(len(icd9proc.graph.edges))
    print(icd9proc.graph.nodes['84.66'])
    print(nx.ancestors(icd9proc.graph, '84.66'))
