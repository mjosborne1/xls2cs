"""
   fhir lighter library for building the fhir artefacts from the TSV input file 
"""

import json
import requests
import numpy as np
import pandas as pd
import logging

from fhirpathpy import evaluate
from fhirclient.models import codesystem


import os

logger = logging.getLogger(__name__)

def build_codesystem(srcfile,outdir,template,df2):
    """
    Build a codesystem based on a template file
    """
    print(f'...Building CodeSystem')

    cs_file = os.path.join(outdir,"CodeSystem.json")
    df1=pd.read_excel(srcfile,sheet_name="Example UCUM v1.5 2020_June", usecols=['code','display'], dtype={'code':str,'display':str})
    
    # Merge DataFrames with different column names
    cs_df = pd.merge(df1, df2, on='code', how='outer')
    # Remove duplicates
    unique_df = cs_df.drop_duplicates(subset=['code'], keep='first')    
    # Sort the DataFrame
    cs_sorted_df = unique_df.sort_values(by='code')

    print("Processing CodeSystem template...{0}".format(template))
    
    ## Drop any duplicate rows
    #df.drop_duplicates(subset=['CODE'], inplace=True)

    with open(template) as f:
        meta = json.load(f)
        cs = codesystem.CodeSystem()
        cs.id = meta.get("id")
        cs.status = meta.get('status')
        cs.name = meta.get('name')
        cs.title = meta.get('title')       
        cs.version = meta.get('version')
        cs.url = meta.get('url')
        cs.copyright = meta.get('copyright')
        cs.experimental = meta.get('experimental')
        cs.content = meta.get('content')       
        cs.concept = []        
        logger.info(f'CodeSystem: {cs.id} {cs.title}')
        for index, row in cs_sorted_df.iterrows():
            if str(row['code']) == 'nan':
                continue
            display = row['display_x']
            if str(row['display_x']) == 'nan':
                display = str(row['display_y'])    
            logger.info(f'{str(row['code'])}\t{display}')
            concept = codesystem.CodeSystemConcept()
            concept.code = str(row["code"])    
            concept.display = display           
            cs.concept.append(concept)
        
        with open(cs_file, "w") as f:
            json.dump(cs.as_json(), f, indent=2)   


## get_valueset_using_params
## Generic Valueset getter, pass an endpoint for the expansion and a parameters file name
## return a pandas dataframe containing the code, display pairs.
def get_valueset_using_params(endpoint,params_file):
    with open(params_file) as f:
        params = json.load(f)
    url = f'{endpoint}/ValueSet/$expand'
    headers = {'Content-Type': 'application/fhir+json'}
    response = requests.post(url, headers=headers, data=json.dumps(params))

    merge_values = []
    if response.status_code == 200:
        data = response.json()
        expansion = evaluate(data,"expansion.contains")
        for entry in expansion:
            code = entry.get("code", {})
            display = entry.get("display", {})
            merge_values.append({"code": code, "display": display })
            #logger.info(f'{code},{display}')
    df2 = pd.DataFrame(merge_values)
    return df2



## Mainline
## Output the CodeSystem from the source file    
def run_main(srcfile,outdir,template):   
    endpoint = 'https://tx.dev.hl7.org.au/fhir'   
    params_file='params.json'
    # Get the current UCUM CodeSystem as a dict to merge in
    merge_values = get_valueset_using_params(endpoint,params_file)
    # Create a new CodeSystem using the values from the Current code system and the ucum spreadsheet    
    build_codesystem(srcfile,outdir,template,merge_values)
   
