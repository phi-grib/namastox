#! -*- coding: utf-8 -*-

# Description    NAMASTOX command
#
# Authors:       Manuel Pastor (manuel.pastor@upf.edu)
#
# Copyright 2022 Manuel Pastor
#
# This file is part of NAMASTOX
#
# NAMASTOX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.
#
# Flame is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NAMASTOX. If not, see <http://www.gnu.org/licenses/>.

import os
import yaml
import json
import shutil
import urllib3
import numpy as np
import pandas as pd
from urllib3.util.ssl_ import create_urllib3_context
import tarfile
from rdkit import Chem
from namastox.logger import get_logger
from namastox.ra import Ra
from namastox.utils import ra_repository_path, ra_path, id_generator

LOG = get_logger(__name__)

def action_new(raname, outfile=None):
    '''
    Create a new risk assessment tree, using the given name.
    This creates the development version "dev",
    copying inside default child classes
    '''
    if not raname:
        return False, 'empty risk assessment name'

    # importlib does not allow using 'test' and issues a misterious error when we
    # try to use this name. This is a simple workaround to prevent creating ranames 
    # with this name 
    if raname == 'test':
        return False, 'the name "test" is disallowed, please use any other name'

    # raname directory with /dev (default) level
    ndir = ra_path(raname)
    if os.path.isdir(ndir):
        return False, f'Risk assessment {raname} already exists'
    try:
        os.mkdir(ndir)
        os.mkdir(os.path.join(ndir,'hist'))
        os.mkdir(os.path.join(ndir,'repo'))
        LOG.debug(f'{ndir}, {ndir}/hist and {ndir}/repo created')
    except:
        return False, f'Unable to create path for {raname} endpoint'

    # Copy templates
    wkd = os.path.dirname(os.path.abspath(__file__))
    template_names = ['ra.yaml', 'workflow.csv']

    for cname in template_names:
        src_path = os.path.join (wkd, 'default', cname)
        try:
            shutil.copy(src_path, ndir)
        except:
            return False, f'Unable to copy {cname} file'

    LOG.debug(f'copied risk assessment templates from {src_path} to {ndir}')

    # Instantiate Ra
    ra = Ra(raname)
    success, results = ra.load()
    if not success:
        return False, results

    # Include RA information 
    ra.setVal('ID', id_generator() )

    # Save
    ra.save()

    # Show template
    yaml = ra.getTemplate()
    
    if outfile is not None:
        with open(outfile,'w') as f:
            f.write(yaml)

    return True, f'New risk assessment {raname} created'

def getRaHistoric (raname, step):
    ''' retrieves from the historical record the item corresponding to the step given as argument
    '''
    radir = ra_path(raname)
    rahist = os.path.join(radir,'hist')
    if not os.path.isdir(rahist):
        return False, f'Historic repository for risk assessment {raname} not found'

    for ra_hist_file in os.listdir(rahist):
        # do not use backup files
        if ra_hist_file.startswith('bk_'):
            continue
        
        ra_hist_item = os.path.join(rahist, ra_hist_file)
        if os.path.isfile(ra_hist_item):
            idict = {}
            with open(ra_hist_item, 'r') as pfile:
                idict = yaml.safe_load(pfile)
                if 'ra' in idict:
                    if 'step' in idict['ra']:
                        if idict['ra']['step'] == step:
                            return True, ra_hist_item
            
    return False, 'file not found'

def action_kill(raname, step=None):
    '''
    removes the last step from the ra tree or the whole tree if no step is specified
    '''
    if not raname:
        return False, 'Empty risk assessment name'

    ndir = ra_path(raname)

    if not os.path.isdir(ndir):
        return False, f'Risk assessment {raname} not found'

    # Remove the whole tree
    if step is None:
        try:
            shutil.rmtree(ndir, ignore_errors=True)
        except:
            return False, f'Failed to remove risk assessment {raname}'

        return True, f'Risk assessment {raname} removed'

    # Remove last step
    if step == 1:
        return False, 'the first step cannot be removed'

    # New value of step
    new_step = step-1

    # load RA
    ra = Ra(raname)
    success, results = ra.load()
    if not success:
        return False, results

    last_step = ra.getVal('step')
    if step!=last_step:
        return False, 'only the last step can be removed'

    # find the previous step in the repo and copy as ra.yaml overwriting existing file
    success, ra_new = getRaHistoric(raname, new_step)
    if not success:
        return False, f'unable to retrieve file {ra_new} from the historic repository'

    shutil.copy(ra_new, os.path.join(ndir,'ra.yaml'))
    
    # remove the ra to delete 
    success, ra_delete = getRaHistoric(raname, step)
    if not success:
        return False, f'unable to remove file {ra_delete}'

    os.remove(ra_delete)

    return True, 'OK'

