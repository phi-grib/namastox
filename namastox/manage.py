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
from flame.util.utils import profiles_repository_path, model_repository_path


LOG = get_logger(__name__)

def action_privileges(raname, username):
    return Ra(raname, username).privileges(username)

def action_newFolder(foldername, username, shared):
    '''
    Create a new folder, to organise RAs, using the given name.
    '''
    if not foldername:
        return False, 'empty folder name'

    # importlib does not allow using 'test' and issues a misterious error when we
    # try to use this name. This is a simple workaround to prevent creating ranames 
    # with this name 
    if foldername == 'test':
        return False, 'the name "test" is disallowed, please use any other name'

    # folder directory with /dev (default) level
    ndir = ra_path(foldername, username)

    if os.path.isdir(ndir):
        return False, f'Folder {foldername} already exists'
    try:
        os.mkdir(ndir)
    except:
        return False, f'Unable to create path for {foldername} endpoint'

    return True, f'New folder {foldername} created'


def action_new(raname, username, shared, currentContextItem):
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
    if currentContextItem and '_folder_' not in currentContextItem:
        ndir = ra_path(raname, username)
    else:
        ndir = ra_path(raname, username,currentContextItem)

    if os.path.isdir(ndir):
        return False, f'Risk assessment {raname} already exists'
    try:
        os.makedirs(ndir)
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
    ra = Ra(raname, username)

    # Default to universal read/write access
    if shared:
        ra.setUsers(['*'],['*'],ndir)
    else:
        ra.setUsers([username], [username],ndir)

    success, results = ra.load()
    if not success:
        return False, results
    

    # Include RA information 
    ra.setVal('ID', id_generator() )

    # Save
    ra.save()

    # Show template
    yaml = ra.getTemplate()
    
    return True, f'New risk assessment {raname} created'

def action_clone(source_raname, username):
    '''
    Clone an existing risk assessment tree, using the given name.
    '''
    if not source_raname:
        return False, 'empty risk assessment name'

    # importlib does not allow using 'test' and issues a misterious error when we
    # try to use this name. This is a simple workaround to prevent creating ranames 
    # with this name 

    # raname directory with /dev (default) level
    source_rapath = ra_path(source_raname, username)

    # raname directory with /dev (default) level
    seq_count = 0
    while True:
        raname = source_raname+f'({seq_count})'
        rapath = os.path.join(source_rapath+f'({seq_count})')
        if os.path.isdir(rapath):
            seq_count+=1
        else:
            break

    shutil.copytree(source_rapath, rapath)

    LOG.debug(f'cloned RA {source_raname} to {raname}')

    # Instantiate Ra
    ra = Ra(raname, username)
    
    # # Default to universal read/write access
    # ra.setUsers(['*'],['*'])

    success, results = ra.load()
    if not success:
        return False, results

    # Include RA information 
    ra.setVal('ID', id_generator() )

    # Save
    ra.save()

    return True, f'New risk assessment {raname} cloned from {source_raname}'

def action_rename(ra_name, username, ra_newname):
    '''
    Rename an existing risk assessment tree, using the given name.
    '''
    if not ra_name:
        return False, 'empty risk assessment name'
    
    # importlib does not allow using 'test' and issues a misterious error when we
    # try to use this name. This is a simple workaround to prevent creating ranames 
    # with this name 
    if ra_newname == 'test':
        return False, 'the name "test" is disallowed, please use any other name'
    
    rapath = ra_path(ra_name, username)
    ranewpath = os.path.join(os.path.dirname(rapath), ra_newname)
    
    if not os.path.isdir(rapath):
        return False, f'{rapath} folder not found in the repository'

    if os.path.isdir(ranewpath):
        return False, f'RA name "{ranewpath}" already in use, select a different name'
    
    shutil.move(rapath, ranewpath)

    LOG.debug(f'renamed RA {rapath} to {ranewpath}')

    return True, f'RA {rapath} renamed to {ranewpath}'

