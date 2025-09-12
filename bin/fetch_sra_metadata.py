#!/usr/bin/env python3

import argparse
import time
import pandas as pd
import xml.etree.ElementTree as ET
from tqdm import tqdm
from Bio import Entrez
import urllib.error
import http.client
import yaml

FIELDS = {
        'Run' : {
            'find' : './/RUN',
            'attrib' : 'accession'
        },
        'Assay Type' : {
            'find' : './/LIBRARY_STRATEGY',
            'text' : True
        },
        'AvgSpotLen' : {
            'find' : './/Statistics/Read[@index="0"]',
            'attrib' : 'average'
        },
        'Bases' : {
            'find' : './/RUN_SET',
            'attrib' : 'bases'
        },
        'BioProject' : {
            'find' : './/EXTERNAL_ID[@namespace="BioProject"]',
            'text' : True
        },
        'BioSample' : {
            'find' : './/EXTERNAL_ID[@namespace="BioSample"]',
            'text' : True
        },
        'BioSample Accession' : {
            'find' : './/SAMPLE_DESCRIPTOR',
            'attrib' : 'accession'
        },
        'BioSampleModel' : {
            'find' : './/SAMPLE_ATTRIBUTE[TAG="BioSampleModel"]/VALUE',
            'text' : True
        },
        'Bytes' : {
            'find' : './/RUN',
            'attrib' : 'size'
        },
        'Center Name' : {
            'find' : './/SUBMISSION',
            'attrib' : 'center_name'
        },
        'Collection_Date' : {
            'find' : './/SAMPLE_ATTRIBUTE[TAG="collection_date"]/VALUE',
            'text' : True
        },
        'Consent' : {
            'find' : './/SRAFile',
            'attrib' : 'cluster'

        },
        'DATASTORE filetype' : {
            'find' : './/CloudFile',
            'attrib' : 'filetype'
        },
        'DATASTORE provider' : {
            'find' : './/CloudFile',
            'attrib' : 'provider'
        },
        'DATASTORE region' : {
            'find' : './/CloudFile',
            'attrib' : 'location'
        },
        'Experiment' : {
            'find' : './/EXPERIMENT',
            'attrib' : 'accession'
        },
        'geo_loc_name_country' : {
            'find' : './/SAMPLE_ATTRIBUTE[TAG="geo_loc_name"]/VALUE',
            'text' : True
        },
        'geo_loc_name_country_continent' : {
            'find' : './/SAMPLE_ATTRIBUTE[TAG="geo_loc_name_country_continent"]/VALUE',
            'default' : 'North America'
        },
        'geo_loc_name' : {
            'find' : './/SAMPLE_ATTRIBUTE[TAG="geo_loc_name"]/VALUE',
            'text' : True
        },
        'Host' : {
            'find' : './/SAMPLE_ATTRIBUTE[TAG="host"]/VALUE',
            'text' : True
        },
        'Instrument' : {
            'find' : './/INSTRUMENT_MODEL',
            'text' : True
        },
        'isolate' : {
            'find' : './/SAMPLE_ATTRIBUTE[TAG="isolate"]/VALUE',
            'text' : True
        },
        'Library Name' : {
            'find' : './/LIBRARY_NAME',
            'text' : True
        },
        'LibraryLayout' : {
            'find' : './/LIBRARY_LAYOUT',
            'text' : False
        },
        'LibrarySelection' : {
            'find' : './/LIBRARY_SELECTION',
            'text' : True
        },
        'LibrarySource' : {
            'find' : './/LIBRARY_SOURCE',
            'text' : True
        },
        'Organism' : {
            'find' : './/SAMPLE_NAME/SCIENTIFIC_NAME',
            'text' : True
        },
        'Platform' : {
            'find' : './/PLATFORM',
            'text' : False
        },
        'ReleaseDate' : {
            'find' : './/RUN',
            'attrib' : 'published'
        },
        'create_date' : {
            'find' : './/SRAFile',
            'attrib' : 'date'
        },
        'version' : {
            'find' : './/SRAFile',
            'attrib' : 'version'
        },
        'Sample Name' : {
            'find' : './/SAMPLE',
            'attrib' : 'alias'
        },
        'SRA Study' : {
            'find' : './/STUDY',
            'attrib' : 'accession'
        },
        'serotype' : {
            'find' : './/SAMPLE_ATTRIBUTE[TAG="serotype"]/VALUE',
            'text' : True
        },
        'isolation_source' : {
            'find' : './/SAMPLE_ATTRIBUTE[TAG="isolation_source"]/VALUE',
            'text' : True
        }
    }


