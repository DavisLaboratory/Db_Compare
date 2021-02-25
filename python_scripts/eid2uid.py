import sys
import re
import urllib.parse
import urllib.request

def extract_UIDs(wp):
    # takes a gmt file of a list of entrez ids per pathway
    with open(wp) as f:
        lines = f.readlines()

    all_uids = open("AllUIDs.txt","w+")

    eidSet = set()

    q = ''
    url = "https://www.uniprot.org/uploadlists/"
    rev_dict = {}

    # for each path in WP
    for i in lines:
        line = i.split('\t')
        # get all entrez ids 
        for j in range(2,len(line)):
            eidSet.add(str(line[j]))

    # add all eids to a query string
    for i in eidSet:
        temp = str(i) + ","
        q += temp

    # convert to UIDs
    params = {
        'from': 'P_ENTREZGENEID',
        'to': 'ACC',
        'format': 'tab',
        'columns':'id,reviewed,length',
        'query': q
        }

    data = urllib.parse.urlencode(params)
    data = data.encode('utf-8')
    req = urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as r:
        response = r.readlines()

        # for each line in the conversion file 
        for respLine in response:
            respStr = respLine.decode('utf-8')
            respStr = respStr.strip('\n')
            current = respStr.split('\t')
            #create an initial dict on how many review/unreviewed entries it has and the length
            rev_dict[current[3]] = {'rev':0, 'unrev':0, 'maxLenRev' : 0, 'maxLenUn':0}

        # go back through and populate initial entry 
        for respLine in response:
            respStr = respLine.decode('utf-8')
            respStr = respStr.strip('\n')
            current = respStr.split('\t')
            uid = current[0]
            rev = current[1]
            length = current[2]
            eid = current[3]
            if rev == "reviewed":
                rev_dict[eid]['rev'] += 1
                if int(length) > int(rev_dict[eid]['maxLenRev']):
                    rev_dict[eid]['maxLenRev'] = length
            elif rev  == 'unreviewed':
                rev_dict[eid]['unrev'] += 1
                if int(length) > int(rev_dict[eid]['maxLenUn']):
                    rev_dict[eid]['maxLenUn'] = length

        #go back through one last time and compare to all other entries for that eid
        used = []
        for respLine in response:
            respStr = respLine.decode('utf-8')
            respStr = respStr.strip('\n')
            current = respStr.split('\t')
            uid = current[0]
            rev = current[1]
            length = current[2]
            eid = current[3]
            # if it has more than one review uid and is the longest take it
            if rev_dict[eid]['rev'] > 1 and rev == "reviewed":
                if rev_dict[eid]['maxLenRev'] == length:
                    all_uids.write(uid+"\n")
                    rev_dict[eid]['maxLenRev'] = 0
                    rev_dict[eid]['maxLenUn'] = 0
                else:
                    continue
            # if it has no reviewed and multi unreviews take the longest
            elif rev_dict[eid]['rev'] == 0 and rev_dict[eid]['unrev'] > 1  and rev_dict[eid]['maxLenUn'] == length:
                all_uids.write(uid+"\n")
                rev_dict[eid]['maxLenUn'] = 0
                rev_dict[eid]['maxLenRev'] = 0
            # if it has no reviewed and only 1 unreviewed
            elif rev_dict[eid]['rev'] == 0 and rev_dict[eid]['unrev'] == 1:
                all_uids.write(uid+"\n")
            # else take the reviewed
            elif rev == "reviewed" and rev_dict[eid]['rev'] == 1:
                all_uids.write(uid + "\n")


    all_uids.close()


def main():
# df to add to
    extract_UIDs(sys.argv[1])

if __name__ == "__main__":
    main()

