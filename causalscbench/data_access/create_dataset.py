"""
Copyright (C) 2022 Anonymised
"""
import os
from typing import Tuple

import numpy as np
from causalscbench.data_access.datasets import download_weissmann
from causalscbench.data_access.utils import preprocessing


class CreateDataset:
    """Download and create the necessary dataset.

    Parameters
    ----------
    data_directory : path to directory where to store the data.
    """

    def __init__(self, data_directory: str):
        self.data_directory = data_directory

    def save(self, dataset, filename: str) -> str:
        output_path = os.path.join(self.data_directory, filename + ".npz")
        if not os.path.exists(output_path):
            with open(output_path, "w") as file:
                np.savez(
                    file,
                    expression_matrix=dataset[0],
                    var_names=dataset[1],
                    interventions=dataset[2],
                )
        return output_path

    def load(self) -> Tuple[str, str]:
        path_k562 = download_weissmann.download_weissmann_k562(self.data_directory)
        path_rpe1 = download_weissmann.download_weissmann_rpe1(self.data_directory)
        dataset_k562 = preprocessing.preprocess_dataset(path_k562)
        output_path_k562 = self.save(dataset_k562, "dataset_k562")
        dataset_rpe1 = preprocessing.preprocess_dataset(path_rpe1)
        output_path_rpe1 = self.save(dataset_rpe1, "dataset_rpe1")

        return output_path_k562, output_path_rpe1
