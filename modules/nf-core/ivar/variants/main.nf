process IVAR_VARIANTS {
    tag "$sra - $referenceGene"
    label 'process_high'

    conda "${moduleDir}/environment.yml"

    input:
    each referenceGene
    tuple val(sra), path(bamFile)
    path reference
    path gff_file

    output:
    path "*_variants.tsv",         emit: variants
    path  "versions.yml", emit: versions

    script:
    def gene = referenceGene.split("\\|")[0]
    def gff_file_arg = gff_file == null ? "" : "-g $gff_file"
    """
    samtools index $bamFile

    samtools mpileup --reference $reference -r \"$referenceGene\" -A -d 0 -aa -Q 0 $bamFile | ivar variants -p ${sra}_${gene}_variants -t 0.01 -m 1 -r $reference $gff_file_arg

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        samtools: \$(echo \$(samtools --version 2>&1) | sed 's/^.*samtools //; s/Using.*\$//')
        ivar: \$(echo \$(ivar version 2>&1) | sed 's/^.*version //; s/Please.*\$//')
    END_VERSIONS
    """

    stub:
    """
    touch ${sra}_${gene}_variants.tsv

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        samtools: \$(echo \$(samtools --version 2>&1) | sed 's/^.*samtools //; s/Using.*\$//')
        ivar: \$(echo \$(ivar version 2>&1) | sed 's/^.*version //; s/Please.*\$//')
    END_VERSIONS
    """
}
