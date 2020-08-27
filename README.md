# Db_Compare

*NOTE: only works on Mac or Linux OS*

`Db_Compare` Compares the databases Reactome, KEGG, HPRD, WikiPathways and PhosphoSitePlus on their coverage of phospho/proteomic data.
 
## Requirements

The following `conda` command will create an environment called `DbCompareConda` with all dependencies installed

```
conda create --name DbCompareConda \
  --channel conda-forge \
  --channel bioconda \
  python=3 \
  pandas \
  requests \
  urllib3 \
  tqdm \
  r=3.6 \
  r-upsetr \
  r-sna \
  r-plotrix \
  r-ggplot2 \
  bioconductor-clusterprofiler \
  bioconductor-org.hs.eg.db \
  pandoc \
  openjdk=8
```

## Usage

To run `Db_Compare` follow these steps:

1. Clone this repo (as below) or create a new directory and place the provided scripts, files and folders inside.

```
git clone https://github.com/HannahHuckstep/Db_Compare.git
```

2. [OPTIONAL] download the most current version of databases into `Db_Compare/`. By default `Db_Compare` 
will use the database file in `refDatabaseFiles.zip` and `sigDatabaseFiles.zip`. 
See the bullet points further down the page for names and locations of databases.

3. Then run the bash script after navigating to the `Db_Compare/` directory. 

```{bash}
conda activate DbCompareConda
cd Db_Compare/
bash dbCompareScript.bash
```


4. Once the analysis has completed open `dbCompareNotebook.html` to view the resulting plots.
The consistency analysis results can be found in each's database directory (For Reactome, PhosphoSitePlus, HPRD, and qPhos)


---

### Databases for step 2

Download the following files and place in the directory created in step 1.
* Download the OWL file for Ractome, use Homo_sapiens (from Reactome, [BioPAX level 3](https://reactome.org/download/current/biopax.zip)) and name it RXM.owl
* Download the OWL file for PhosphoSitePlus (from PhosphoSitePlus, [BioPAX:Kinase-substrate information](https://www.phosphosite.org/staticDownloads)) and name it PSP.owl
* Download the file for the full version of PhosphoSitePlus (from PhosphoSitePlus, [Phosphorylation_site_dataset](https://www.phosphosite.org/staticDownloads)) and name it PSP_full.tsv
* Download the OWL file for HPRD (from Pathway Commons [PathwayCommons11.hprd.BIOPAX.owl.gz ](https://www.pathwaycommons.org/archives/PC2/v11/PathwayCommons11.hprd.BIOPAX.owl.gz)) and name it HPRD.owl
* Download the gmt file for WikiPathways (from WikiPathways, Homo_sapiens [Gene lists per pathway(GMT)](http://data.wikipathways.org/current/gmt/wikipathways-20200810-gmt-Homo_sapiens.gmt)) and name it WP.tsv
* Download the ppi from IMEX (from IMEX [intact-micluster.txt from psi-mitab](https://www.ebi.ac.uk/intact/downloads)) and name it IMEX.tsv
* Request the dataset from [qPhos](http://qphos.cancerbio.info/download.php) and name the file QPHOS_DATA.tsv
* Copy the qPhos supplementary data file from the 'about' page in the qPhos website and name the file QPHOS_SUPP_DATA.tsv
