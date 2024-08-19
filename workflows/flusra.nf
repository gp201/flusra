include { BWA_MEM                 } from '../modules/nf-core/bwa/mem/main'
include { IVAR_CONSENSUS          } from '../modules/nf-core/ivar/consensus/main'
include { IVAR_VARIANTS           } from '../modules/nf-core/ivar/variants/main'
include { SAMTOOLS_DEPTH          } from '../modules/nf-core/samtools/depth/main'
include { SRATOOLS_FASTERQDUMP    } from '../modules/nf-core/sratools/fasterqdump/main'

workflow FLUSRA {
    take:
    sra_accessions_ch
    fetch_and_pull

    main:

    if (fetch_and_pull) {
        SRATOOLS_FASTERQDUMP(sra_accessions_ch)
    } else {
        SRATOOLS_FASTERQDUMP(sra_accessions_ch)

        BWA_MEM(SRATOOLS_FASTERQDUMP.out.reads, params.reference)

        // make this a tuple of reference and gene
        Channel.from(readFastaHeaders(params.reference))
            .set { headers_ch }

        IVAR_CONSENSUS(headers_ch, BWA_MEM.out.bam, params.reference)
        IVAR_VARIANTS(headers_ch, BWA_MEM.out.bam, params.reference, params.gff_file)
        SAMTOOLS_DEPTH(headers_ch, BWA_MEM.out.bam, params.reference)
    }
}

def readFastaHeaders(fastaFile) {
    def headers = []
    new File(fastaFile).withReader { reader ->
        def line
        while ((line = reader.readLine()) != null) {
            if (line.startsWith(">")) {
                headers << line.substring(1)
            }
        }
    }
    return headers
}
