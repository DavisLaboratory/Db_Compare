import sys
import re

def extract_UIDs(modFile):

    fileName = "UID_MOD_" + modFile

    with open(modFile) as f:
        lines = f.readlines()

    all_uids = open(fileName,"w+")

    for i in lines:
        line = i.split('\t')
        loc = int(re.search(r'\d+',line[4]).group())
        all_uids.write(line[2]+"_p-"+line[4][0]+str(loc)+"\n")

    all_uids.close()


def main():
    # df to add to
    extract_UIDs(sys.argv[1])

if __name__ == "__main__":
    main()
