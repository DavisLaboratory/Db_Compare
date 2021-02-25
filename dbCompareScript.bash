#!/bin/bash

if [ ! -f ./RXM.owl ] || [ ! -f ./PSP.owl ] || [ ! -f ./HPRD_PPI.tsv ] || [ ! -f ./HPRD_mods.tsv ] || [ ! -f ./WP.tsv ]  || [ ! -f ./SIGNOR_UIDs.tsv ]  || [ ! -f ./SIGNOR_mods.tsv ]  || [ ! -f ./PSP_full.tsv ]; then
    unzip sigDatabaseFiles.zip
fi


if  [ ! -f ./BG_UIDs.tsv ]  || [ ! -f ./BG_mods.tsv ]; then
    unzip BG.zip
fi

if [ ! -f ./IMEX.tsv ] || [ ! -f ./QPHOS_DATA.tsv ] || [ ! -f ./QPHOS_SUPP_DATA.tsv ] || [ ! -f ./GO_SIG.tsv ] || [ ! -f ./GP_PKA.tsv ] || [ ! -f ./UP_PP.tsv ]; then
    unzip refDatabaseFiles.zip
fi

mkdir ./RXM
mkdir ./PSP
mkdir ./HPRD
mkdir ./BG
mkdir ./SIGNOR
mkdir ./KEGG
mkdir ./WP
mkdir ./GO
mkdir ./IMEX
mkdir ./QPHOS
mkdir ./UNIPROT
mkdir ./PSP_full

mv ./RXM.owl ./RXM
mv ./PSP.owl ./PSP
mv ./HPRD_MAP.tsv ./HPRD
mv ./HPRD_PPI.tsv ./HPRD
mv ./HPRD_mods.tsv ./HPRD
mv ./BG_UIDs.tsv ./BG
mv ./BG_mods.tsv ./BG
mv ./SIGNOR_UIDs.tsv ./SIGNOR
mv ./SIGNOR_mods.tsv ./SIGNOR
mv ./WP.tsv ./WP
mv ./GO_* ./GO
mv ./IMEX.tsv ./IMEX
mv ./QPHOS_* ./QPHOS
mv ./PSP_full.tsv ./PSP_full
mv ./UP_PP.tsv ./UNIPROT


# for Reactome, PhosphositePlus and HPRD create the database, print the UIDs and Mods,remove isoforms, then do consistency analysis 
#: <<'END'

for f in ./RXM/RXM.owl ./PSP/PSP.owl
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

# for HPRD extract UIDs from PPI and then update them, then remove isoforms, also extract mods from mod file, update mod UIDs, then run consistency analysis
echo
echo 'HPRD'
cd ./HPRD
sort -u HPRD_mods.tsv | sed '/Phosphorylation/!d' > HPRD_phos_temp.tsv 
sort -u HPRD_phos_temp.tsv | sed 's/;-//' > HPRD_phos.tsv 
rm HPRD_phos_temp.tsv

python3 ../python_scripts/hprd2uid.py HPRD_PPI.tsv HPRD_phos.tsv
sort -u AllUIDs.txt |  sed 's/-1$//g' > AllUIDs_q.txt 
sort -u AllUIDs_q.txt |  sed '/-[0-9]\{1,4\}/d' > AllUIDs_unique.txt 
rm AllUIDs_q.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv UniProtIDs_noISO.tsv

sort -u AllMODs.txt |  sed 's/-1//g' > AllMODs_q.txt 
sort -u AllMODs_q.txt |  sed '/-[0-9]\{1,4\}/d' > AllmodUIDs_unique.txt 
rm AllMODs_q.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllmodUIDs_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv Phosphorylations_noISO.tsv
java -jar ../dbcompare_jar/dbcompare.jar --mode CompareModListToUniProt -itf Phosphorylations_noISO.tsv -op ./
cd ../

