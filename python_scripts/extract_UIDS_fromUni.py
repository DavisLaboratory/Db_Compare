import sys
import re

def extract_UIDs(go):

    with open(go) as f:
        lines = f.readlines()

    all_uids = open("AllUIDs_GO.txt","w+")

    UIDset = set()

    for i in lines:
        line = i.split('\t')
        uid = line[0].replace('UniProtKB:','')
        UIDset.add(uid)


    for i in UIDset:
        all_uids.write(i+"\n")

    all_uids.close()


def main():
    # df to add to
    extract_UIDs(sys.argv[1])

if __name__ == "__main__":
    main()
