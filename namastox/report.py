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
    
    elif report_format == 'excel':

        reportfile = os.path.join (ra.rapath,'report.xlsx')
        
        workbook = xlsxwriter.Workbook(reportfile)
        worksheet = workbook.add_worksheet()

        # define styles
        worksheet.set_column(0,2,width=25)
        worksheet.set_column(3,3,width=60)

        label_format = workbook.add_format()
        label_format.set_align('top') 
        
        value_format = workbook.add_format()
        value_format.set_text_wrap() 
        value_format.set_align('top') 

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

        for reitem in ra.results:
            #TODO use a more descriptive label
            worksheet.write(irow, 0, reitem['id'], label_format )

            worksheet.write(irow, 1, 'date', label_format )
            worksheet.write(irow, 3, reitem['date'], value_format )
            irow+=1
            
            worksheet.write(irow, 1, 'summary', label_format )
            worksheet.write(irow, 3, reitem['summary'], value_format )
            irow+=1

            if len(reitem['links'])> 0:            
                worksheet.write(irow, 1, 'links', label_format )
                for ilink in reitem['links']:
                    worksheet.write(irow, 2, ilink['label'].replace('_',' '), label_format )
                    worksheet.write(irow, 3, ilink['File'], value_format )
                    irow+=1

            if 'decision' in reitem and reitem['decision']:
                worksheet.write(irow, 1, 'decision', label_format )
                worksheet.write(irow, 3, bool_to_text[reitem['report']], value_format )
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
                    
                    for iresult in reitem['uncertainties']:
                        if iresult['p'] > 0:
                            worksheet.write(irow, 2, 'p', label_format )
                            worksheet.write(irow, 3, iresult['p'], value_format )
                            irow+=1
            
                        if iresult['term'] != '':
                            worksheet.write(irow, 2, 'term', label_format )
                            worksheet.write(irow, 3, iresult['term'], value_format )
                            irow+=1
    
                #TODO: valores numéricos

            irow+=1




        #TODO: Notes section

        # close workbook    
        workbook.close()

    else:
        return False, 'format unsupported'

    return True, reportfile



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

