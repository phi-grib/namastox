# NAMASTOX

Software tool for supporting the implementation of New Assessment Methods (NAMs) within a New Generation Risk Assessment (NGRA) framework.


## Install

*** conda environment ***


## NAMASTOX commands

| Command | Description |
| --- | --- |
| -c/ --command | Action to be performed. Acceptable values are *new*, *kill*, *list*, *update*, *report*  |
| -r/ --raname | Name of the risk assessment 
| -v/ --version | Version of the risk assessment 
| -a/ --action | Use 'silent' to configure the program using default RA repositories    |
| -d/ --directory | Use this parameter in action configure to define the RA repositories    |
| -i/ --infile | Name of the input file used by the command. |
| -o/ --outfile | Name of the output file used by the command. |
| -p/ --pdf | Name of the report in PDF format |
| -h/ --help | Shows a help message on the screen |


## Quickstart

Configure using 

``python namastox.py -config -a silent``

Create a new risk assessment 

``python namastox.py -c new -r myproject -o myproject.yaml``

This creates a yaml file which can be used as a template for add information about the substances to study or the endpoints which should be studied 

Update a risk assessment, using a delta.yaml file containing new data

``python namastox.py -c update -r myproject -i delta.yaml``

Idem but generating an output yaml file wich can be used to add new information

``python namastox.py -c update -r myproject -i delta.yaml -o myproyect.yaml``

Remove completely a risk assessment

``python namastox.py -c kill -r myproject ``

List all the risk assessments present in the current repository

``python namastox.py -c list ``


## Acknowledgments

Part of the project RISKHUNT3R (https://www.risk-hunt3r.eu/)

![Alt text](images/risk-hunt3r-logo.png?raw=true "RISKHUNT3R-logo") 

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 964537.