def read_xml_data(xml_data: str) -> pd.DataFrame:
    """
    Parses the provided XML metadata and extracts experiment package details into a pandas DataFrame.
    The function operates by:
        - Attempting to parse the XML string. If an initial parse fails, it waits 10 seconds before retrying.
        - Iterating over each 'EXPERIMENT_PACKAGE' element found in the XML.
        - Extracting specific metadata fields defined in the global FIELDS dictionary. For each field, the 
          function determines whether to extract an attribute, text, or nested tag based on the provided configuration.
        - Handling missing or malformed data by substituting empty strings.
        - Aggregating the extracted data into a dictionary keyed by the 'Run' identifier.
        - Converting the aggregated data into a pandas DataFrame, ensuring that 'Run' becomes a dedicated column.
    Parameters:
        xml_data (str): A string containing the XML metadata to be processed.
    Returns:
        pd.DataFrame: A DataFrame where each row represents an experiment package, with columns corresponding 
        to the metadata fields (excluding 'Run', which is used as the index before being reset to a column).
    """

# Parse XML metadata
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        print('Error parsing XML, retrying...')
        time.sleep(10)
        root = ET.fromstring(xml_data)

    allDictVals = {}

    for root0 in tqdm(root.findall('.//EXPERIMENT_PACKAGE')):
        # Initialize a dictionary to store the extracted data
        try:
            data = {field: '' for field in FIELDS}
            for field in FIELDS:
                if isinstance(FIELDS[field], dict):
                    try:
                        if 'DATASTORE' in field:
                            value = []
                            for child in root0.findall(FIELDS[field]['find']):
                                val = child.attrib[FIELDS[field]['attrib']]
                                if val:
                                    value.append(val)
                            data[field] = ','.join(list(set(value)))
                            continue
                        if 'attrib' in FIELDS[field]:
                            data[field] = root0.find(FIELDS[field]['find']).attrib[FIELDS[field]['attrib']]
                        elif 'text' in FIELDS[field] and FIELDS[field]['text']:
                            data[field] = root0.find(FIELDS[field]['find']).text
                        elif 'text' in FIELDS[field] and not FIELDS[field]['text']:
                            data[field] = root0.find(FIELDS[field]['find'])[0].tag
                    except AttributeError:
                        data[field] = ''
                else:
                    data[field] = ''
        except AttributeError:
            print(f"Error parsing data for {root0.__dict__}")

        allDictVals[data['Run']] = {k: v for k, v in data.items() if k != 'Run'}        

    metadata = pd.DataFrame.from_dict(allDictVals, orient='index', columns=[k for k in FIELDS.keys() if k != 'Run'])
    metadata.reset_index(inplace=True)
    metadata.rename(columns={'index': 'Run'}, inplace=True)
    return metadata

