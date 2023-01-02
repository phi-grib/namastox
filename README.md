# NAMASTOX

Software tool for supporting the implementation of New Assessment Methods (NAMs) within a New Generation Risk Assessment (NGRA) framework.


## Install

*** conda environment ***


## NAMASTOX commands

| Command | Description |
| --- | --- |
| -c/ --command | Action to be performed. Acceptable values are *new*, *kill*, *update*  |
| -r/ --risk | Name of the risk assessment (RA)
| -a/ --action | Use 'silent' to configure the program using default RA repositories    |
| -i/ --infile | Name of the input file used by the command. |
| -o/ --outfile | Name of the output file used by the command. |
| -h/ --help | Shows a help message on the screen |


## Quickstart

Configure using 

``python namastox.py -config -a silent``

Create a new risk assessment 

``python namastox.py -c new -r myproject ``

Remove completely a risk assessment

``python namastox.py -c kill -r myproject ``

Update a risk assessment, using a delta.yaml file containing new data

``python namastox.py -c update -r myproject -i delta.yaml``

Idem but generating an output yaml file wich can be used to add new information

``python namastox.py -c update -r myproject -i delta.yaml -o myproyect.yaml``


## Acknowledgments

Part of the project RISKHUNT3R (https://www.risk-hunt3r.eu/)

![Alt text](images/risk-hunt3r-logo.png?raw=true "RISKHUNT3R-logo") 

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 964537.

