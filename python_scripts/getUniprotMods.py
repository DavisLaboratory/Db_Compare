import sys
import re
import requests

def extract_UIDs():

    #unreviewed + reviewed 
    uurl = 'https://www.uniprot.org/uniprot/?query=organism:9606&format=tab&columns=id,entry%20name,reviewed,feature(MODIFIED%20RESIDUE)'
    myfile_trambl = requests.get(uurl)

    #reviewed
    url = 'https://www.uniprot.org/uniprot/?query=reviewed:yes+AND+organism:9606&format=tab&columns=id,entry%20name,reviewed,feature(MODIFIED%20RESIDUE)'
    myfile = requests.get(url)

    #trembl
    trmbl_uids = open("Trembl.tsv","w+")

    #actually mods 
    all_uids = open("SwissProtMods.tsv","w+")

    #uids 
    all = open("SwissProt.tsv","w+")

    lines = myfile.text.split('\n')
    
    #with open(mods) as f:
    #    lines = f.readlines()
    
    for i in range(0,len(lines)-1):
        line = lines[i].split('\t')
        all.write(line[0] + "\n")
        mods = line[3].split(";")
        for j in range(0,len(mods)):
            if "Phosphoserine" in mods[j]:
                num = re.findall(r"\d+",mods[j-1])
                all_uids.write(line[0] + "_p-S"+str(num[0])+"\n")
            elif "Phosphotyrosine" in mods[j]:
                num = re.findall(r"\d+",mods[j-1])
                all_uids.write(line[0] + "_p-Y"+str(num[0])+"\n")
            elif "Phosphothreonine" in mods[j]:
                num = re.findall(r"\d+",mods[j-1])
                all_uids.write(line[0] + "_p-T"+str(num[0])+"\n")

    lines = myfile_trambl.text.split('\n')
    for i in range(0,len(lines)-1):
        line = lines[i].split('\t')
        trmbl_uids.write(line[0] + "\n")


    trmbl_uids.close()
    all_uids.close()
    all.close()

def main():
    # df to add to
    extract_UIDs()

if __name__ == "__main__":
    main()