def action_list(out='text'):
    '''
    if no argument is provided lists all ranames present at the repository 
    otherwyse lists all versions for the raname provided as argument
    '''
    rdir = ra_repository_path()
    if os.path.isdir(rdir) is False:
        return False, 'The risk assessment name repository path does not exist. Please run "namastox -c config".'

    output = []
    num_ranames = 0
    if out != 'json':
        LOG.info('Risk assessment(s) found in repository:')
        
    for x in os.listdir(rdir):
        xpath = os.path.join(rdir,x) 

        # discard if the item is not a directory
        if not os.path.isdir(xpath):
            continue

        num_ranames += 1
        if out != 'json':
            LOG.info('\t'+x)

        output.append(x)

    LOG.debug(f'Retrieved list of risk assessments from {rdir}')
    
    # web-service
    if out=='json':
        return True, output

    return True, f'{num_ranames} risk assessment(s) found'

def action_steps(raname, out='text'):
    '''
    provides a list with all steps for ranames present at the repository 
    '''
    radir = ra_path(raname)
    rahist = os.path.join(radir,'hist')
    if not os.path.isdir(rahist):
        return False, f'Historic repository for risk assessment {raname} not found'

    steps = []
    for ra_hist_file in os.listdir(rahist):

        # ignore backup files
        if ra_hist_file.startswith('bk'):
            continue
        
        ra_hist_item = os.path.join(rahist, ra_hist_file)
        if os.path.isfile(ra_hist_item):
            idict = {}
            with open(ra_hist_item, 'r') as pfile:
                idict = yaml.safe_load(pfile)
                if 'ra' in idict:
                    if 'step' in idict['ra']:
                        steps.append(idict['ra']['step'])
                        if out != 'json':
                            LOG.info(f'step: {steps[-1]}')
    
    LOG.debug(f'Retrieved list of steps from {rahist}')

    # web-service
    if out=='json':
        return True, steps

    return True, f'{len(steps)} steps found'

def action_info(raname, out='text'):
    '''
    provides a list with all steps for ranames present at the repository 
    '''
    # instantiate a ra object
    ra = Ra(raname)

    succes, results = ra.load()
    if not succes:
        return False, results

    # get a dictionary with the ra.yaml contents that can
    # be passed to the GUI or shown in screen
    info = ra.getGeneralInfo()

    LOG.debug(f'Retrieved general info for {raname}')

    for ikey in info:
        ielement = info[ikey]
        for jkey in ielement:
            jelement = ielement[jkey]
            if out != 'json':
                LOG.info(f'{ikey} : {jkey} : {jelement}')

    # web-service
    if out=='json':
        return True, info

    return True, f'completed info for {raname}'

def getPath(raname):
    '''
    returns the path to the RA folder for ra raname
    '''
    # instantiate a ra object
    ra = Ra(raname)

    succes, results = ra.load()
    if not succes:
        return False, results
    
    return True, ra.rapath

def getRepositoryPath(raname):
    '''
    returns the path to the repository folder for ra raname
    '''
    # instantiate a ra object
    ra = Ra(raname)

    succes, results = ra.load()
    if not succes:
        return False, results
    
    repo_path = os.path.join(ra.rapath, 'repo')
    return True, repo_path

def getWorkflow(raname, step=None):
    '''
    returns a marmaid string describing the "visible workflow"
    '''

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load()
    if not succes:
        return False, results
    
    workflow_graph = ra.getWorkflowGraph(step)
    return (workflow_graph is not None), workflow_graph


def setCustomWorkflow (raname, file):
    '''
    defines the file provided as argument as a custom workflow
    '''
    # instantiate a ra object
    ra = Ra(raname)

    success, result = ra.updateWorkflow (file)
    return success, result

