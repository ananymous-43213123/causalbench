"""
Copyright (C) 2022 Anonymised
"""
import os

import gdown


def download_if_not_exist(url, output_directory, filename):
    path = os.path.join(output_directory, filename)
    if not os.path.exists(path):
        gdown.download(url, path, quiet=False)
    return path
    