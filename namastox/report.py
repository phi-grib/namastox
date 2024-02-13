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

os.environ['OPENBLAS_CORETYPE']='haswell'

import xlsxwriter



LOG = get_logger(__name__)

def action_report (raname, report_format):

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load()

    if not succes:
        return False, results
    
    dict_temp = {
        'ra': ra.ra,
        'general': ra.general, 
        'results': ra.results,
        'notes': ra.notes,
    }

    if report_format == 'yaml':
    
        reportfile = os.path.join (ra.rapath,'report.yaml')
        with open(reportfile,'w') as f:
            f.write(yaml.dump(dict_temp))
        return True, reportfile
    
    elif report_format == 'excel':

        reportfile = os.path.join (ra.rapath,'report.xlsx')
        
        workbook = xlsxwriter.Workbook(reportfile)
        worksheet = workbook.add_worksheet()

        worksheet.write('A1', 'Hello world')

        workbook.close()
        return True, reportfile

    
        # ws.title = f"RA {raname} report" 
        # alignment_style = Alignment(vertical='top',wrapText=True)

        # try:    
        #     wb.save(reportfile)
        #     return True, reportfile
        # except:
        #     return False, f'error saving report as {reportfile}'

    else:
        print ('format unknown')

    return False, None



def dumpExcel (self,oname):
    return True

            # wb = Workbook() 
            # ws = wb.active 
            # ws.title = f"Model {self.model} documentation" 
            # alignment_style = Alignment(vertical='top',wrapText=True)
            
            # # Label Style
            # Label = NamedStyle(name="Label")
            # Label.font = Font(name='Calibri',size=11,bold=True)
            # Label.alignment = alignment_style
            
            # ws.column_dimensions['A'].width = 25.10
            # ws.column_dimensions['B'].width = 28.00
            # ws.column_dimensions['C'].width = 60.00
            # ws.column_dimensions['D'].width = 60.00

            # # sections of the document, specifying the document keys which will be listed
            # sections = [('General model information',['ID', 'Version', 'Model_title', 'Model_description', 'Keywords', 'Contact', 'Institution', 'Date', 'Endpoint',
            #             'Endpoint_units', 'Interpretation', 'Dependent_variable', 'Species',
            #             'Limits_applicability', 'Experimental_protocol', 'Model_availability',
            #             'Data_info']), 
            #             ('Algorithm and software',['Algorithm', 'Software', 'Descriptors', 'Algorithm_settings',
            #             'AD_method', 'AD_parameters', 'Goodness_of_fit_statistics',
            #             'Internal_validation_1', 'Internal_validation_2', 'External_validation',
            #             'Comments']),
            #             ('Other information',['Other_related_models', 'Date_of_QMRF', 'Date_of_QMRF_updates',
            #             'QMRF_updates', 'References', 'QMRF_same_models', 'Mechanistic_basis', 
            #             'Mechanistic_references', 'Supporting_information', 'Comment_on_the_endpoint',
            #             'Endpoint_data_quality_and_variability', 'Descriptor_selection'])]

            # #Save the position and name of the label for the first and last section
            # position = []
            # name = [sections[0][1][0],'Other Comments']
            
            # count = 1
            # for isection in sections:

            #     for ik in isection[1]:
                 
            #         label_k = ik.replace('_',' ')

            #         if label_k == 'Internal validation 2' or label_k == 'External validation':
            #             ws[f"A{count}"] = label_k
            #             ws[f'A{count}'].style = Label
            #         else:
            #             ws[f"B{count}"] = label_k
            #             ws[f"B{count}"].style = Label

            #         if ik in self.fields:
            #             # set defaults for value
            #             ivalue= ''
            #             #v is the selected entry in the documentation dictionary
            #             v = self.fields[ik]
            #             ## newest parameter formats are extended and contain
            #             ## rich metainformation for each entry
            #             if 'value' in v:
            #                 ivalue = v['value']
                             
            #                 if isinstance(ivalue,dict):

            #                     ws[f"A{count}"] = label_k
            #                     ws[f"A{count}"].style = Label
                                
            #                     end = (count)+(len(ivalue)-1)

            #                     for intk in ivalue:
            #                         label_ik = intk.replace('_',' ')
            #                         # label_ik = intk.replace('_f', '').replace('_', ' ')
            #                         ws[f'B{count}'] = label_ik
            #                         ws[f'B{count}'].style = Label
                                    
                                     
            #                         intv = ivalue[intk]
            #                         if not isinstance(intv,dict):
                                        
            #                             iivalue = intv
            #                             if iivalue is None:
            #                                 iivalue = " "
            #                         else:
            #                             intv = ivalue[intk]
            #                             iivalue = ''
            #                             if 'value' in intv:
            #                                 iivalue = intv["value"]
            #                             if iivalue is None:
            #                                 iivalue = ''

            #                             ws[f'D{count}'] = intv['description']
            #                             ws[f'D{count}'].alignment = alignment_style

                                        
            #                         ws[f'C{count}'] = f'{str(iivalue)}'
            #                         ws[f'C{count}'].font = Font(name='Calibri',size=11,color='3465a4')
            #                         ws[f'C{count}'].alignment = alignment_style
                                    
            #                         ws.merge_cells(f'A{count}:A{end}')
                                 
            #                         count +=1
                                               
            #                 else:

            #                     ws[f'D{count}'] = v['description']
            #                     ws[f'D{count}'].alignment = alignment_style

            #                     if label_k == 'Experimental protocol' or label_k == 'Comments':
            #                         position.append(count)
                                    
            #                     if ivalue is None:
            #                         ivalue = ''

            #                     ws[f'C{count}'] = f'{str(ivalue)}'
            #                     ws[f'C{count}'].font = Font(name='Calibri',size=11,color='3465a4')
            #                     ws[f'C{count}'].alignment = alignment_style

                                
            #                     count += 1
            
            # itr = 0
            # for i in position:
            #     if itr == 0:    
            #         ws[f'A{1}'] = name[itr]
            #         ws[f"A{1}"].style = Label
            #         ws.merge_cells(f'A{1}:A{i}')
            #     else:
            #         ws[f'A{i}'] = name[itr]
            #         ws[f"A{i}"].style = Label
            #         ws.merge_cells(f'A{i}:A{count-1}')

            #     itr +=1

            # try:    
            #     wb.save(oname)
            # except:
            #     return False, f'error saving document as {oname}'
            
            # return True, 'OK'

