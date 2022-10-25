"""
Copyright (C) 2022 Anonymised
"""
from abc import abstractmethod
from typing import List, Tuple

import numpy as np
from causalscbench.models.training_regimes import TrainingRegime


class AbstractInferenceModel(object):
    @abstractmethod
    def __call__(
        self,
        expression_matrix: np.array,
        interventions: List[str],
        gene_names: List[str],
        training_regime: TrainingRegime,
        seed: int = 0
    ) -> List[Tuple]:
        """
        Learn a GRN causal network given single cell expression data.

        Args:
            expression_matrix: a numpy matrix of expression data of size [nb_samples, nb_genes]
            interventions: a list of size [nb_samples] that indicates which gene has been perturb. "non-targeting" means no gene has been perturbed (observational data)
            gene_names: name of the genes in the expression matrix
            training_regime: indicates in which training regime we are (either fully observational, partially intervened or fully intervened)
            seed: randomness seed for reproducibility
        Returns:
            A list of pairs of gene (from gene_names). (A, B) means that there is an edge from A to B in the inferred network

        """
        raise NotImplementedError()
