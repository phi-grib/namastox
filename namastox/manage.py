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
import requests
import urllib3
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
    radir = ra_path(raname)
    rahist = os.path.join(radir,'hist')
    if not os.path.isdir(rahist):
        return False, f'Historic repository for risk assessment {raname} not found'

    for ra_hist_file in os.listdir(rahist):
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
    removes the ra tree described by the argument
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
    In no argument is provided lists all ranames present at the repository 
     otherwyse lists all versions for the raname provided as argument
    '''

    rdir = ra_repository_path()
    if os.path.isdir(rdir) is False:
        return False, 'The risk assessment name repository path does not exist. Please run "namastox -c config".'

    output = []
    num_ranames = 0
    LOG.info('Risk assessment(s) found in repository:')
    for x in os.listdir(rdir):
        xpath = os.path.join(rdir,x) 
        # discard if the item is not a directory
        if not os.path.isdir(xpath):
            continue

        num_ranames += 1
        LOG.info('\t'+x)
        output.append(x)

    LOG.debug(f'Retrieved list of risk assessments from {rdir}')
    
    # web-service
    if out=='json':
        return True, output
        # return output

    return True, f'{num_ranames} risk assessment(s) found'

def action_steps(raname, out='text'):
    '''
    Provides a list with all steps for ranames present at the repository 
    '''

    radir = ra_path(raname)
    rahist = os.path.join(radir,'hist')
    if not os.path.isdir(rahist):
        return False, f'Historic repository for risk assessment {raname} not found'

    steps = []
    for ra_hist_file in os.listdir(rahist):
        ra_hist_item = os.path.join(rahist, ra_hist_file)
        if os.path.isfile(ra_hist_item):
            idict = {}
            with open(ra_hist_item, 'r') as pfile:
                idict = yaml.safe_load(pfile)
                if 'ra' in idict:
                    if 'step' in idict['ra']:
                        steps.append(idict['ra']['step'])
                        LOG.info(f'step: {steps[-1]}')
    
    LOG.debug(f'Retrieved list of steps from {rahist}')

    # web-service
    if out=='json':
        return True, steps

    return True, f'{len(steps)} steps found'

def action_info(raname, out='text'):
    '''
    Provides a list with all steps for ranames present at the repository 
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

        # obtain the SMILES
        ismiles = Chem.MolToSmiles(mol)

        results.append( {'name': iname, 'SMILES': ismiles, 'CASRN': icasrn })

    if len(results)> 0:
        return True, results

    return False, 'empty molecule'

def getLocalModels ():
    from flame import manage as flame_manage

    results = []
    success, models = flame_manage.action_dir()
    if not success:
        return False, results
    
    for imodel in models:
        results.append((imodel['modelname'], imodel['version']))

    return True, results

def predictLocalModels (raname, models, versions):

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
    if 'substance_SMILES' in generalInfo:

        # extract SMILES and write a SDFile in RA repository
        smiles = generalInfo['substance_SMILES'][0]['SMILES']
        mol = Chem.MolFromSmiles(smiles)
        writer = Chem.SDWriter(structure_sdf)
        writer.write(mol)
        writer.close()

        # predicts
        arguments = {'label' : 'namastox',
                     'infile': structure_sdf,
                     'multi' : {'endpoints': models, 
                               'versions': versions}
                     }
        success, results = context.profile_cmd(arguments)
        return True, results

    else:
        return False, f'no substance defined in {raname}'

def getLocalModelPrediction():
    from flame import manage as flame_manage

    success, results = flame_manage.action_profiles_summary('namastox',output="summary")
    if success:
        return True, results
    else:
        return False, 'unable to retrieve prediction results'

def exportRA (raname):

    current_path = os.getcwd()

    root_path = ra_repository_path()
    compressedfile = os.path.join(root_path, raname+'.tgz')

    with tarfile.open(compressedfile, 'w:gz') as tar:
        os.chdir(root_path)
        tar.add(os.path.join(raname))
        os.chdir(current_path)

    return True, compressedfile


def importRA (filename):

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


class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')

        self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx)


def getInfoStructure(molname=None, casrn=None):

    # URL from COMPTOX
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
        resp = http.request('POST', url, json=payload)
        if resp.status==200:
            rdict = json.loads(resp.data)
            # print (rdict)
            return True, rdict

    return False, resp.status
