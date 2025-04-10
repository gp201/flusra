#!/usr/bin/env python3

import pandas as pd
import os
import glob
import argparse


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for merging GenofLu results files.
    This function sets up an ArgumentParser with the following arguments:
        -i, --input_dir (str): Directory containing Genoflu results files.
                               Default is the current directory ".".
        -o, --output_file (str): Name of the output merged TSV file.
                               This argument is required. If the file already exists, new results are appended.
        -e, --existing_file (str): Optional path to an existing TSV file to use for merging.
                               Default is None.
    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(description="Merge GenofLu results files.")
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        default=".",
        help="Directory containing genoflu results files",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        required=True,
        help="Name of the output merged TSV file. If the file already exists, new results are appended.",
    )
    parser.add_argument(
        "-e",
        "--existing_results",
        type=str,
        default=None,
        help="Path to an existing TSV file to use for merging, if provided.",
    )
    return parser.parse_args()


def merge_genoflu_results(input_dir: str, output_file: str, existing_results: str = None):
    """
    Merge genoflu results from multiple TSV files and optionally merge them with an existing file.
    This function looks for files ending in '_stats.tsv' in the specified input directory and loads
    them into pandas DataFrames if they are non-empty. It then concatenates these DataFrames into a single
    result DataFrame. If an existing file is provided and exists, the function filters out any overlapping
    indices from the new data before merging with the existing data. Finally, it writes the merged DataFrame
    to the specified output file in TSV format.
    Parameters:
        input_dir (str): Path to the directory containing '*_stats.tsv' files.
                         Only files that exist and have a non-zero size are considered.
        output_file (str): Path to the file where the merged results will be saved (in TSV format).
        existing_file (str, optional): Path to an existing results file.
                                       If provided and exists, new results (rows with indices not in the existing file)
                                       are merged with the existing data.
    Returns:
        None
    """

    # Construct file pattern using the input directory
    result_files = [
        file
        for file in glob.glob(os.path.join(input_dir, "*_stats.tsv"))
        if os.path.isfile(file) and os.path.getsize(file) > 0
    ]
    if not result_files:
        print(f"No valid result files found in {input_dir}.")
        return

    new_results_df = pd.concat(
        (pd.read_csv(file, sep="\t", index_col=0) for file in result_files),
        axis=0
    )

    if existing_results and os.path.exists(existing_results):
        existing_df = pd.read_csv(existing_results, sep="\t", index_col=0)
        new_idx = new_results_df.index.difference(existing_df.index)
        new_results_df = new_results_df.loc[new_idx]
        merged_results_df = pd.concat([existing_df, new_results_df])
    else:
        merged_results_df = new_results_df

    merged_results_df.to_csv(output_file, sep="\t", index=True, header=True)


def main():
    args = parse_args()
    merge_genoflu_results(
        input_dir=args.input_dir,
        output_file=args.output_file,
        existing_results=args.existing_results,
    )


if __name__ == "__main__":
    main()
