import argparse
import os
import lighter
import logging
from datetime import datetime

def main():
    """
    Create a FHIR CodeSystem from an XLS File
    """
    
    homedir=os.environ['HOME']
    parser = argparse.ArgumentParser()
    infiledefault=os.path.join(homedir,"data","ucum","in","TableOfExampleUcumCodesForElectronicMessaging.xlsx")
    templatedefault=os.path.join(homedir,"data","ucum","CodeSystemTemplate.json")
    outdirdefault=os.path.join(homedir,"data","ucum","out")
    #endpoint_default="https://r4.ontoserver.csiro.au/fhir"
    endpoint_default="http://localhost:8080/fhir"

    logger = logging.getLogger(__name__)
    parser.add_argument("-i", "--infile", help="infile path for excel file", default=infiledefault)
    parser.add_argument("-o", "--outdir", help="dir name for file output", default=outdirdefault)
    parser.add_argument("-t", "--template", help="CodeSystem file path", default=templatedefault)
    parser.add_argument("-p", "--publish", help="Endpoint to publish on or blank", default="")
    args = parser.parse_args()
    now = datetime.now() # current date and time
    ts = now.strftime("%Y%m%d-%H%M%S")
    logsdir=os.path.join(homedir,"data","ucum","logs")
    FORMAT='%(asctime)s %(lineno)d : %(message)s'
    logging.basicConfig(format=FORMAT, filename=os.path.join(logsdir,f'xls2cs-{ts}.log'),level=logging.INFO)
    logger.info('Started')
    
    lighter.run_main(args.infile,args.outdir,args.template)
    logger.info("Finished")

if __name__ == '__main__':
    main()