def action_renameFolder(oldFolderName, username, newFolderName):
    '''
    Rename an existing folder, using the given name.
    '''
    if not oldFolderName:
        return False, 'empty folder name'
    
    # importlib does not allow using 'test' and issues a misterious error when we
    # try to use this name. This is a simple workaround to prevent creating ranames 
    # with this name 
    if newFolderName == 'test':
        return False, 'the name "test" is disallowed, please use any other name'

    #ra_path creates the path for RA and for FOLDERS
    folderpath = ra_path(oldFolderName, username)
    folderNewpath = os.path.join(os.path.dirname(folderpath), newFolderName)
    
    if not os.path.isdir(folderpath):
        return False, f'{folderpath} folder not found in the repository'

    if os.path.isdir(folderNewpath):
        return False, f'RA name "{folderNewpath}" already in use, select a different name'
    
    shutil.move(folderpath, folderNewpath)

    LOG.debug(f'renamed RA {folderpath} to {folderNewpath}')

    return True, f'RA {folderpath} renamed to {folderNewpath}'

def getRaHistoric (raname, username, step):
    ''' retrieves from the historical record the item corresponding to the step given as argument
    '''
    radir = ra_path(raname, username)
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

def action_kill(raname, username):
    '''
    removes the ra tree
    '''
    if not raname:
        return False, 'Empty risk assessment name'

    ndir = ra_path(raname, username)

    if not os.path.isdir(ndir):
        return False, f'Risk assessment {raname} not found'

    # Remove the whole tree
    try:
        shutil.rmtree(ndir, ignore_errors=True)
    except:
        return False, f'Failed to remove risk assessment {raname}'

    return True, f'Risk assessment {raname} removed'

def action_deleteFolder(folder_name, username):
    '''
    removes the folder tree
    '''
    if not folder_name:
        return False, 'Empty folder name'

    ndir = ra_path(folder_name, username)

    if not os.path.isdir(ndir):
        return False, f'Folder {folder_name} not found'

    # Remove the whole tree
    try:
        shutil.rmtree(ndir, ignore_errors=True)
    except:
        return False, f'Failed to remove folder {folder_name}'

    return True, f'Folder {folder_name} removed'



def action_backwards(raname, username):
    '''
    removes the last step from the ra tree 
    '''
    if not raname:
        return False, 'Empty risk assessment name'

    ndir = ra_path(raname, username)

    if not os.path.isdir(ndir):
        return False, f'Risk assessment {raname} not found'

    # load RA
    ra = Ra(raname, username)
    success, results = ra.load()
    if not success:
        return False, results

    # get last step (step)
    step = ra.getVal('step')
    if step == 1:
        return False, 'the last step cannot be removed!'

    new_step = step -1 
  
    # find the previous step in the repo and copy as ra.yaml overwriting existing file
    success, ra_new = getRaHistoric(raname, username, new_step)
    if not success:
        return False, f'no step found!'

    shutil.copy(ra_new, os.path.join(ndir,'ra.yaml'))
    
    # remove the ra to delete 
    success, ra_delete = getRaHistoric(raname, username, step)
    if not success:
        return False, f'unable to remove file {ra_delete}'

    os.remove(ra_delete)

    return True, 'OK'


