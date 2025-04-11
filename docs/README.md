# flusra: Documentation

You can run the pipeline with the following command:

```bash
nextflow run https://github.com/andersen-lab/flusra.git -r 'main' -c /nextflow.config -profile <mamba,conda>
```

## Parameters in the `nextflow.config` file

- `bioproject`: The BioProject ID to fetch the data from NCBI.
- `email`: The email address to use for the NCBI API.
- `only_fetch`: If `true`, only fetch the metadata from NCBI and save it to the `outdir` directory.
- `fetch_and_pull`: If `true`, fetch the metadata from NCBI and pulls the new data from SRA.
- `metadata`: Provide an existing metadata file to bypass processing already processed SRA data
- `reference`: The reference genome to use for mapping.
- `sra_accessions`: The SRA accessions to process. Provide a list of SRA accessions to process without a BioProject ID skips fetching metadata.
- `outdir`: The output directory where the results will be saved.

If you want to run the pipeline with a different configuration, you can create a new `nextflow.config` file and provide the path to the `-c` option.

Please report any issues and suggestions regarding the pipeline to the [issue tracker](https://github.com/andersen-lab/flusra/issues).
