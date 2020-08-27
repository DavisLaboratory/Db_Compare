import sys
import re

def extract_UIDs(cell_line):

    fileName = "UID_MOD_" + cell_line

    with open(cell_line) as f:
        lines = f.readlines()

    all_uids = open(fileName,"w+")

    for i in lines:
        line = i.split('\t')
        all_uids.write(line[0]+"_p-"+line[-1][7]+line[2]+"\n")

    all_uids.close()


def main():
    # df to add to
    extract_UIDs(sys.argv[1])

if __name__ == "__main__":
    main()
