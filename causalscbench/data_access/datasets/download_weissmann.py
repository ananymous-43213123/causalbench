"""
Copyright (C) 2022 Anonymised
"""
from causalscbench.data_access.utils import download


def download_weissmann_k562(output_directory):
    URL = "https://plus.figshare.com/ndownloader/files/35773219"
    filename = "k562.h5ad"
    path = download.download_if_not_exist(URL, output_directory, filename)
    return path

def download_weissmann_rpe1(output_directory):
    URL = "https://plus.figshare.com/ndownloader/files/35775606"
    filename = "rpe1.h5ad"
    path = download.download_if_not_exist(URL, output_directory, filename)
    return path
