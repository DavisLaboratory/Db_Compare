import sys
import re

def PMID_agg(qPhos, supp_data, sample):
    # ultimate file given thw qPhos file, supplamental data and a sample name it will extract UIDS and mods 

    with open(qPhos) as f:
        lines = f.readlines()

    with open(supp_data) as f2:
        lines2 = f2.readlines()
    
    # create files to write to 
    sampleFile= sample + ".txt"
    UIDFile = "UID_" + sample + ".txt"
    ModFile = "UID_MOD_" + sample + ".txt"
    MCF7 = open(sampleFile,"w+")
    UIDs = open(UIDFile,"w+")
    Mods = open(ModFile, "w+") 

    #UID SET
    UIDset = set()

    #Mod SET
    MODset = set()

    # get the col that holds PMIDs in qphos
    for i in lines:
        line = i.split('\t')
        for j in range(0,len(line)):
            if line[j] == "PMID":
                pmid_col_qphos = j

    # get the PMIDS from the supp data and add to dict 
    pmid_dict = {}
    for i in lines2:
        line2 = i.split('\t')
        pmid_dict[line2[0].strip()] = {'sample':line2[1],'quant_mthd':line2[2]}

    for i in lines:
        line = i.split('\t')
        pmids = line[pmid_col_qphos].split(';')
        for j in pmids:
            if pmid_dict[j]['sample'] == sample:
                MCF7.write(line[0]+ "\t"+ line[1] + "\t" + line[2] + "\t" + line[3] +"\t" + line[5])
                UIDset.add(line[0])
                MODset.add(line[0] + "_p-" + line[5][7]+line[2])

    MCF7.close()

    for i in UIDset:
        UIDs.write(i + "\n")

    UIDs.close()

    for i in MODset:
        Mods.write(i + "\n")

    Mods.close()



def main():
    PMID_agg(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    main()

