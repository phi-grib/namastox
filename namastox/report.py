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

from namastox.logger import get_logger
from namastox.ra import Ra
import os, yaml
import xlsxwriter

LOG = get_logger(__name__)

def report_excel (ra):
    reportfile = os.path.join (ra.rapath,'report.xlsx')

    if os.path.isfile(reportfile):
        try:
            os.remove(reportfile)
        except:
            return False, 'Failed! the report file is open or not writtable'
        
    workbook = xlsxwriter.Workbook(reportfile)
    worksheet = workbook.add_worksheet()

    # define styles and formats
    worksheet.set_column(0,0,width=40)
    worksheet.set_column(1,2,width=25)
    worksheet.set_column(3,3,width=60)
    worksheet.set_column(4,6,width=25)


    label_format = workbook.add_format({'align':'top', 'text_wrap': True, 'bold': True})
    value_format = workbook.add_format({'align':'top', 'text_wrap': True, 'font_color':'#3465A4'})

    # General section
    raitem = ra.general
    labels = ['title','endpoint', 'general_description', 'administration_route', 'regulatory_framework','species','background']

    irow =0 
    worksheet.write(irow, 0, 'General Information', label_format )
    for ilabel in labels:
        if not ilabel in raitem:
            continue
        worksheet.write(irow, 1, ilabel.replace('_',' '), label_format )
        worksheet.write(irow, 3, raitem[ilabel], value_format )
        irow+=1

    substances_items = ra.general['substances']
    substance_keys = ['name', 'casrn', 'id', 'smiles']
    
    for isubstance in substances_items:
        worksheet.write(irow, 1, 'substance', label_format ) 
        for ikey in substance_keys:
            if not ikey in isubstance:
                continue
            worksheet.write(irow, 2, ikey, label_format )
            worksheet.write(irow, 3, isubstance[ikey], value_format )
            irow+=1

    irow+=1

    # Results section

    bool_to_text = {True:'Yes', False:'No'}
    workflow = ra.workflow

    for reitem in ra.results:

        # Name and Description are not in results but in workflow
        inode = workflow.getNode(reitem['id'])
        itask = inode.getTask()
        idict = itask.getDescriptionDict()
        name = idict['task description']['name']
        description = idict['task description']['description']
        if 'label' in reitem:
            label = reitem['label']
        else:
            label = ''

        worksheet.write(irow, 0, name+f" ({label})", label_format )

        worksheet.write(irow, 1, 'description', label_format )
        worksheet.write(irow, 3, description, value_format )
        irow+=1
        
        worksheet.write(irow, 1, 'summary', label_format )
        worksheet.write(irow, 3, reitem['summary'], value_format )
        irow+=1

        if 'decision' in reitem:
            worksheet.write(irow, 1, 'decision', label_format )
            worksheet.write(irow, 3, bool_to_text[reitem['decision']], value_format )
            irow+=1

            worksheet.write(irow, 1, 'justification', label_format )
            worksheet.write(irow, 3, reitem['justification'], value_format )
            irow+=1
        
        else:
            if reitem['result_type'] == 'text':

                for iresult in reitem['values']:
                    worksheet.write(irow, 1, 'result', label_format )
                    worksheet.write(irow, 3, iresult, value_format )
                    irow+=1
                
                if 'uncertainties' in reitem:
                    for iresult in reitem['uncertainties']:
                        if 'p' in iresult and iresult['p'] > 0:
                            worksheet.write(irow, 1, 'confidence p', label_format )
                            worksheet.write(irow, 3, iresult['p'], value_format )
                            irow+=1
            
                        if 'term' in iresult and iresult['term'] != '':
                            worksheet.write(irow, 1, 'uncertainty', label_format )
                            worksheet.write(irow, 3, iresult['term'], value_format )
                            irow+=1

            elif reitem['result_type'] == 'value':
                        
                if len(reitem['values'])==len(reitem['uncertainties']):
                    worksheet.write(irow, 1, 'result', label_format )
                    
                    for iresult,iuncertain in zip(reitem['values'],reitem['uncertainties']):
                            
                        if 'parameter' in iresult:
                            worksheet.write(irow, 2, iresult['parameter'], label_format )
                            
                        if 'value' in iresult:
                            worksheet.write(irow, 3, iresult['value'], value_format )

                        if 'unit' in iresult and iresult['unit']!='':
                            worksheet.write(irow, 4, iresult['unit'], value_format )
                            
                        if 'p' in iuncertain and iuncertain['p'] != '0':
                            worksheet.write(irow, 5, f"conf: {iuncertain['p']}", value_format )
            
                        if 'term' in iuncertain and iuncertain['term'] != '':
                            worksheet.write(irow, 6, iuncertain['term'], value_format )
                            
                        irow+=1

                # fallback when the size of parameters and uncertainties don't match (this should never happen)
                else:
                    worksheet.write(irow, 1, 'result', label_format )
                    
                    for iresult in reitem['values']:
                            
                        if 'parameter' in iresult:
                            worksheet.write(irow, 2, iresult['parameter'], label_format )
                            
                        if 'value' in iresult:
                            worksheet.write(irow, 3, iresult['value'], value_format )

                        if 'unit' in iresult and iresult['unit']!='':
                            worksheet.write(irow, 4, iresult['unit'], value_format )
                    
                        irow+=1
                            
                    for iuncertain in reitem['uncertainties']:
                        if 'p' in iuncertain and iuncertain['p'] > 0:
                            worksheet.write(irow, 2, 'confidence', value_format )
                            worksheet.write(irow, 3, f"conf: {iuncertain['p']}", value_format )
                            irow+=1
            
                        if 'term' in iuncertain and iuncertain['term'] != '':
                            worksheet.write(irow, 2, 'uncertainty', value_format )
                            worksheet.write(irow, 3, iuncertain['term'], value_format )
                            irow+=1

    
        if len(reitem['links'])> 0:    
            worksheet.write(irow, 1, 'links', label_format )
            for ilink in reitem['links']:
                if 'include' in ilink and not ilink['include']:
                    continue 
                worksheet.write(irow, 2, ilink['label'].replace('_',' '), label_format )
                worksheet.write(irow, 3, ilink['File'], value_format )
                irow+=1

        worksheet.write(irow, 1, 'date', label_format )
        worksheet.write(irow, 3, reitem['date'], value_format )
        irow+=1

    irow+=1

    # Notes section
    for noitem in ra.notes:
        worksheet.write(irow, 0, f"{noitem['title']} ({noitem['id']})", label_format )
        worksheet.write(irow, 1, 'note', label_format )
        worksheet.write(irow, 3, noitem['text'], value_format )
        irow+=1
        worksheet.write(irow, 1, 'date', label_format )
        worksheet.write(irow, 3, noitem['date'], value_format )
        irow+=1
    
        irow+=1

    irow+=1
        
    # close workbook    
    workbook.close()

    return True, reportfile

def report_word (ra):

    print ('not implemented!')

    return False, 'not implemented'

def action_report (raname, report_format):

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load()

    if not succes:
        return False, results
    
    if report_format == 'yaml':
    
        reportfile = os.path.join (ra.rapath,'report.yaml')

        # include only "human interesting" sections
        dict_temp = {
            'general': ra.general, 
            'results': ra.results,
            'notes': ra.notes,
        }
        with open(reportfile,'w') as f:
            f.write(yaml.dump(dict_temp))

        return True, reportfile
    
    elif report_format == 'excel':

        return report_excel(ra)

    elif report_format == 'word':

        return report_word(ra)

    return False, 'format unsupported'

