def get_args(wildcards):
    """Function returning appropriate parameters with the flag
    for the corresponding model
    """
    if "MMSplice" in wildcards.model:
        return "-g tests/data/interval-based/test.gtf"
    else:
        return "-s diff -s logit"


rule all:
    input: 
        "tests/output.merged.tsv"

rule run_vep:
    input: 
        vcf = "tests/data/interval-based/test.vcf", 
        fasta = "tests/data/interval-based/test.fa", 
    output: 
        temp("output.{model}.tsv")
    params: 
        model_args = get_args
    shell: 
        "kipoi_veff2 {input.vcf} {input.fasta} {params.model_args} {output} -m {wildcards.model}"


rule merge:
    input: 
        expand("output.{model}.tsv", model=["Basset", "MMSplice/mtsplice"])
    output: "tests/output.merged.tsv"
    shell: 
        "merge {input} {output}"

