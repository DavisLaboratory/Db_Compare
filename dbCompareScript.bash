#!/bin/bash

if [ ! -f ./RXM.owl ] || [ ! -f ./PSP.owl ] || [ ! -f ./HPRD.owl ] || [ ! -f ./WP.tsv ] ; then
    unzip sigDatabaseFiles.zip
fi

if [ ! -f ./IMEX.tsv] || [ ! -f ./QPHOS_DATA.tsv ] || [ ! -f ./QPHOS_SUPP_DATA.tsv ] ; then
    unzip refDatabaseFiles.zip
fi

mkdir ./RXM
mkdir ./PSP
mkdir ./HPRD
mkdir ./KEGG
mkdir ./WP
mkdir ./GO
mkdir ./IMEX
mkdir ./QPHOS
mkdir ./UNIPROT
mkdir ./PSP_full

mv ./RXM.owl ./RXM
mv ./PSP.owl ./PSP
mv ./HPRD.owl ./HPRD
mv ./WP.tsv ./WP
mv ./GO_* ./GO
mv ./IMEX.tsv ./IMEX
mv ./QPHOS_* ./QPHOS
mv ./PSP_full.tsv ./PSP_full


# for Reactome, PhosphositePlus and HPRD create the database, print the UIDs and Mods,remove isoforms, then do consistency analysis 
#: <<'END'

for f in ./RXM/RXM.owl ./PSP/PSP.owl ./HPRD/HPRD.owl 
do
	echo
	echo  $(basename -- "${f%.*}")
	java -jar ./dbcompare_jar/dbcompare.jar --mode CreateDB -iof $f -op ./$(basename -- "${f%.*}")/GRAPH  -sa ./SEC_ACC.tsv -uid ./UIDs.tsv 
	java -jar ./dbcompare_jar/dbcompare.jar --mode WriteAllUIDs -idb ./$(basename -- "${f%.*}")/GRAPH -op ./$(basename -- "${f%.*}")/
	java -jar ./dbcompare_jar/dbcompare.jar --mode WritePhos -idb ./$(basename -- "${f%.*}")/GRAPH -op ./$(basename -- "${f%.*}")/
	sort -u ./$(basename -- "${f%.*}")/UniProtIDs.tsv | sed '/-[0-9]\{1,2\}/d' > ./$(basename -- "${f%.*}")/UniProtIDs_noISO.tsv 
	sort -u ./$(basename -- "${f%.*}")/Phosphorylations.tsv | sed '/-[0-9]\{1,2\}/d' > ./$(basename -- "${f%.*}")/Phosphorylations_NoISO.tsv 
	java -jar ./dbcompare_jar/dbcompare.jar --mode CompareModListToUniProt -itf ./$(basename -- "${f%.*}")/Phosphorylations_NoISO.tsv -op ./$(basename -- "${f%.*}")/
done
#END

# for KEGG extract UIDs and then update them, then remove isoforms
echo
echo 'KEGG'
cd ./KEGG
python3 ../python_scripts/kegg2uniprot.py
sort -u AllUIDs.txt |  sed '/-[0-9]\{1,2\}/d' > AllUIDs_unique.txt 
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
cd ../

# for WP exrtract entrez ids and update them, then remove isoforms
echo
echo 'WP'
cd ./WP
python3 ../python_scripts/eid2uid.py WP.tsv 
sort -u AllUIDs.txt  |  sed '/-[0-9]\{1,2\}/d' > AllUIDs_unique.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
cd ../

# for GO extract UIDs and update them, then remove isoforms
echo
echo 'GO'
cd ./GO
python3 ../python_scripts/extract_UIDS_fromUni.py GO_KA.txt
mv AllUIDs_GO.txt AllUIDs_GO_KA.txt 
sort -u AllUIDs_GO_KA.txt  |  sed '/-[0-9]\{1,2\}/d' > AllUIDs_GO_KA_unique.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_GO_KA_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv updatedAllUID_KA.tsv

python3 ../python_scripts/extract_UIDS_fromUni.py GO_SIG.txt
mv AllUIDs_GO.txt AllUIDs_GO_SIG.txt 
sort -u AllUIDs_GO_SIG.txt  |  sed '/-[0-9]\{1,2\}/d'  > AllUIDs_GO_SIG_unique.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_GO_SIG_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv updatedAllUID_SIG.tsv
cd ../

# for IMEX extract UIDs and update them, then remove isoforms
echo
echo 'IMEX'
cd ./IMEX
python3 ../python_scripts/extract_UIDs_IMEX.py IMEX.tsv
sort -u AllUIDs.txt  |  sed '/-[0-9]\{1,2\}/d' > AllUIDs_unique.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
cd ../

# for qPhos aggregate samples and data, then remove isoforms
echo
echo 'QPHOS'
cd ./QPHOS

python3 ../python_scripts/extract_UIDs_qphos.py QPHOS_DATA.tsv
sort -u UID_QPHOS_DATA.tsv | sed '/-[0-9]\{1,2\}/d' > qphos_UIDS.tsv
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf qphos_UIDS.tsv -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv updatedAllUID_qphos.tsv


python3 ../python_scripts/getModFormat.py QPHOS_DATA.tsv
sort -u UID_MOD_QPHOS_DATA.tsv | sed '/-[0-9]\{1,2\}/d' > qphos_UID_MODS.tsv
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf qphos_UID_MODS.tsv -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv updatedAllUID_qphos_mods.tsv

java -jar ../dbcompare_jar/dbcompare.jar --mode CompareModListToUniProt -itf updatedAllUID_qphos_mods.tsv -op ./


SAMPLES=`awk -F "\"*\t\"*" '{print $2}' QPHOS_SUPP_DATA.tsv| sort -u | sed '/;/d' `


for i in $SAMPLES
do
	#echo $i
	python3 ../python_scripts/PMID_aggregation.py QPHOS_DATA.tsv QPHOS_SUPP_DATA.tsv $i
	sort -u UID_$i\.txt | sed '/-[0-9]\{1,2\}/d' > UID_$i\_NoIso.txt
	sort -u UID_MOD_$i\.txt | sed '/-[0-9]\{1,2\}/d' > UID_MOD_$i\_NoIso.txt
done

cd ../


#for PSP_full rmove non-human, get mods and run consistency anaylsis
echo
echo 'PSP full'
cd ./PSP_full

sed -e '/human/!d' PSP_full.tsv > PSP_full_human.tsv
python3 ../python_scripts/getModFormat_PSP_full.py PSP_full_human.tsv
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf UID_MOD_PSP_full_human.tsv -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv updatedAllUID_PSP_full_mods.tsv
java -jar ../dbcompare_jar/dbcompare.jar --mode CompareModListToUniProt -itf updatedAllUID_PSP_full_mods.tsv -op ./

cd ../


# for UniProt just download relavant files
echo
echo "UniProt"
cd ./UNIPROT
python3 ../python_scripts/getUniprotMods.py 
cd ../

# overlap plots
Rscript -e "rmarkdown::render('dbCompareNotebook.Rmd')"

