# Db_Compare

In order to perform the analysis these libraries must be installed:

**Java 8**

**python3**: copy, gzip, io, logging, pickle, pathlib, collections, itertools, typing, pandas, requests, tqdm, bs4, requests.adapters, urllib3, sys, re, request, urllibs

**R**: UpSetR, sna, plotrix, ggplot2, clusterProfiler, org.Hs.eg.db, pandoc

Then follow these steps:

1. Create a new directory and place the provided scripts, files and folders inside
or clone this repo.

2. If you would like to use the most current version of the databases:
* Download the following files and place in the directory created in step 1.
* Download the OWL file for Ractome (from Reactome, BioPAX level 3) and name it RXM.owl
* Download the OWL file for PhosphoSitePlus (from PhosphoSitePlus, BioPAX:Kinase-substrate information) and name it PSP.owl
* Download the file for the full version of PhosphoSitePlus (from PhosphoSitePlus, Phosphorylation_site_dataset) and name it PSP_full.tsv
* Download the OWL file for HPRD (from Pathway Commons) and name it HPRD.owl
* Download the gmt file for WikiPathways (from WikiPathways, Gene lists per pathway(GMT)) and name it WP.tsv
* Download the UniProt ID Gene Ontology list for Cell Signalling Category (GO:0023052) and name it GO_SIG.txt
* Download the UniProt ID Gene Ontology list for Kinase Activity Category (GO:0016301) and name it GO_KA.txt
* Download the ppi from IMEX (from IMEX) and name it IMEX.tsv
* Request the dataset from qPhos and name the file QPHOS_DATA.tsv
* Copy the qPhos supplementary data file from the 'about' page in the qPhos website and name the file QPHOS_SUPP_DATA.tsv

Otherwise the script will use the versions provided in the zip files.

3. Run the bash script dbCompare.bash on the command line

(Open your terminal, navigate to the correct directory using the 'cd' command, run it by typing './dbCompare.bash')

4. Open the HTML file (dbCompareNotebook.html) created to view the resulting plots

The consistency analysis results can be found in each's database directory (For Reactome, PhosphoSitePlus, HPRD, and qPhos)
