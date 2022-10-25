"""
Copyright (C) 2022 Anonymised
"""
import json
import os

import pandas as pd
import slingpy as sp
from causalscbench.apps.utils.run_utils import create_experiment_folder
from causalscbench.data_access.create_dataset import CreateDataset
from causalscbench.data_access.create_evaluation_datasets import \
    CreateEvaluationDatasets
from causalscbench.data_access.utils.splitting import DatasetSplitter
from causalscbench.evaluation import (biological_evaluation,
                                      statistical_evaluation)
from causalscbench.models import training_regimes
from causalscbench.models.causallearn_models import GES, PC
from causalscbench.models.dcdi_models import DCDI
from causalscbench.models.feature_selection import (
    LassoFeatureSelection, RandomForestFeatureSelection)
from causalscbench.models.gies import GIES
from causalscbench.models.notears import NotearsLin, NotearsMLP
from causalscbench.models.random_network import FullyConnected, RandomWithSize
from causalscbench.models.sparsest_permutations import (
    GreedySparsestPermutation, InterventionalGreedySparsestPermutation)

DATASET_NAMES = [
    "weissmann_k562",
    "weissmann_rpe1",
]

METHODS = [
    "random100",
    "random1000",
    "random10000",
    "fully-connected",
    "lasso",
    "random_forest",
    "ges", 
    "gies",
    "pc", 
    "mvpc"
    "gsp",
    "igsp",
    "notears-lin",
    "notears-lin-sparse",
    "notears-mlp",
    "notears-mlp-sparse",
    "DCDI-G",
    "DCDI-DSF",
    "corum", 
    "lr", 
    "string_network",
    "string_physical"
]