def get_new_srps(search_term: str, email: str) -> pd.DataFrame:
    """
    Fetches SRA metadata records for a given BioProject search term from the NCBI SRA database.
    This function performs the following steps:
    1. Searches for SRA submissions using the provided search_term. It retrieves submission IDs in batches until no more results are found.
    2. For each batch of submission IDs, it fetches the detailed XML metadata in batches.
    3. Optionally saves each XML metadata batch to a local file named 'batch_meta_{start}.xml'.
    4. Parses each batch of XML metadata using the function 'read_xml_data' and concatenates the results into a single pandas DataFrame.
    Parameters:
        search_term (str): The search query string used to locate SRA submissions, typically representing a BioProject.
        email (str): The email address to register with the Entrez API for identification purposes.
    Returns:
        pd.DataFrame: A pandas DataFrame containing the concatenated metadata from all fetched batches.
                      Returns an empty DataFrame if no metadata is retrieved.
    Raises:
        HTTPError, IncompleteRead: If fetching data fails after the specified number of retry attempts.
    """

    Entrez.email = email
    retstart = 0
    retmax = 4000
    all_ids = []
    print(f"Searching for SRA submissions with the term: {search_term}")
    while True:
        print(f"Fetching records {retstart} to {retstart + retmax}")
        retries = 3
        for attempt in range(retries):
            try:
                with Entrez.esearch(db="sra", idtype='acc', retstart=retstart, retmax=retmax, sort='recently_added', term=search_term) as handle:
                    record = Entrez.read(handle)
                break
            except (urllib.error.HTTPError, http.client.IncompleteRead) as e:
                print(f"Error fetching data for records {retstart} to {retstart + retmax}: {e}, retrying...")
                time.sleep(10)
                if attempt == retries - 1:
                    raise
        if not record['IdList']:
            break
        all_ids.extend(record['IdList'])
        retstart += retmax

    print(f"Found {len(all_ids)} SRA submissions.")

    # Fetch metadata in batches
    metadata_batches = []
    for start in range(0, len(all_ids), retmax):
        batch_ids = all_ids[start:start+retmax]
        print(f"Fetching metadata for batch starting at {start} of size {len(batch_ids)}")
        retries = 2
        for attempt in range(retries):
            try:
                with Entrez.efetch(db="sra", id=batch_ids, rettype="full", retmode='text') as handle:
                    batch_meta = handle.read().decode('UTF-8')
                break
            except (urllib.error.HTTPError, http.client.IncompleteRead) as e:
                print(f"Error fetching data for batch starting at {start}: {e}, retrying...")
                time.sleep(10)
                if attempt == retries - 1:
                    raise
        if batch_meta.strip():
            # Optionally, keep a local copy of the XML batch
            with open(f'batch_meta_{start}.xml', 'w') as f:
                f.write(batch_meta)
            metadata_batches.append(read_xml_data(batch_meta))
        else:
            break

    metadata = pd.concat(metadata_batches, ignore_index=True) if metadata_batches else pd.DataFrame()
    return metadata

def check_retracted_runs(old_metadata: pd.DataFrame, new_metadata: pd.DataFrame) -> pd.Series:
    """
    Check for retracted runs by comparing old and new metadata.
    This function identifies the 'Run' entries in the old_metadata DataFrame that are not present
    in the new_metadata DataFrame, effectively determining which runs have been retracted.
    Parameters:
        old_metadata (pd.DataFrame): A DataFrame containing the previous metadata, which must include a 'Run' column.
        new_metadata (pd.DataFrame): A DataFrame containing the updated metadata, which must include a 'Run' column.
    Returns:
        pd.Series: A Series containing the 'Run' values that were present in old_metadata but are missing from new_metadata.
    """

    retracted_runs = old_metadata[~old_metadata['Run'].isin(new_metadata['Run'])]['Run']
    return retracted_runs

def parse_args() -> argparse.Namespace:
    """
    Parses command-line arguments for the SRA metadata fetching script.
    Returns:
        argparse.Namespace: An object containing the following attributes:
            - bioproject_ids (str): BioProject ID(s) to monitor. Multiple IDs should be separated by commas.
            - email (str): Email address provided for Entrez.
            - metadata (str): Path to the old metadata file.
            - trimming_config (str, optional): Path to the trimming YAML configuration file (if provided).
            - check_retracted (bool): Flag indicating whether to check for retracted SRA runs.
    """

    parser = argparse.ArgumentParser(description='Fetch SRA metadata for a BioProject.')
    parser.add_argument('-b', '--bioproject_ids', type=str, required=True, help='BioProject ID to monitor. Multiple IDs should be separated by commas.')
    parser.add_argument('-e', '--email', type=str, required=True, help='Email address for Entrez')
    parser.add_argument('-m', '--metadata', type=str, required=False, help='Path to old metadata file')
    parser.add_argument('-t', '--trimming_config', type=str, required=False, help='Path to trimming yaml file')
    parser.add_argument('-r', '--check_retracted', action='store_true', help='Check for retracted SRA runs')
    return parser.parse_args()

