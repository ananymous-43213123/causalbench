"""
Copyright (C) 2022 Anonymised
"""
import random
from re import A
from typing import List, Tuple

import numpy as np
from causalscbench.models.abstract_model import AbstractInferenceModel
from causalscbench.models.training_regimes import TrainingRegime


class RandomWithSize(AbstractInferenceModel):
    def __init__(self, size) -> None:
        super().__init__()
        self.size = size

    def __call__(
        self,
        expression_matrix: np.array,
        interventions: List[str],
        gene_names: List[str],
        training_regime: TrainingRegime,
        seed: int = 0,
    ) -> List[Tuple]:
        random.seed(seed)
        edges = set()
        while len(edges) < self.size:
            pair = random.sample(range(len(gene_names)), 2)
            edges.add((gene_names[pair[0]], gene_names[pair[1]]))
        return list(edges)


class FullyConnected(AbstractInferenceModel):
    def __init__(self) -> None:
        super().__init__()

    def __call__(
        self,
        expression_matrix: np.array,
        interventions: List[str],
        gene_names: List[str],
        training_regime: TrainingRegime,
        seed: int = 0,
    ) -> List[Tuple]:
        random.seed(seed)
        edges = set()
        for i in range(len(gene_names)):
            a = gene_names[i]
            for j in range(i + 1, len(gene_names)):
                b = gene_names[j]
                edges.add((a, b))
                edges.add((b, a))
        return list(edges)
