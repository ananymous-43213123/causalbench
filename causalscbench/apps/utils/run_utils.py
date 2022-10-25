"""
Copyright (C) 2022 Anonymised
"""
import os
import random


def create_experiment_folder(exp_id, output_directory):
    if exp_id == "":
        exists = True
        while exists:
            exp_id = "".join(["{}".format(random.randint(0, 9)) for _ in range(0, 6)])
            exists = os.path.exists(os.path.join(output_directory, exp_id))
    output_dir = os.path.join(output_directory, exp_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir
