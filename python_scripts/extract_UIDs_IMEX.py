import sys 
import re

def extract_UIDs(imex):

    with open(imex) as f:
        lines = f.readlines()

    all_uids = open("AllUIDs.txt","w+")

    for i in lines:
        line = i.split('\t')
        aliasA = line[2]
        aliasB = line[3]
        uidA = re.search("[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}",aliasA)
        if uidA:
            all_uids.write(str(uidA.group(0)))
            all_uids.write("\n")
            
        uidB = re.search("[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}",aliasB)
        if uidB:
            all_uids.write(str(uidB.group(0)))
            all_uids.write("\n")

    all_uids.close()


def main():
    # df to add to
    extract_UIDs(sys.argv[1])

if __name__ == "__main__":
    main()