def convertSubstances(file):
    '''
    returns a dictionary with a list of substances names, SMILES and CASRN
    '''
    suppl = Chem.SDMolSupplier(file, sanitize=True)
    count = 0
    results = []
    for mol in suppl:
        if mol is None:
            continue
        count=count+1

        # extract the molecule name
        if mol.HasProp('name'):  
            iname = mol.GetProp('name')
        elif mol.HasProp('Name'):  
            iname = mol.GetProp('Name')
        elif mol.HasProp('NAME'):  
            iname = mol.GetProp('NAME')
        else:
            iname = f'mol{count}'

        # extract the CASRN 
        if mol.HasProp('CASRN'):  
            icasrn = mol.GetProp('CASRN')
        elif mol.HasProp('CAS'):  
            icasrn = mol.GetProp('CAS')
        elif mol.HasProp('CAS-RN'):  
            icasrn = mol.GetProp('CAS-RN')
        else:
            icasrn = 'na'

        # extract the ID 
        if mol.HasProp('id'):  
            iid = mol.GetProp('id')
        elif mol.HasProp('ID'):  
            iid = mol.GetProp('ID')
        elif mol.HasProp('molid'):  
            iid = mol.GetProp('molid')
        else:
            iid = 'na'

        # obtain the SMILES
        ismiles = Chem.MolToSmiles(mol)

        results.append( {'name': iname, 'id': iid, 'smiles': ismiles, 'casrn': icasrn })

    if len(results)> 0:
        return True, results

    return False, 'empty molecule'

def getLocalModels ():
    '''
    returns the list of local models calling directly the Flame library. The models must be 
    available in a properly configured Flame repository
    '''
    from flame import manage as flame_manage

    results = []
    success, models = flame_manage.action_dir()
    if not success:
        return False, results
    
    for imodel in models:
        results.append((imodel['modelname'], imodel['version']))

    return True, results

def getModelDocumentation (model_name, model_ver):

    from flame import manage as flame_manage

    success, documentation = flame_manage.action_documentation(model_name, model_ver, oformat='JSON')

    if not success:
        return False, documentation

    documentation_YAML = documentation.dumpYAML()
    documentation_str = ''
    for iline in documentation_YAML:
        documentation_str+= iline.split('#')[0]+'\n'
    documentation_dict = yaml.safe_load(documentation_str)

    return True, documentation_dict

def predictLocalModels (raname, models, versions):
    ''' returns a prediction using the substance defined in the ra, using the list of local models and versions specified
    '''
    from flame import context

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load()
    if not succes:
        return False, results
    
    success, ra_repo_path = getRepositoryPath (raname)
    structure_sdf = os.path.join(ra_repo_path,'structure.sdf')

    generalInfo = ra.getGeneralInfo()
    generalInfo = generalInfo['general']
    try:
        # extract SMILES and write a SDFile in RA repository
        smiles = generalInfo['substances'][0]['smiles']
    except:
        return False, f'no substance defined in {raname}'

    try:
        mol = Chem.MolFromSmiles(smiles)
    except:
        return False, f'incorrect SMILES format: {smiles}'
    
    writer = Chem.SDWriter(structure_sdf)
    writer.write(mol)
    writer.close()

    # profile requires more than one model selected
    # if only one model is selected, run the prediction twice
    if len(models)==1:
        models.append(models[0])
        versions.append(versions[0])

    arguments = {'label' : 'namastox',
                 'infile': structure_sdf,
                 'multi' : {'endpoints': models, 
                            'versions': versions}
                }
    
    success, results = context.profile_cmd(arguments)
    return success, results

def getLocalModelPrediction():
    ''' 
    returns the profile result produced by Flame in summary format 
    '''
    # TODO: uses the label 'namastox', this does not allow concurrent use (colliding predictions)
    from flame import manage as flame_manage

    success, results = flame_manage.action_profiles_summary('namastox',output=None)
    if success:

        # initialize list of results 
        model=[]
        x_val=[]
        unc  =[]

        # when only one model is selected we predict twice as a workaround. Here we clean the duplicate
        if len (results) == 2 and results[0].getMeta('modelID') == results[1].getMeta('modelID'):
            results.pop(1)

        for ii in results:
            # append model info
            model.append((ii.getMeta("endpoint"),ii.getMeta("version")))

            #TODO get the real confidence value
            confidence = 80
            
            ival = ii.getVal("values")[0]            
            uncstr = ''
            
            if ii.getMeta("quantitative"):
                try:
                    ival = f'{ival:.4f}'
                except:
                    None

                if confidence != None:
                    cilow = ii.getVal('lower_limit')
                    ciup  = ii.getVal('upper_limit')

                    if cilow !=None and ciup != None:
                        cilow = float(cilow)
                        ciup = float(ciup)
                        print (cilow, ciup)
                        uncstr = f'{cilow:.4f} to {ciup:.4f} (%{confidence} conf.)'

            else:
                if ival == 0:
                    ival = 'negative'
                elif ival == 1:
                    ival = 'positive'
                else:
                    ival = 'uncertain'

                if confidence != None:
                    uncstr = f'(%{confidence} conf.)'
          
            x_val.append(ival)
            unc.append(uncstr)
        
        print ({'models':model, 'results':x_val, 'uncertainty': unc})
        return True, {'models':model, 'results':x_val, 'uncertainty': unc}
    else:
        return False, 'unable to retrieve prediction results'


