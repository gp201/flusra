include { BWA_MEM } from '../../../modules/nf-core/bwa/mem/main'
include { IVAR_CONSENSUS } from '../../../modules/nf-core/ivar/consensus/main'
include { IVAR_VARIANTS } from '../../../modules/nf-core/ivar/variants/main'
include { SAMTOOLS_DEPTH } from '../../../modules/nf-core/samtools/depth/main'
include { GENOFLU } from '../../../modules/local/genoflu/main'
include { MERGE_GENOFLU_RESULTS } from '../../../modules/local/merge_genoflu_results/main'

workflow PROCESS_SRA {
    take:
    sra_samples_ch

    main:
    BWA_MEM(sra_samples_ch, params.reference)

    // Generate a tuple of genes from the reference fasta file
    Channel
        .from(readFastaHeaders(params.reference))
        .set { genes_ch }

    IVAR_CONSENSUS(
        BWA_MEM.out.bam,
        genes_ch,
        params.reference,
        params.consensus_threshold,
        params.consensus_min_depth,
    )

    IVAR_CONSENSUS.out.consensus
        .map { meta, consensus_file -> [meta.id, consensus_file] }
        .collectFile { id, file -> ["${id}.fa", file] }
        .set { consensus_for_genoflu_ch }

    GENOFLU(consensus_for_genoflu_ch)

    MERGE_GENOFLU_RESULTS(
        GENOFLU.out.genoflu_results.collect(),
        params.genoflu_results,
    )

    SAMTOOLS_DEPTH(
        BWA_MEM.out.bam,
        genes_ch,
        params.reference,
    )

    BWA_MEM.out.bam
        .combine(
            genes_ch.map { header ->
                def gene = header.split("\\|")[0]
                [
                    gene,
                    header,
                    !params.gff_files.isEmpty() ? params.gff_files?.get(gene) ?: "${projectDir}/assets/NO_FILE" : "${projectDir}/assets/NO_FILE",
                ]
            }
        )
        .set { ch_ivar_variants_input }

    IVAR_VARIANTS(
        ch_ivar_variants_input,
        params.reference,
        params.variant_threshold,
        params.variant_min_depth,
    )
}

def readFastaHeaders(fastaFile) {
    new File(fastaFile)
        .readLines()
        .findAll { it.startsWith(">") }
        .collect { it.substring(1) }
}
