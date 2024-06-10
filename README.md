# namastox

Software tool for supporting the implementation of New Assessment Methods (NAMs) within a New Generation Risk Assessment (NGRA) framework.


## Install

A docker container (https://www.docker.com/), fully configured can be downloaded from DockerHub and installed using:

```bash
docker run -d -p 5000:5000 acabrera809/namastox:latest
```
Then, the NAMASTOX GUI will be accesible from a web browser at address http://localhost:5000

Please note that the port of this address is defined in the command line above and can be easily customized.

It is also possible to use an existing local folder for storing the RAs. Let's assume you wish to use 'c:\data' as the local NAMASTOX repository. Start by creating a folder inside named 'ras'. Then, run the following command: 

```bash
docker run -d -p 5000:5000 -v c:\data:/data acabrera809/namastox:latest
```
Then, as in the previous example, you can acces the NAMASTOX GUI from a web broser at http://localhost:5000


NAMASTOX can be used in most Windows, Linux or macOS configurations, provided that a suitable execution environment is set up. We recommend, as a fist step, installing the Conda package and environment manager. Download a suitable Conda or Anaconda distribution for your operative system from [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html#)


Download the repository:

```bash
git clone https://github.com/phi-grib/NAMASTOX.git
```

Go to the repository directory 

```bash
cd NAMASTOX
```

and create the **conda environment** with all the dependencies and extra packages (numpy, RDKit...):

```bash
conda env create -f environment.yml
```

Once the environment is created type:

```bash
source activate namastox
```

to activate the environment.

Conda environments can be easily updated using a new version of the environment definition

```bash
conda env update -f new_environment.yml
```

NAMASTOX must be installed as a regular Python package. From the NAMASTOX directory type (note the dot at the end):

```bash
pip install . 
```

or

```bash
python setup.py install
```

For development, use pip with the -e flag or setup with `develop` instead of `install`. This will made accesible the latest changes to other components

```bash
pip install -e .
```
or 

```bash
python setup.py develop
```

## Documentation (for the GUI)

We prepared a series of short (1 to 2 minutes) videos explaining how to carry out common tasks:
- create a new RA [here](https://drive.google.com/file/d/17FPzaVE1tzNcwi3nP1jXF43jvoSx1Xpw/view?usp=sharing)
- executing a task [here](https://drive.google.com/file/d/1TaPsgqTesrx2kdPxViZ2nO3Bfq6LCNuH/view?usp=sharing)
- making decisions [here](https://drive.google.com/file/d/1xKlXPA0fk0a--rHdeo1W1GtFjNGrPDlL/view?usp=sharing)
- review results and decisions [here](https://drive.google.com/file/d/1a57Q-YlWtUpAKSPjYFTB80LOMO7drdDY/view?usp=sharing)
- generating reports [here](https://drive.google.com/file/d/1Y5dfElFdavgh5JqWUpmr0KbRrtDuf-Hp/view?usp=sharing)
- project management [here](https://drive.google.com/file/d/1AKXig2ASWMTS5iLqF-n2LQ865ZRzGilQ/view?usp=sharing)

Here is also the link to a quickstarting guide: [here](https://github.com/phi-grib/namastox/namastox/documentation/quickstarting.pdf)

## Configuration

After installation is completed, you must run the configuration command to configure the directory where NAMASTOX will place the risk assessments. If NAMASTOX has not been configured previously the following command

```bash
namastox -c config
```

will suggest a default directory structure following the XDG specification in GNU/Linux, %APPDATA% in windows and `~/Library/Application Support/NAMASTOX_RA` in Mac OS X.

To specify a custom path use the `-d` parameter to enter the root folder where the risk assessments will be placed:

```bash
namastox -c config -d /my/custom/path
```

will set up the risk assessments repository to `/my/custom/path/ras`

Once NAMASTOX has been configured, the current setting can be displayed using again the command 

```bash
namastox -c config
```

As a fallback, NAMASTOX can also be configured using the following command

```bash
namastox -c config -a silent
```

This option sets up the risk assessments within the NAMASTOX installation directory (`namastox\namastox\ras`). Unlike other options, this command does not ask permision to the end-user to create the directories or set up the repositories and is used internally by automatic installers and for software development. 



## NAMASTOX commands

Command interface synthax

| Command | Description |
| --- | --- |
| -c/ --command | Action to be performed. Acceptable values are *new*, *kill*, *list*, *update*, *report*  |
| -r/ --raname | Name of the risk assessment 
| -a/ --action | Use 'silent' to configure the program using default RA repositories    |
| -d/ --directory | Use this parameter in action configure to define the RA repositories    |
| -i/ --infile | Name of the input file used by the command. |
| -o/ --outfile | Name of the output file used by the command. |
| -h/ --help | Shows a help message on the screen |

Command examples and description

| Command | Example | Description |
| --- | --- | ---|
| new | *namastox -c new -r myproject -o template.yaml* | Creates a new entry in the risk assessments repository named myproject and generates a yaml file that is used as a template for updating the risk assessement |
| kill | *namastox -c kill -r myproject* | Removes myproject from the risk assessment repository. **Use with extreme care**, since the program will not ask confirmation and the removal will be permanent and irreversible  |
| list | *namastox -c list* | Lists the risk assessments present in the repository |
| update | *namastox -c update -r myproject -i result.yaml -o template.yaml* | Update the risk assessment with the new information present in the result.yaml file. The new data is processed internally, progressing to the new workflow node and the new data is stored in a local repository. The output is a template for entering new information |
| report | *namastox -c report -r myproject -w report.docx* |  |


## Quickstart

Configure using 

``namastox -config -a silent``

Create a new risk assessment 

``namastox -c new -r myproject -o template.yaml``

This creates a yaml file which can be used as a template for add information about the substances to study or the endpoints which should be studied 

Update a risk assessment, using a delta.yaml file containing new data. The file generates a new version of the yaml file

``namastox -c update -r myproject -i result.yaml -o template.yaml``

Generate a report with the current status of the risk assessment (in Word format):

``namastox -c report -r myproject -w report.docx``

Remove completely a risk assessment

``namastox -c kill -r myproject ``

List all the risk assessments present in the current repository

``namastox -c list ``


## Acknowledgments

NAMASTOX has been developed for the project RISKHUNT3R (https://www.risk-hunt3r.eu/)

![Alt text](images/risk-hunt3r-logo.png?raw=true "RISKHUNT3R-logo") 

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 964537.