class MainApp:
    def __init__(
        self,
        output_directory: str,
        data_directory: str,
        model_name: str = METHODS[0],
        dataset_name: str = DATASET_NAMES[0],
        model_seed: int = 0,
        training_regime: training_regimes.TrainingRegime = training_regimes.TrainingRegime.Interventional,
        partial_intervention_seed: int = 0,
        fraction_partial_intervention: float = 1.0,
        subset_data: float = 1.0,
        exp_id: str = "",
    ):
        """
        Main full training pipeline.

        Args:
            output_directory (str): Directory for output results
            data_directory (str): Directory to store the datasets
            model_name (str, optional): Which method to run. Defaults to METHODS[0].
            dataset_name (List[str], optional): Which dataset to use. Defaults to DATASET_NAMES[0].
            model_seed (int, optional): Seed for model reproducibility. Defaults to 0.
            training_regime (training_regimes.TrainingRegime, optional): Choice of training regime. Defaults to training_regimes.Interventional.
            partial_intervention_seed (int, optional): If training_regime is partial intervention, seed for random selection of perturbed genes. Defaults to 0.
            fraction_partial_intervention (float, optional):  If training_regime is partial intervention, fraction of genes which should have interventional data. Defaults to 1.0.
            subset_data (float, optional): Option to subset the whole dataset for easier training. Defaults to 1.0.
            exp_id (str, optional): Unique experiment id (6 digit number). Default to randomly generated.
        """
        self.data_directory = data_directory
        self.output_directory = create_experiment_folder(exp_id, output_directory)
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.model_seed = model_seed
        self.training_regime = training_regime
        self.partial_intervention_seed = partial_intervention_seed
        self.fraction_partial_intervention = fraction_partial_intervention
        self.subset_data = subset_data
        self.exp_id = exp_id
        self.model = None
        self.dataset_splitter = None
        self.corum_evaluator = None
        self.lr_evaluator = None
        self.quantitative_evaluator = None

    def load_model(self):
        models_dict = {
            "random100": RandomWithSize(100),
            "random1000": RandomWithSize(1000),
            "random10000": RandomWithSize(10000),
            "fully-connected": FullyConnected(),
            "lasso": LassoFeatureSelection(),
            "random_forest": RandomForestFeatureSelection(),
            "ges": GES(),
            "gies": GIES(),
            "pc": PC(missing_value=False),
            "mvpc": PC(missing_value=True),
            "gsp": GreedySparsestPermutation(),
            "igsp": InterventionalGreedySparsestPermutation(),
            "notears-lin": NotearsLin(lambda1=0.0),
            "notears-lin-sparse": NotearsLin(lambda1=0.01),
            "notears-mlp": NotearsMLP(lambda1=0.0),
            "notears-mlp-sparse": NotearsMLP(lambda1=0.01),
            "DCDI-G": DCDI("DCDI-G"),
            "DCDI-DSF": DCDI("DCDI-DSF"),
            "corum": self.corum_evaluator,
            "lr": self.lr_evaluator,
            "string_network": self.string_network_evaluator,
            "string_physical": self.string_physical_evaluator
        }
        if self.model_name not in METHODS:
            raise NotImplementedError()
        self.model = models_dict[self.model_name]

    def load_data(self):
        path_k562, path_rpe1 = CreateDataset(self.data_directory).load()

        if self.dataset_name == "weissmann_k562":
            self.dataset_splitter = DatasetSplitter(path_k562, self.subset_data)
        elif self.dataset_name == "weissmann_rpe1":
            self.dataset_splitter = DatasetSplitter(path_rpe1, self.subset_data)
        else:
            raise NotImplementedError()

    def load_evaluators(self):
        (
            corum,
            lr_pairs,
            string_network_pairs,
            string_physical_pairs,
        ) = CreateEvaluationDatasets(self.data_directory).load()
        self.corum_evaluator = biological_evaluation.Evaluator(corum)
        self.lr_evaluator = biological_evaluation.Evaluator(lr_pairs)
        self.string_network_evaluator = biological_evaluation.Evaluator(
            string_network_pairs
        )
        self.string_physical_evaluator = biological_evaluation.Evaluator(
            string_physical_pairs
        )
        (
            expression_matrix_test,
            interventions_test,
            gene_names,
        ) = self.dataset_splitter.get_test_data()
        self.quantitative_evaluator = statistical_evaluation.Evaluator(
            expression_matrix_test, interventions_test, gene_names
        )

    def train_and_evaluate(self):
        if self.training_regime == training_regimes.TrainingRegime.Observational:
            (
                expression_matrix_train,
                interventions_train,
                gene_names,
            ) = self.dataset_splitter.get_observational()
        elif (
            self.training_regime == training_regimes.TrainingRegime.PartialIntervational
        ):
            (
                expression_matrix_train,
                interventions_train,
                gene_names,
            ) = self.dataset_splitter.get_partial_interventional(
                self.fraction_partial_intervention, self.partial_intervention_seed
            )
        else:
            (
                expression_matrix_train,
                interventions_train,
                gene_names,
            ) = self.dataset_splitter.get_interventional()
        arguments = {
            "model_name": self.model_name,
            "dataset_name": self.dataset_name,
            "model_seed": self.model_seed,
            "training_regime": self.training_regime.name,
            "partial_intervention_seed": self.partial_intervention_seed,
            "fraction_partial_intervention": self.fraction_partial_intervention,
            "subset_data": self.subset_data,
            "exp_id": self.exp_id,
        }
        with open(os.path.join(self.output_directory, "arguments.json"), "w") as output:
            json.dump(arguments, output)
        output_network = self.model(
            expression_matrix_train,
            interventions_train,
            gene_names,
            self.training_regime,
            self.model_seed,
        )
        corum_evaluation = self.corum_evaluator.evaluate_network(output_network)
        ligand_receptor_evaluation = self.lr_evaluator.evaluate_network(output_network)
        string_network_evaluation = self.string_network_evaluator.evaluate_network(
            output_network
        )
        string_physical_evaluation = self.string_physical_evaluator.evaluate_network(
            output_network
        )
        quantitative_test_evaluation = self.quantitative_evaluator.evaluate_network(
            output_network
        )
        metrics = {
            "corum_evaluation": corum_evaluation,
            "ligand_receptor_evaluation": ligand_receptor_evaluation,
            "quantitative_test_evaluation": quantitative_test_evaluation,
            "string_network_evaluation": string_network_evaluation,
            "string_physical_evaluation": string_physical_evaluation,
        }
        with open(os.path.join(self.output_directory, "metrics.json"), "w") as output:
            json.dump(metrics, output)
        pd.DataFrame(output_network).to_csv(
            os.path.join(self.output_directory, "output_network.csv")
        )

        return metrics

    def run(self):
        self.load_data()
        self.load_evaluators()
        self.load_model()
        self.train_and_evaluate()


def main():
    app = sp.instantiate_from_command_line(MainApp)
    results = app.run()


if __name__ == "__main__":
    main()
