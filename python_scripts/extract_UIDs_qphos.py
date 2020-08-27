import sys
import re

def PMID_agg(qPhos):

    fileName = "UID_" + qPhos

    with open(qPhos) as f:
        lines = f.readlines()

    MCF7 = open(fileName,"w+")


    # get the col that holds PMIDs in qphos
    for i in lines:
        line = i.split('\t')
        MCF7.write(line[0]+"\n")

    MCF7.close()


def main():
    PMID_agg(sys.argv[1])

if __name__ == "__main__":
    main()

