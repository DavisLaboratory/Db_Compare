import os
import glob
import sys

# input the file containing the UIDs for the databases HPRD, BioGRID, Reactome, KEGG, WikiPathways PhosphositePlus, and SIGNOR, in that order
# outputs a tsv file containing the UID intersections of each database with all qphos 'samples'

def intersectionFunction(fHPRD, fBG, fRXM, fKEGG, fWP, fPSP, fSIG):

        UID_spreadsheet = open("database_qPhos_Comparison_UID.tsv", "w+")
        UID_spreadsheet.write("Intersection\tHPRD\tBioGRID\tReactome\tKEGG\tWikiPathways\tPhosphoSitePlus\tSIGNOR\n")

        HPRD = set(line.strip() for line in open(fHPRD))
        RXM = set(line.strip() for line in open(fRXM))
        KEGG= set(line.strip() for line in open(fKEGG))
        WP = set(line.strip() for line in open(fWP))
        PSP = set(line.strip() for line in open(fPSP))
        BG = set(line.strip() for line in open(fBG))
        SIG = set(line.strip() for line in open(fSIG))

        # get all UID files and MOD files for each qphos 'sample'
        for file in glob.glob('UID*_NoIso.txt'):
            if not(file.startswith("UID_MOD")):
                with open(file) as f:
                    fileName = set(line.strip() for line in open(file))
                    iHPRD = len(HPRD.intersection(fileName))
                    iRXM = len(RXM.intersection(fileName))
                    iKEGG = len(KEGG.intersection(fileName))
                    iWP = len(WP.intersection(fileName))
                    iPSP = len(PSP.intersection(fileName))
                    iBG = len(BG.intersection(fileName))
                    iSIG = len(SIG.intersection(fileName))
                    UID_spreadsheet.write('%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n'%(file, iHPRD, iBG, iRXM, iKEGG, iWP, iPSP, iSIG))


        UID_spreadsheet.close()

def main():
    intersectionFunction(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])

if __name__ == "__main__":
    main()