def action_list(username):
    '''
    if no argument is provided lists all ranames present at the repository 
    otherwyse lists all versions for the raname provided as argument
    '''
    output_user = []
    output_shared = []
    
    rdir = ra_repository_path(username)
    if os.path.isdir(rdir) is False:
        return False, 'The risk assessment name repository path does not exist. Please run "namastox -c config".'

    # for ra_name in os.listdir(rdir):
    #     ra_path = os.path.join(rdir,ra_name) 

    #     # discard if the item is not a directory
    #     if not os.path.isdir(ra_path):
    #         continue

    #     # discard if we don't have privileges
    #     ra = Ra(ra_name, username)
    #     if not 'r' in ra.privileges(username):
    #         continue

    #     output_user.append(ra_name)

    #now ra_name = ra name or folder name
    for ra_name in os.listdir(rdir):
        ra_path = os.path.join(rdir, ra_name)

        # discard if the item is not a directory
        if not os.path.isdir(ra_path):
            continue

        # is a container folder (_folder_)
        if '_folder_' in ra_name:
            folder_RAs = []

            for childFolder_name in os.listdir(ra_path):
                childFolder_path = os.path.join(ra_path, childFolder_name)

                # discard if the item is not a directory
                if not os.path.isdir(childFolder_path):
                    continue

                folder_RAs.append(childFolder_name)
            #in this case, ra_name is the name of the folder
            output_user.append({
                'folder': ra_name, # folder = folder name
                'items': folder_RAs # items = list of RAs inside the folder
            })

            continue

        # is a RA 
        ra = Ra(ra_name, username)

        if 'r' not in ra.privileges(username):
            continue

        output_user.append(ra_name)

    LOG.debug(f'Retrieved list of risk assessments from {rdir}')

    rdir = ra_repository_path('shared')
    if os.path.isdir(rdir) is False:
        return False, 'The risk assessment name repository path does not exist. Please run "namastox -c config".'

    #now ra_name = ra name or folder name
    for ra_name in os.listdir(rdir):
        ra_path = os.path.join(rdir,ra_name) 

        # discard if the item is not a directory
        if not os.path.isdir(ra_path):
            continue

        # is a container folder (_folder_)
        if '_folder_' in ra_name:
            folder_RAs = []

            for childFolder_name in os.listdir(ra_path):
                childFolder_path = os.path.join(ra_path, childFolder_name)
                print(childFolder_path)
                # discard if the item is not a directory
                if not os.path.isdir(childFolder_path):
                    continue
                
                # discard if we don't have privileges
                # ra = Ra(childFolder_name, 'shared')
                # if not 'r' in ra.privileges(username):
                #     continue
                
                folder_RAs.append(childFolder_name)

            output_shared.append({
                'folder': ra_name,
                'items': folder_RAs
            })

            continue
        else: 
            # discard if we don't have privileges
            ra = Ra(ra_name, 'shared')
            if not 'r' in ra.privileges(username):
                continue

            output_shared.append(ra_name)

    LOG.debug(f'Retrieved list of risk assessments from {rdir}')
    
    # web-service
    result = {username: output_user,
              'shared': output_shared}
    return True, result


def action_setusers(raname, username, users_read, users_write):
    ra = Ra(raname, username)
    ra.setUsers(users_read, users_write)

def action_getusers(raname, username):
    ra = Ra(raname, username)
    return ra.getUsers()

def action_steps(raname, username, out='text'):
    '''
    provides a list with all steps for ranames present at the repository 
    '''
    radir = ra_path(raname, username)
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

def action_info(raname, username, out='text'):
    '''
    provides a list with all steps for ranames present at the repository 
    '''
    # instantiate a ra object
    ra = Ra(raname, username)

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

def getPath(raname, username):
    '''
    returns the path to the RA folder for ra raname
    '''
    return True, ra_path(raname, username)

def getRepositoryPath(raname, username):
    '''
    returns the path to the repository folder for ra raname
    '''
    repo_path = os.path.join(ra_path(raname, username), 'repo')
    return True, repo_path

def getModelPath():
    return model_repository_path()

def getWorkflow(raname, username, step=None):
    '''
    returns a marmaid string describing the "visible workflow"
    '''

    # instantiate a ra object
    ra = Ra(raname, username)
    succes, results = ra.load()
    if not succes:
        return False, results
    
    workflow_graph = ra.getWorkflowGraph(step)
    return (workflow_graph is not None), workflow_graph

def getCatalogue(raname, username):
    '''
    returns a marmaid string describing the "visible workflow"
    '''

    # instantiate a ra object
    ra = Ra(raname, username)
    succes, results = ra.load()
    if not succes:
        return False, results
    
    workflow_graph = ra.getCatalogueGraph()

    return (workflow_graph is not None), workflow_graph

def setCustomWorkflow (raname, username, file):
    '''
    defines the file provided as argument as a custom workflow
    '''
    # instantiate a ra object
    ra = Ra(raname, username)

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

def saveModelDocumentation (model_name, model_ver,  oformat='WORD'):
    from flame import manage as flame_manage
    success, results = flame_manage.action_documentation(model_name, model_ver, oformat=oformat)
    # results will contains errors if success and the output filename otherwise
    return success, results

