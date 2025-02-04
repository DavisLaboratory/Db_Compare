import glob
import sys

# input the file containing the mods for the databases HPRD, BioGRID, PhosphositePlus and Reactome, in that order
# outputs a tsv file containing the phosphosite intersections of each database with all qphos 'samples'


def intersectionFunction(fHPRD, fBG, fPSP, fRXM, fSIG):

        MOD_spreadsheet = open("database_qPhos_Comparison_MOD.tsv", "w+")
        MOD_spreadsheet.write("Intersection\tHPRD\tBioGRID\tPhosphoSitePlus\tReactome\tSIGNOR\n")

        HPRD = set(line.strip() for line in open(fHPRD))
        RXM = set(line.strip() for line in open(fRXM))
        PSP = set(line.strip() for line in open(fPSP))
        BG = set(line.strip() for line in open(fBG))
        SIG = set(line.strip() for line in open(fSIG))

        # get all UID files and MOD files for each qphos 'sample'
        for file in glob.glob('UID*_NoIso.txt'):
            if file.startswith("UID_MOD"):
                with open(file) as f:
                    fileName = set(line.strip() for line in open(file))
                    iBG = len(BG.intersection(fileName))
                    iHPRD = len(HPRD.intersection(fileName))
                    iRXM = len(RXM.intersection(fileName))
                    iPSP = len(PSP.intersection(fileName))
                    iSIG = len(SIG.intersection(fileName))
                    MOD_spreadsheet.write('%s\t%d\t%d\t%d\t%d\t%d\n'%(file, iHPRD, iBG, iPSP, iRXM, iSIG))

        MOD_spreadsheet.close()

def main():
    intersectionFunction(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

if __name__ == "__main__":
    main()
