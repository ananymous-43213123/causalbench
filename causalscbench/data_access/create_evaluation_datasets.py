"""
Copyright (C) 2022 Anonymised
"""
from typing import Set, Tuple

import pandas as pd
from causalscbench.data_access.create_name_to_ensembl_map import \
    GeneNameMapLoader
from causalscbench.data_access.datasets import download_evaluation_files


class CreateEvaluationDatasets:
    """Download and create the evaluation datasets from CORUM and ligand-receptor pairs.

    Parameters
    ----------
    data_directory : path to directory where to store the data.
    """

    def __init__(self, data_directory: str):
        self.data_directory = data_directory

    def _load_corum(self) -> Set[Tuple[str]]:
        map_name_to_ensembl = GeneNameMapLoader(self.data_directory).load()
        path_corum = download_evaluation_files.download_corum(self.data_directory)
        df = pd.read_csv(
            path_corum,
            index_col="subunits(Gene name)",
            sep="\t",
            compression="zip",
        )
        row_names = df.index.values.tolist()
        gene_from, gene_to = [], []
        for row_name in row_names:
            complex_members = row_name.split(";")
            complex_members = [
                map_name_to_ensembl.get(gene)
                for gene in complex_members
                if gene in map_name_to_ensembl
            ]
            for i in range(len(complex_members)):
                for other in complex_members[:i] + complex_members[i + 1 :]:
                    gene_to.append(other)
                    gene_from.append(complex_members[i])
        dataset_corum = set(zip(gene_from, gene_to))
        return dataset_corum

    def _load_lr_pairs(self) -> Set[Tuple[str]]:
        path_lr_pairs = download_evaluation_files.download_ligand_receptor_pairs(
            self.data_directory
        )
        df = pd.read_csv(path_lr_pairs, index_col="ligand_gene_symbol", sep="\t")
        dataset_lr = set()
        for row in df[["ligand_ensembl_gene_id", "receptor_ensembl_gene_id"]].values:
            if not pd.isna(row[0]) and not pd.isna(row[1]):
                dataset_lr.add((row[0], row[1]))
                dataset_lr.add((row[1], row[0]))
        return dataset_lr

    def _load_string_pairs(self) -> Tuple[Set[Tuple[str]], Set[Tuple[str]]]:
        path_string_network_pairs = download_evaluation_files.download_string_network(
            self.data_directory
        )
        path_string_physical_pairs = download_evaluation_files.download_string_physical(
            self.data_directory
        )
        filename_info = download_evaluation_files.download_string_protein_info(
            self.data_directory
        )
        info = pd.read_csv(filename_info, sep="\t", compression="gzip")
        protein_id_to_gene_name = dict()
        for gene_name, string_id in info[["preferred_name", "#string_protein_id"]].to_numpy():
            protein_id_to_gene_name[string_id] = gene_name
        df1 = pd.read_csv(path_string_network_pairs, sep=" ", compression="gzip")
        df2 = pd.read_csv(path_string_physical_pairs, sep=" ", compression="gzip")
        map_name_to_ensembl = GeneNameMapLoader(self.data_directory).load()
        def create_dataset(df):
            dataset_string = set()
            for row in df[["protein1", "protein2"]].values:
                prot1, prot2 = row
                prot1, prot2 = protein_id_to_gene_name[prot1], protein_id_to_gene_name[prot2]
                if prot1 in map_name_to_ensembl and prot2 in map_name_to_ensembl:
                    prot1, prot2 = map_name_to_ensembl[prot1], map_name_to_ensembl[prot2] 
                    dataset_string.add((prot1, prot2))
                    dataset_string.add((prot2, prot1))
            return dataset_string
        return create_dataset(df1), create_dataset(df2)

    def load(self) -> Tuple[Set[Tuple[str]], Set[Tuple[str]], Set[Tuple[str]], Set[Tuple[str]]]:
        dataset_string_network, dataset_string_physical = self._load_string_pairs()
        return self._load_corum(), self._load_lr_pairs(), dataset_string_network, dataset_string_physical