def exportRA (raname):
    '''
    compresses (as tgz) the ra with the name of [ra].tgz and
    returns the file name
    '''
    current_path = os.getcwd()

    root_path = ra_repository_path()
    compressedfile = os.path.join(root_path, raname+'.tgz')

    with tarfile.open(compressedfile, 'w:gz') as tar:
        os.chdir(root_path)
        tar.add(os.path.join(raname))
        os.chdir(current_path)

    return True, compressedfile

def importRA (filename):
    '''
    imports the tgz file generated by the command export and decompresses it 
    in the ra repository creating a new funcional ra 
    '''
    root_path = ra_repository_path()
    raname = os.path.splitext(os.path.basename(filename))[0]
    base_path = os.path.join(root_path, raname)

    # safety checks
    if os.path.isdir(base_path):
        return False, f'RA {raname} already exists'

    # create directory
    try:
        os.mkdir(base_path)
    except Exception as e:
        return False, f'Error creating directory {base_path}: {e}'

    # unpack tar.gz. This is done for any kind of export file
    with tarfile.open(filename, 'r:gz') as tar:
        tar.extractall(root_path)

    return True, 'OK'

def attachmentsRA (raname):
    '''
    compresses (as tgz) the ra attachments with the name of the [ra]_repo.tgz and
    returns the file name
    '''
    current_path = os.getcwd()

    compressedfile = os.path.join(ra_repository_path(), raname+'_repo.tgz')

    with tarfile.open(compressedfile, 'w:gz') as tar:
        os.chdir(ra_repository_path())
        tar.add(os.path.join(raname,'repo'))
        os.chdir(current_path)

    return True, compressedfile

def getInfoStructure(molname=None, casrn=None):
    ''' 
    gets information for a substance, using either its name or its casrn, making 
    a call to a web service
    now we are using comptox dashboard
    TODO: use ASPA resources instead
    '''
    # COMPTOX URL
    url = "https://comptox.epa.gov/dashboard-api/batchsearch/chemicals"
    
    # Adding a payload
    if casrn != None:
        payload = {"identifierTypes":["CASRN"],"massError":0,"downloadItems":[],"searchItems":f"{casrn}","inputType":"IDENTIFIER"}
    elif molname != None:
        payload = {"identifierTypes":["chemical_name"],"massError":0,"downloadItems":[],"searchItems":f"{molname}","inputType":"IDENTIFIER"}

    ctx = create_urllib3_context()
    ctx.load_default_certs()
    ctx.options |= 0x4  # ssl.OP_LEGACY_SERVER_CONNECT

    with urllib3.PoolManager(ssl_context=ctx) as http:
        try:
            resp = http.request('POST', url, json=payload)
        except Exception as ins:
            return False, ins
        
        if resp.status==200:
            result = json.loads(resp.data)
            if result == []:
                return False, 'no compound found'
            return True, result

    return False, resp.status

def getTableContents (filename):

    LOG.info (f'import table {filename}')

    # use pandas CVS utility to import and convert to a dictionary
    table_dataframe = pd.read_csv(filename, sep=None).replace(np.nan, None)
    table_dict = table_dataframe.to_dict('records')

    # split in a values and uncertainties list, each item containing a dictionary with the required keys
    val_labels = ['parameter', 'value', 'unit']
    unc_labels = ['uncertainty', 'p', 'term']

    values = []
    uncertainties = []
        
    for item in table_dict:
        v_dict = {}
        u_dict = {}
        for v_label in val_labels:
            if v_label in item:
                v_dict[v_label] = item[v_label]
        
        values.append(v_dict)
    
        for u_label in unc_labels:
            if u_label in item:
                u_dict[u_label] = item[u_label]
            
        uncertainties.append(u_dict)
    
    if len(values)==0:
        return False, 'No value found', 'Aborted'

    return True, values, uncertainties