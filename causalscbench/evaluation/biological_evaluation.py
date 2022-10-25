"""
Copyright (C) 2022 Anonymised
"""
from typing import Dict, List, Set, Tuple

import numpy as np
from causalscbench.models.training_regimes import TrainingRegime


class Evaluator(object):
    def __init__(self, ground_truth_subnetwork: Set[Tuple[str]]) -> None:
        """
        Evaluation module to biologically evaluate a network using ground-truth biological data.

        Args:
            ground_truth_subnetwork: list of know gene-gene interactions
        """
        self.ground_truth_subnetwork = ground_truth_subnetwork

    def __call__(
        self,
        expression_matrix: np.array,
        interventions: List[str],
        gene_names: List[str],
        training_regime: TrainingRegime,
        seed: int = 0,
    ) -> List[Tuple]:
        edges = set()
        gene_names = set(gene_names)
        for i, j in self.ground_truth_subnetwork:
            if i in gene_names and j in gene_names:
                edges.add((i, j))
        return list(edges)

    def evaluate_network(self, network: List[Tuple]) -> Dict:
        true_positives = 0
        for edge in network:
            if edge in self.ground_truth_subnetwork:
                true_positives += 1
        return {
            "true_positives": true_positives,
        }
