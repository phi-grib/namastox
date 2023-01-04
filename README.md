# NAMASTOX

Software tool for supporting the implementation of New Assessment Methods (NAMs) within a New Generation Risk Assessment (NGRA) framework.


## Install

*** conda environment ***


## NAMASTOX commands

Command interface synthax

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

Command examples and description

| Command | Example | Description |
| --- | --- | ---|
| new | *namastox.py -c new -r myproject -o myproject.yaml* | Creates a new entry in the risk assessments repository named myproject and generates a yaml file that is used as a template for updating the risk assessement |
| kill | *namastox.py -c kill -r myproject* | Removes myproject from the risk assessment repository. **Use with extreme care**, since the program will not ask confirmation and the removal will be permanent and irreversible  |
| list | *namastox.py -c list* | Lists the risk assessments present in the repository |
| update | *namastox.py -c update -r myproject -i delta.yaml -o myproject.yaml* | Update the risk assessment with the new information present in the delta.yaml file. The new data is processed by the expert and the changes are reflected interanally and in the yaml output file |
| report | *namastox.py -c report -r myproject -p report.pdf* | *** not implemented yet *** |


## Quickstart

Configure using 

``python namastox.py -config -a silent``

Create a new risk assessment 

``python namastox.py -c new -r myproject -o myproject.yaml``

This creates a yaml file which can be used as a template for add information about the substances to study or the endpoints which should be studied 

Update a risk assessment, using a delta.yaml file containing new data. The file generates a new version of the yaml file

``python namastox.py -c update -r myproject -i delta.yaml -o myproyect.yaml``

*** report ***



Remove completely a risk assessment

``python namastox.py -c kill -r myproject ``

List all the risk assessments present in the current repository

``python namastox.py -c list ``


## Acknowledgments

Part of the project RISKHUNT3R (https://www.risk-hunt3r.eu/)

![Alt text](images/risk-hunt3r-logo.png?raw=true "RISKHUNT3R-logo") 

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 964537.

