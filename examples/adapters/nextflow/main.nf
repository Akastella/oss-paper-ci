process hello {
    output:
        stdout into results
    """
    echo "Hello from Nextflow"
    """
}

results.view()