# for BioGRID extract UIDs from PPI and update them, then remove isofomrms, also extract mods from mod file, update them and run consistency analysis
echo
echo 'BioGRID'
cd ./BG
sort -u BG_mods.tsv | sed '/Phos.*Homo/!d' > BG_mods_humanOnly.tsv
sort -u BG_UIDs.tsv | sed '/Homo.*Homo/!d' > BG_UIDs_humanOnly.tsv

python3 ../python_scripts/extractUIDsandMODs_BioGRID.py BG_UIDs_humanOnly.tsv BG_mods_humanOnly.tsv
sort -u AllUIDs.txt |  sed 's/-1$//g' > AllUIDs_q.txt 
sort -u AllUIDs_q.txt |  sed '/-[0-9]\{1,4\}/d' > AllUIDs_unique.txt 
rm AllUIDs_q.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv UniProtIDs_noISO.tsv

sort -u AllMODs.txt |  sed 's/-1//g' > AllMODs_q.txt 
sort -u AllMODs_q.txt |  sed '/-[0-9]\{1,4\}/d' > AllmodUIDs_unique.txt 
rm AllMODs_q.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllmodUIDs_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv Phosphorylations_noISO.tsv
java -jar ../dbcompare_jar/dbcompare.jar --mode CompareModListToUniProt -itf Phosphorylations_noISO.tsv -op ./
cd ../

# for SIGNOR, extract UIDs and then update them, then remove isoforms 
echo
echo 'SIGNOR'
cd ./SIGNOR

sort -u SIGNOR_UIDs.tsv |  sed '/-[0-9]\{1,4\}/d' > AllUIDs_unique.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv UniProtIDs_noISO.tsv

sort -u SIGNOR_mods.tsv | awk -F "\t" '/1/ {print $7 "\t" $11}' > sig_phos.tsv
sed -i '' -e  's/Thr/T/' sig_phos.tsv
sed -i '' -e  's/Ser/S/' sig_phos.tsv
sed -i '' -e  's/Tyr/Y/' sig_phos.tsv
sed -i '' -e  's/	/_p-/' sig_phos.tsv
sed -i '' -e  '/-[S|T|Y][0-9]\{1,2\}/!d' sig_phos.tsv
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf sig_phos.tsv -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv Phosphorylations_noISO.tsv
java -jar ../dbcompare_jar/dbcompare.jar --mode CompareModListToUniProt -itf Phosphorylations_noISO.tsv -op ./
cd ../

# for KEGG extract UIDs and then update them, then remove isoforms
echo
echo 'KEGG'
cd ./KEGG
python3 ../python_scripts/kegg2uniprot.py
sort -u AllUIDs.txt |  sed '/-[0-9]\{1,4\}/d' > AllUIDs_unique.txt 
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
cd ../

# for WP exrtract entrez ids and update them, then remove isoforms
echo
echo 'WP'
cd ./WP
python3 ../python_scripts/eid2uid.py WP.tsv 
sort -u AllUIDs.txt  |  sed '/-[0-9]\{1,4\}/d' > AllUIDs_unique.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
cd ../

# for GO extract UIDs and update them, then remove isoforms
echo
echo 'GO'
cd ./GO
python3 ../python_scripts/extract_UIDS_fromUni.py GO_PKA.tsv
mv AllUIDs_GO.txt AllUIDs_GO_PKA.tsv 
sort -u AllUIDs_GO_PKA.tsv  |  sed '/-[0-9]\{1,4\}/d' > AllUIDs_GO_PKA_unique.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_GO_PKA_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv updatedAllUID_PKA.tsv

python3 ../python_scripts/extract_UIDS_fromUni.py GO_SIG.tsv
mv AllUIDs_GO.txt AllUIDs_GO_SIG.tsv 
sort -u AllUIDs_GO_SIG.tsv  |  sed '/-[0-9]\{1,4\}/d'  > AllUIDs_GO_SIG_unique.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_GO_SIG_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv updatedAllUID_SIG.tsv
cd ../

