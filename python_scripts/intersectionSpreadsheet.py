import glob
import sys

# input the file containing the mods for the databases Uniprot, HPRD, Reactome and PhosphositePlus, in that order
# outputs a tsv file containing the phosphosite intersections of each database with all qphos 'samples'


def intersectionFunction(fUKB,fHPRD, fRXM, fPSP):

        MOD_spreadsheet = open("database_qPhos_Comparison_MOD.tsv", "w+")
        MOD_spreadsheet.write("Intersection\tUniProt\tHPRD\tReactome\tPhosphoSitePlus\n")

        HPRD = set(line.strip() for line in open(fHPRD))
        RXM = set(line.strip() for line in open(fRXM))
        PSP = set(line.strip() for line in open(fPSP))
        UKB = set(line.strip() for line in open(fUKB))


        # get all UID files and MOD files for each qphos 'sample'
        for file in glob.glob('UID*'):
            if file.startswith("UID_MOD"):
                with open(file) as f:
                    fileName = set(line.strip() for line in open(file))
                    iUKB = len(UKB.intersection(fileName))
                    iHPRD = len(HPRD.intersection(fileName))
                    iRXM = len(RXM.intersection(fileName))
                    iPSP = len(PSP.intersection(fileName))
                    MOD_spreadsheet.write('%s\t%d\t%d\t%d\t%d\n'%(file, iUKB, iHPRD, iRXM, iPSP))

        MOD_spreadsheet.close()

def main():
    intersectionFunction(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

if __name__ == "__main__":
    main()
