import sys
import re
import urllib.parse
import urllib.request

def extract_UIDs(bg, ptms):
    # takes a txt file with each line a unique hprdID and eid
    with open(bg) as f:
        lines = f.readlines()

    all_uids = open("AllUIDs.txt","w+")

    eidSet = set()
    uidSet = set()

    q = ''
    url = "https://www.uniprot.org/uploadlists/"
    rev_dict = {}
    eid2uid = {}

    # for each line in biogrid - get the eid from interactor A and interactor B
    for i in lines:
        line = i.split("\t")
        A = line[25]
        B = line[28]
        aIso = A.split("|")
        bIso = B.split("|")
        for a in aIso:
            eidSet.add(a)
        for b in bIso:
            eidSet.add(b)

    # add all eids to a query string
    for i in eidSet:
        temp = str(i) + ","
        q += temp

    # convert to UIDs
    params = {
        'from': 'P_REFSEQ_AC',
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
            e = current[3]
            eids = e.split(',')
            for eid in eids:
                rev_dict[eid] = {'rev':0, 'unrev':0, 'maxLenRev' : 0, 'maxLenUn':0}

        # go back through and populate initial entry 
        for respLine in response:
            respStr = respLine.decode('utf-8')
            respStr = respStr.strip('\n')
            current = respStr.split('\t')
            uid = current[0]
            rev = current[1]
            length = current[2]
            e = current[3]

            eids = e.split(',')
            for eid in eids:
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
            e = current[3]
            ref2uid = current[4]
            iso = re.split(' -> |,', ref2uid)
            eids = e.split(',')
            for eid in eids:
                
                if len(iso) >1:
                    for i in range(0,len(iso)):
                        if eid == iso[i]:
                            uid = iso[i+1]
 
                # if it has more than one review uid and is the longest take it
                if rev_dict[eid]['rev'] > 1 and rev == "reviewed":
                    if rev_dict[eid]['maxLenRev'] == length:
                        all_uids.write(uid+"\n")
                        uidSet.add(uid)
                        rev_dict[eid]['maxLenRev'] = 0
                        rev_dict[eid]['maxLenUn'] = 0
                        eid2uid[eid] = uid
                    else:
                        continue
                # if it has no reviewed and multi unreviews take the longest
                elif rev_dict[eid]['rev'] == 0 and rev_dict[eid]['unrev'] > 1  and rev_dict[eid]['maxLenUn'] == length:
                    all_uids.write(uid+"\n")
                    uidSet.add(uid)
                    rev_dict[eid]['maxLenUn'] = 0
                    rev_dict[eid]['maxLenRev'] = 0
                    eid2uid[eid] = uid

                # if it has no reviewed and only 1 unreviewed
                elif rev_dict[eid]['rev'] == 0 and rev_dict[eid]['unrev'] == 1:
                    all_uids.write(uid+"\n")
                    uidSet.add(uid)
                    eid2uid[eid] = uid

                # else take the reviewed
                elif rev == "reviewed" and rev_dict[eid]['rev'] == 1:
                    all_uids.write(uid + "\n")
                    uidSet.add(uid)
                    eid2uid[eid] = uid

                
                # if there are multi eids to one uid
                if ',' in eid:
                    temp_uid = eid2uid[eid]
                    eids = eid.split(',')
                    for e in eids:
                        eid2uid[e] = uid
    all_uids.close()

    #now extract ptms and exctract uid from eid
    with open(ptms) as f:
        lines = f.readlines()

    all_mods = open("AllMODs.txt","w+")
    
    for i in lines:
        line = i.split('\t') 
       # get all entrez id
        bgeid = line[7]
        if bgeid in eid2uid:
            uid = eid2uid[bgeid]
            if uid in uidSet:
                all_mods.write(uid + "_p-" + line[10] + line[8] + "\n")

def main():
# df to add to
    extract_UIDs(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