# for IMEX extract UIDs and update them, then remove isoforms
echo
echo 'IMEX'
cd ./IMEX
python3 ../python_scripts/extract_UIDs_IMEX.py IMEX.tsv
sort -u AllUIDs.txt  |  sed '/-[0-9]\{1,4\}/d' > AllUIDs_unique.txt
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf AllUIDs_unique.txt -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
cd ../


# for qPhos aggregate samples and data, then remove isoforms
echo
echo 'QPHOS'
cd ./QPHOS

python3 ../python_scripts/extract_UIDs_qphos.py QPHOS_DATA.tsv
sort -u UID_QPHOS_DATA.tsv | sed '/-[0-9]\{1,4\}/d' > qphos_UIDS.tsv
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf qphos_UIDS.tsv -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv updatedAllUID_qphos.tsv


python3 ../python_scripts/getModFormat.py QPHOS_DATA.tsv
sort -u UID_MOD_QPHOS_DATA.tsv | sed '/-[0-9]\{1,4\}/d' > qphos_UID_MODS.tsv
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf qphos_UID_MODS.tsv -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv updatedAllUID_qphos_mods.tsv

java -jar ../dbcompare_jar/dbcompare.jar --mode CompareModListToUniProt -itf updatedAllUID_qphos_mods.tsv -op ./

sed -i '' -e  's/breast cancer/breast_cancer/' QPHOS_SUPP_DATA.tsv

SAMPLES=`awk -F "\"*\t\"*" '{print $2}' QPHOS_SUPP_DATA.tsv| sort -u | sed '/;/d' `


for i in $SAMPLES
do
	#echo $i
	python3 ../python_scripts/PMID_aggregation.py QPHOS_DATA.tsv QPHOS_SUPP_DATA.tsv $i
	sort -u UID_$i\.txt | sed '/-[0-9]\{1,4\}/d' > UID_$i\_NoIso.txt
	sort -u UID_MOD_$i\.txt | sed '/-[0-9]\{1,4\}/d' > UID_MOD_$i\_NoIso.txt
done

python3 ../python_scripts/intersectionSpreadsheet.py ../HPRD/Phosphorylations_noISO.tsv ../BG/Phosphorylations_noISO.tsv ../RXM/Phosphorylations_NoISO.tsv ../PSP/Phosphorylations_NoISO.tsv ../SIGNOR/Phosphorylations_NoISO.tsv 
python3 ../python_scripts/intersectionSpreadsheet_UIDs.py ../HPRD/UniProtIDs_noISO.tsv ../BG/UniProtIDs_noISO.tsv ../RXM/UniProtIDs_noISO.tsv ../KEGG/updatedAllUID.tsv ../WP/updatedAllUID.tsv ../PSP/UniProtIDs_noISO.tsv ../SIGNOR/UniProtIDs_noISO.tsv

cd ../


#for PSP_full rmove non-human, get mods and run consistency anaylsis
echo
echo 'PSP full'
cd ./PSP_full

sed -e '/human/!d' PSP_full.tsv > PSP_full_human.tsv
python3 ../python_scripts/getModFormat_PSP_full.py PSP_full_human.tsv
java -jar ../dbcompare_jar/dbcompare.jar --mode UpdateUniProtIDs -itf UID_MOD_PSP_full_human.tsv -op ./ -sa ../SEC_ACC.tsv -uid ../UIDs.tsv
mv updatedAllUID.tsv updatedAllUID_PSP_full_mods.tsv
sort -u updatedAllUID_PSP_full_mods.tsv | sed '/-[0-9]\{1,4\}/d' > updatedAllUID_PSP_full_mods_NoIso.tsv 
java -jar ../dbcompare_jar/dbcompare.jar --mode CompareModListToUniProt -itf updatedAllUID_PSP_full_mods_NoIso.tsv -op ./

cd ../


# for UniProt just download relavant files
echo
echo "UniProt"
cd ./UNIPROT
python3 ../python_scripts/getUniprotMods.py 
cd ../

# overlap plots
Rscript -e "rmarkdown::render('dbCompareNotebook.Rmd')"