def predictLocalModels (raname, username, models, versions):
    ''' returns a prediction using the substance defined in the ra, using the list of local models and versions specified
    '''
    from flame import context

    # instantiate a ra object
    ra = Ra(raname, username)
    succes, results = ra.load()
    if not succes:
        return False, results
    
    success, ra_repo_path = getRepositoryPath (raname)
    structure_sdf = os.path.join(ra_repo_path,'structure.sdf')

    generalInfo = ra.getGeneralInfo()
    generalInfo = generalInfo['general']
    if 'substances' in generalInfo:
        generalSubst = generalInfo['substances']
    else:
        return False, 'no substance defined in {raname}'
    smiles = []
    names = []

    # extract SMILES and write a SDFile in RA repository
    for isubst in generalSubst:
        if 'smiles' in isubst: 
            smiles.append(isubst['smiles'])
        if 'name' in isubst:
            names.append(isubst['name'])
    
    if len(smiles) == 0:
        return False, f'no substance defined in {raname}'
    
    if len(smiles) != len (names):
        return False, f'every substance should have an SMILES and a name defined in {raname}'

    writer = Chem.SDWriter(structure_sdf)
    n = 0
    for ismiles,iname in zip(smiles, names):
        try:
            mol = Chem.MolFromSmiles(ismiles)
        except:
            writer.close()
            return False, f'incorrect SMILES format: {ismiles}'
        
        if mol != None:
            mol.SetProp("name",iname)
            mol.SetProp("_Name",iname)
            writer.write(mol)
        
        n+=1

    writer.close()

    # profile requires more than one model selected
    # if only one model is selected, run the prediction twice
    if len(models)==1:
        models.append(models[0])
        versions.append(versions[0])

    label = f'namastox_{id_generator()}'    

    arguments = {'label' : label,
                 'infile': structure_sdf,
                 'multi' : {'endpoints': models, 
                            'versions': versions}
                }
    
    success, results = context.profile_cmd(arguments)
    if success:
        return True, label
    
    return success, results

def getLocalModelPrediction(raname, username, prediction_label):
    ''' 
    returns the profile result produced by Flame in summary format 
    '''
    # TODO: uses the label 'namastox', this does not allow concurrent use (colliding predictions)
    from flame import manage as flame_manage

    success, results = flame_manage.action_profiles_summary(prediction_label,output=None)
    if success:

        # initialize list of results 
        model=[]
        units=[]
        parameters=[]
        interpretations=[]
        methods = []

        nmol =  results[0].getVal('obj_num')
        mol_names =  results[0].getVal('obj_nam')

        x_val = [[] for _ in range(nmol)] 
        unc = [[] for _ in range(nmol)]

        # when only one model is selected we predict twice as a workaround. Here we clean the duplicate
        if len (results) == 2 and results[0].getMeta('modelID') == results[1].getMeta('modelID'):
            results.pop(1)

        for ii in results:

            # variables for facilitating access to key information
            iendpoint = ii.getMeta("endpoint")
            iversion = ii.getMeta("version")
            iquantitative = ii.getMeta("quantitative")

            # defaults
            confidence = None
            unit = ''
            parameter = iendpoint
            interpretation = ''
            uncstr = ''
            imethod = {}

            # extract model information from the documentation
            success, documentation = getModelDocumentation(iendpoint,iversion)

            if success:
                if 'AD_parameters' in documentation:
                    if 'confidence' in documentation['AD_parameters']:
                        confidence = documentation['AD_parameters']['confidence']
                        if confidence is not None:
                            confidence*=100.0

                if iquantitative:
                    if 'Endpoint_units' in documentation:
                        if documentation['Endpoint_units'] != 'None':
                            unit = documentation['Endpoint_units']
    
                if 'Endpoint' in documentation:
                    if documentation['Endpoint'] != 'None':
                        parameter = documentation['Endpoint']
    
                if 'Interpretation' in documentation:
                    interpretation = documentation['Interpretation']

                success, docfile = saveModelDocumentation(iendpoint,iversion)
                if success:
                    destpath = os.path.join (ra_path(raname, username), 'repo', docfile)
                    if os.path.isfile(destpath):
                        os.remove(destpath)
                    if os.path.isfile(docfile):
                        shutil.move(docfile, destpath)

            # Generate pseudo-method:
            imethod['name'] = iendpoint
            imethod['description'] = interpretation
            imethod['link'] = f'documentation_{iendpoint}v{iversion}.docx'

            # Iterate for every substance j
            mollist = ii.getVal("values")
            for j, ival in enumerate(mollist):

                if iquantitative:
                    try:
                        ival = f'{ival:.4f}'
                    except:
                        None

                    imethod['sd'] = documentation['Internal_validation_1']['SDEP']

                    if confidence != None:
                        cilow = ii.getVal('lower_limit')[j]
                        ciup  = ii.getVal('upper_limit')[j]

                        if cilow !=None and ciup != None:
                            cilow = float(cilow)
                            ciup = float(ciup)
                            uncstr = f'{cilow:.4f} to {ciup:.4f} (%{confidence} conf.)'

                else:
                    if ival == 0:
                        ival = 'negative'
                    elif ival == 1:
                        ival = 'positive'
                    else:
                        ival = 'uncertain'

                    imethod['specificity'] = documentation['Internal_validation_1']['Specificity']
                    imethod['sensitivity'] = documentation['Internal_validation_1']['Sensitivity']

                    if confidence != None:
                        uncstr = f'%{confidence} conf.'


                x_val[j].append(ival)
                unc[j].append(uncstr)

            model.append((iendpoint, iversion))
            units.append(unit)
            parameters.append(parameter)
            interpretations.append(interpretation)
            methods.append(imethod)
        
        # reformat list so they can be easily presented
        extmodel = []
        extparameters = []
        extunits = []
        extinterpretations = []
        extmethods = []

        extval = []
        extunc = []

        extmolnames = []

        for i in range(nmol):

            for j in range(len(model)):
                extmolnames.append(mol_names[i])
                extval.append(x_val[i][j])
                extunc.append(unc[i][j])

            for iitem in model:
                extmodel.append(iitem)
            for iitem in parameters:
                extparameters.append(iitem)
            for iitem in units:
                extunits.append(iitem)
            for iitem in interpretations:
                extinterpretations.append(iitem)
            for iitem in methods:
                extmethods.append(iitem)

        # print ({'molnames': extmolnames, 'models':extmodel, 'results':extval, 'uncertainty': extunc, 
        #         'parameters': extparameters, 'units': extunits, 'interpretations': extinterpretations, 'methods': extmethods})
        
        shutil.rmtree(os.path.join(profiles_repository_path(), prediction_label))
        
        return True, {'molnames': extmolnames, 'models':extmodel, 'results':extval, 'uncertainty': extunc, 'parameters': extparameters, 'units': extunits, 'interpretations': extinterpretations, 'methods': extmethods}
    else:
        return False, f'unable to retrieve prediction results with error: {results}'


