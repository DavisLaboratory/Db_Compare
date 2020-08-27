import os
import glob
import sys

# input the file containing the UIDs for the databases HPRD, Reactome KEGG, WikiPathways and PhosphositePlus, in that order
# outputs a tsv file containing the UID intersections of each database with all qphos 'samples'

def intersectionFunction(fHPRD, fRXM, fKEGG, fWP, fPSP):

        UID_spreadsheet = open("database_qPhos_Comparison_UID.tsv", "w+")
        UID_spreadsheet.write("Intersection\tHPRD\tReactome\tKEGG\tWikiPathways\tPhosphoSitePlus\n")

        HPRD = set(line.strip() for line in open(fHPRD))
        RXM = set(line.strip() for line in open(fRXM))
        KEGG= set(line.strip() for line in open(fKEGG))
        WP = set(line.strip() for line in open(fWP))
        PSP = set(line.strip() for line in open(fPSP))


        # get all UID files and MOD files for each qphos 'sample'
        for file in glob.glob('UID*'):
            if not(file.startswith("UID_MOD")):
                with open(file) as f:
                    fileName = set(line.strip() for line in open(file))
                    iHPRD = len(HPRD.intersection(fileName))
                    iRXM = len(RXM.intersection(fileName))
                    iKEGG = len(KEGG.intersection(fileName))
                    iWP = len(WP.intersection(fileName))
                    iPSP = len(PSP.intersection(fileName))
                    UID_spreadsheet.write('%s\t%d\t%d\t%d\t%d\t%d\n'%(file, iHPRD, iRXM, iKEGG, iWP, iPSP))


        UID_spreadsheet.close()

def main():
    intersectionFunction(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

if __name__ == "__main__":
    main()
