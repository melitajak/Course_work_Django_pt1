from django import forms

class SpadesOptionsForm(forms.Form):
    # Input Data 
    input_type = forms.ChoiceField(choices=[
        ('interlaced', 'Interlaced Paired-End Reads'),
        ('paired', 'Paired-End Reads'),
        ('unpaired', 'Unpaired Reads'),
        ('merged', 'Merged Paired-End Reads'),
    ], label="Select Input Type", required=True)

    interlaced_reads = forms.FileField(label="Interlaced Paired-End Reads", required=False)
    forward_reads = forms.FileField(label="Forward Reads (-1)", required=False)
    reverse_reads = forms.FileField(label="Reverse Reads (-2)", required=False)
    unpaired_reads = forms.FileField(label="Unpaired Reads (-s)", required=False)
    merged_reads = forms.FileField(label="Merged Paired-End Reads", required=False)

    # Basic Options
    isolate = forms.BooleanField(label="--isolate", required=False)
    sc = forms.BooleanField(label="--sc", required=False)
    meta = forms.BooleanField(label="--meta", required=False)
    bio = forms.BooleanField(label="--bio", required=False)
    corona = forms.BooleanField(label="--corona", required=False)
    rna = forms.BooleanField(label="--rna", required=False)
    plasmid = forms.BooleanField(label="--plasmid", required=False)
    metaviral = forms.BooleanField(label="--metaviral", required=False)
    metaplasmid = forms.BooleanField(label="--metaplasmid", required=False)
    rnaviral = forms.BooleanField(label="--rnaviral", required=False)
    iontorrent = forms.BooleanField(label="--iontorrent", required=False)
    test = forms.BooleanField(label="--test", required=False)

    # Pipeline Options
    only_error_correction = forms.BooleanField(label="--only-error-correction", required=False)
    only_assembler = forms.BooleanField(label="--only-assembler", required=False)
    careful = forms.BooleanField(label="--careful", required=False)
    checkpoints = forms.ChoiceField(choices=[('last', 'Last'), ('all', 'All')], label="--checkpoints", required=False)
    continue_run = forms.BooleanField(label="--continue", required=False)
    restart_from = forms.CharField(label="--restart-from", required=False)
    disable_gzip_output = forms.BooleanField(label="--disable-gzip-output", required=False)
    disable_rr = forms.BooleanField(label="--disable-rr", required=False)

    # Advanced Options
    threads = forms.IntegerField(label="-t, --threads", required=False, initial=16)
    kmer_sizes = forms.CharField(label="-k, --k-mer sizes", required=False, initial='auto')
    cov_cutoff = forms.CharField(label="--cov-cutoff", required=False, initial='off')
    phred_offset = forms.ChoiceField(choices=[(33, '33'), (64, '64')], label="--phred-offset", required=False)
