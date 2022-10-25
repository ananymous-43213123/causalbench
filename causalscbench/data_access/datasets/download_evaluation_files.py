"""
Copyright (C) 2022 Anonymised
"""
from causalscbench.data_access.utils import download


def download_corum(output_directory):
    URL = "https://mips.helmholtz-muenchen.de/corum/download/releases/current/humanComplexes.txt.zip"
    filename = "corum_complexes.txt.zip"
    path = download.download_if_not_exist(URL, output_directory, filename)
    return path


def download_ligand_receptor_pairs(output_directory):
    URL = "https://raw.githubusercontent.com/LewisLabUCSD/Ligand-Receptor-Pairs/ba44c3c4b4a3e501667309dd9ce7208501aeb961/Human/Human-2020-Shao-LR-pairs.txt"
    filename = "human_lr_pair.txt"
    path = download.download_if_not_exist(URL, output_directory, filename)
    return path


def download_string_network(output_directory):
    URL = "https://stringdb-static.org/download/protein.links.detailed.v11.5/9606.protein.links.detailed.v11.5.txt.gz"
    filename = "protein.links.txt.gz"
    path = download.download_if_not_exist(URL, output_directory, filename)
    return path


def download_string_physical(output_directory):
    URL = "https://stringdb-static.org/download/protein.physical.links.detailed.v11.5/9606.protein.physical.links.detailed.v11.5.txt.gz"
    filename = "protein.physical.links.txt.gz"
    path = download.download_if_not_exist(URL, output_directory, filename)
    return path


def download_string_protein_info(output_directory):
    URL = "https://stringdb-static.org/download/protein.info.v11.5/9606.protein.info.v11.5.txt.gz"
    filename = "protein.info.txt.gz"
    path = download.download_if_not_exist(URL, output_directory, filename)
    return path
