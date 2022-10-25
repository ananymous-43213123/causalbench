"""
Copyright (C) 2022 Anonymised
"""
import enum


class TrainingRegime(enum.Enum):
    Observational = "observational"
    PartialIntervational = "partial_interventional"
    Interventional = "interventional"