def exportRA (raname, username):
    '''
    compresses (as tgz) the ra with the name of [ra].tgz and
    returns the file name
    '''
    current_path = os.getcwd()

    if raname[0] == '+':  # RA is in shared folder 
        username = 'shared'

    root_path = ra_repository_path(username)
    compressedfile = os.path.join(root_path, raname+'.tgz')

    with tarfile.open(compressedfile, 'w:gz') as tar:
        os.chdir(root_path)
        tar.add(raname)
        os.chdir(current_path)

    return True, compressedfile

def importRA (filename, username):
    '''
    imports the tgz file generated by the command export and decompresses it 
    in the ra repository creating a new funcional ra 
    '''

    raname = os.path.splitext(os.path.basename(filename))[0]

    root_path = ra_repository_path(username)
    base_path = os.path.join(root_path, raname)

    # safety checks
    if os.path.isdir(base_path):
        return False, f'RA {raname} already exists'

    # # create directory
    # try:
    #     os.mkdir(base_path)
    # except Exception as e:
    #     return False, f'Error creating directory {base_path}: {e}'

    # unpack tar.gz. This is done for any kind of export file
    with tarfile.open(filename, 'r:gz') as tar:
        tar.extractall(root_path)

    return True, 'OK'

def attachmentsRA (raname, username):
    '''
    compresses (as tgz) the ra attachments with the name of the [ra]_repo.tgz and
    returns the file name
    '''
    current_path = os.getcwd()

    if raname[0] == '+': # in shared folder
        username = 'shared'

    compressedfile = os.path.join(ra_repository_path(username), raname+'_repo.tgz')

    with tarfile.open(compressedfile, 'w:gz') as tar:
        os.chdir(ra_repository_path(username))
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
    val_labels = ['substance', 'method', 'parameter', 'value', 'unit']
    unc_labels = ['uncertainty', 'term']

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