def main():
    """
    Main function to fetch, update, and process SRA metadata.
    This function performs the following steps:
    1. Parses command-line arguments.
    2. Processes provided BioProject IDs to construct a search term.
    3. Retrieves new SRA metadata using the search term and a supplied email address.
    4. Reads the previous metadata from a CSV file.
    5. Identifies new SRA runs by comparing the retrieved metadata against the previous metadata.
    6. If new runs are found:
        - Prints the number of new SRA runs.
        - Concatenates the new runs with the previous metadata.
        - Assigns a 'process_flag' and a boolean 'is_milk' flag based on the 'isolation_source' column.
        - If a trimming configuration file is provided, applies global trimming settings for applicable assay types.
        - Saves the processed information for new SRA runs to a TSV file.
    7. If the check for retracted runs is enabled:
        - Marks retracted runs in the combined metadata.
        - Updates the retraction detection date for newly retracted runs.
    8. Compares the updated metadata with the previous metadata and saves the updated metadata to a new CSV file if changes are detected.
    Returns:
         None
    """

    args = parse_args()
    
    # Resolve metadata path: use provided path or build a sensible default from bioproject ids
    if args.metadata:
        metadata_path = args.metadata
    else:
        proj_tag = "_".join([bid.strip() for bid in args.bioproject_ids.split(',') if bid.strip()]) or "sra"
        metadata_path = f"{proj_tag}_metadata.csv"
    
    # Process BioProject IDs
    bioproject_ids = [bid.strip() for bid in args.bioproject_ids.split(',') if bid.strip()]
    search_term = " OR ".join(f"{bid}[BioProject]" for bid in bioproject_ids)

    new_metadata = get_new_srps(search_term, args.email)
    # Try to read previous metadata from the resolved metadata_path; if missing use empty df
    try:
        prev_metadata = pd.read_csv(metadata_path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        print(f"Metadata file {metadata_path} not found or empty, using empty DataFrame.")
        prev_metadata = pd.DataFrame(columns=FIELDS.keys())

    new_sras = new_metadata.loc[~new_metadata['Run'].isin(prev_metadata['Run'])]
    combined_metadata = prev_metadata.copy()

    if new_sras.empty:
        print("No new SRA runs found.")
    else:
        print(f"Found {len(new_sras)} new SRA run(s).")
        combined_metadata = pd.concat([prev_metadata, new_sras], ignore_index=True)
        new_sras = new_sras.assign(
            is_milk=new_sras['isolation_source'].str.contains('milk', case=False, na=False),
            process_flag=True
        )
        save_columns = ['Run', 'process_flag', 'is_milk']

        if args.trimming_config:
            with open(args.trimming_config, 'r') as f:
                trimming_config = yaml.safe_load(f)
            new_sras['global_trimming'] = new_sras.apply(
                lambda row: trimming_config.get(row['BioProject'], trimming_config['default']).get('global_trimming')
                            if 'amp' in str(row['Assay Type']).lower() else None,
                axis=1
            )
            save_columns.append('global_trimming')

        new_sras[save_columns].to_csv(
            metadata_path.replace('.csv', '_to_process.tsv'),
            index=False,
            sep='\t'
        )

    if args.check_retracted:
        # Check for retracted runs and update metadata accordingly
        retracted_runs = check_retracted_runs(prev_metadata, new_metadata)
        combined_metadata['is_retracted'] = combined_metadata['Run'].isin(retracted_runs)
        # ensure is_retracted is boolean
        combined_metadata['is_retracted'] = combined_metadata['is_retracted'].astype(bool)

        # Ensure the retraction detection date column exists
        if 'retraction_detection_date_utc' not in combined_metadata.columns:
            combined_metadata['retraction_detection_date_utc'] = pd.NaT

        # Update detection date for newly retracted runs
        now_str = pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%d %H:%M:%S')
        mask = combined_metadata['is_retracted'] & combined_metadata['retraction_detection_date_utc'].isna()
        combined_metadata.loc[mask, 'retraction_detection_date_utc'] = now_str

        # assert that all retracted runs have a detection date and no non-retracted runs have a date
        assert combined_metadata.loc[combined_metadata['is_retracted'], 'retraction_detection_date_utc'].notna().all()
        assert combined_metadata.loc[~combined_metadata['is_retracted'], 'retraction_detection_date_utc'].isna().all()

    if combined_metadata.equals(prev_metadata):
        print("No new updates found.")
    else:
        updated_path = metadata_path.replace('.csv', '_updated.csv')
        combined_metadata.to_csv(updated_path, index=False)
        print(f"Updated metadata saved to {updated_path}")


if __name__ == "__main__":
    main()
