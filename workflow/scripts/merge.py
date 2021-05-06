import pandas as pd

list_of_input_files = list(snakemake.input)  # noqa: F821
df1 = pd.read_csv(
    list_of_input_files[0],
    sep="\t",
    index_col=["#CHROM", "POS", "ID", "REF", "ALT"],
)
for input_file in list_of_input_files[1:]:
    df2 = pd.read_csv(
        input_file, sep="\t", index_col=["#CHROM", "POS", "ID", "REF", "ALT"]
    )
    df1 = pd.concat([df1, df2], axis=1)
df1.to_csv(snakemake.output[0], sep="\t")  # noqa: F821
