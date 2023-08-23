# ArXiv dataset downloading and preprocessing
😊 [中文說明](https://hackmd.io/@7111056013/SyxoXIX32)

## Task
1. Download arXiv data from Amazon S3 to EC2
2. Data preprocessing
3. Data filtering and related statistics

## AWS
Connect to EC2
```
ssh ubuntu@ec2-3-137-149-71.us-east-2.compute.amazonaws.com -i llm-vm.pem
```

## Download arXiv source data from Amazon S3
1. **Use RedPajama script** ✔
<br>Before downloading, you need to get slurm done first. The next section explains the installation method and download steps
<br>https://github.com/togethercomputer/RedPajama-Data/tree/main/data_prep/arxiv

2. **Refer to arXiv official website**
<br>Full Text via S3 - arXiv info
<br>https://info.arxiv.org/help/bulk_data_s3.html#src

3. **Using arxiv-tools**
<br>Downloading according to README does not require slurm, but the downloaded data will be less ( the reason is unknown )
<br>https://github.com/armancohan/arxiv-tools

## Install slurm + download arXiv steps

```
sudo apt update -y
sudo apt install slurm-wlm slurm-wlm-doc -y
```
* View the hardware configuration of the current node through the slurmd -C command

<img src="https://github.com/gigilin7/ArXiv-Dataset/assets/43805264/46345ca6-82d8-436a-83b4-48c321ded2a6" width="800" />

* Set slurm configure ( path in `/etc/slurm/` )
     * Through the form provided by the official, select the content you want to send and there will be slurm.conf
     <br>https://slurm.schedmd.com/configurator.html
     * The currently used config is as follows
```
# slurm.conf file generated by configurator easy.html.
# Put this file on all nodes of your cluster.
# See the slurm.conf man page for more information.
#
ControlMachine=ip-172-31-45-84
#ControlAddr=
#
#MailProg=/bin/mail
MpiDefault=none
#MpiParams=ports=#-#
ProctrackType=proctrack/pgid
ReturnToService=1
SlurmctldPidFile=/var/run/slurm-llnl/slurmctld.pid
#SlurmctldPort=6817
SlurmdPidFile=/var/run/slurm-llnl/slurmd.pid
#SlurmdPort=6818
SlurmdSpoolDir=/var/spool/slurmd
SlurmUser=root
#SlurmdUser=root
StateSaveLocation=/var/spool/slurm-llnl
SwitchType=switch/none
TaskPlugin=task/none
#
#
# TIMERS
#KillWait=30
#MinJobAge=300
SlurmctldTimeout=3600
SlurmdTimeout=300
BatchStartTimeout=3600
PropagateResourceLimits=NONE
#
#
# SCHEDULING
#FastSchedule=1
SchedulerType=sched/backfill
SelectType=select/linear
#SelectTypeParameters=
#
#
# LOGGING AND ACCOUNTING
#AccountingStorageType=accounting_storage/none
ClusterName=mycluster
#JobAcctGatherFrequency=30
#JobAcctGatherType=jobacct_gather/none
#SlurmctldDebug=3
#SlurmctldLogFile=
#SlurmdDebug=3
#SlurmdLogFile=
#
# Acct
AccountingStorageEnforce=1
#AccountingStorageLoc=/opt/slurm/acct
#AccountingStorageType=accounting_storage/filetxt

JobCompLoc=/opt/slurm/jobcomp
JobCompType=jobcomp/filetxt

JobAcctGatherFrequency=30
JobAcctGatherType=jobacct_gather/linux
#
# COMPUTE NODES
NodeName=ip-172-31-45-84 CPUs=8 State=UNKNOWN
PartitionName=debug Nodes=ip-172-31-45-84 Default=YES MaxTime=INFINITE State=UP
```

* Create the directory and permission settings corresponding to config

```
rm -rf  /var/spool/slurm-llnl
mkdir /var/spool/slurm-llnl
chown -R slurm.slurm /var/spool/slurm-llnl
rm -rf /var/run/slurm-llnl/
mkdir /var/run/slurm-llnl/
chown -R slurm.slurm /var/run/slurm-llnl/
sudo mkdir -p /opt/slurm 
sudo chmod -Rf 777 /opt/slurm 
cd /opt/slurm 
touch acct 
touch jobcomp
```

* Start and set up to start automatically

```
systemctl start slurmd
systemctl enable slurmd
systemctl start slurmctld
systemctl enable slurmctld
```

⚠ Make sure both slurmd and slurmctld are started

<img src="https://github.com/gigilin7/ArXiv-Dataset/assets/43805264/82b62a42-b42d-4de0-9417-9920e565c285" width="500" />

<img src="https://github.com/gigilin7/ArXiv-Dataset/assets/43805264/60be520b-209c-448a-9f98-d3d30c83e7d5" width="500" />

* View the current status of slurm

<img src="https://github.com/gigilin7/ArXiv-Dataset/assets/43805264/67d5fcee-4d12-43f6-b5e3-b23b8af3908b" width="500" />

* Close slurm ( close after downloading arXiv )

```
systemctl stop slurmd
systemctl disable slurmd
systemctl stop slurmctld
systemctl disable slurmctld
```

* After installing slurm, you can download arXiv with the following command
<br> Remember to clone `https://github.com/togethercomputer/RedPajama-Data.git`

```
bash scripts/arxiv-kickoff-download.sh
```

* If you encounter the following problems

<img src="https://github.com/gigilin7/ArXiv-Dataset/assets/43805264/5335caa0-c12f-4b34-85e1-34d9064b85f9" width="600" />

* First check the memory information `mem=1M`, and change the --mem-per-cpu of arxiv-download-slurm.sbatch to 1M

<img src="https://github.com/gigilin7/ArXiv-Dataset/assets/43805264/9906badf-fbce-40fb-ad03-3d99deb25ec6" width="500" />

* Check the download progress through the squeue command

<img src="https://github.com/gigilin7/ArXiv-Dataset/assets/43805264/bc30ce40-ff8c-4ec8-a1f5-d506b277a010" width="500" />

* Download completed
<br>After downloading, it will be a bunch of tar, and after decompression, it will be a bunch of gz ( some pdf will be mixed in, and the pdf will be filtered out later without data cleaning )

<img src="https://github.com/gigilin7/ArXiv-Dataset/assets/43805264/35cfd29e-8c32-41cb-8be4-dadfa3f6f67c" width="250" /> <img src="https://github.com/gigilin7/ArXiv-Dataset/assets/43805264/759817aa-53db-4949-898d-99bc17f05360" width="150" />

## Preprocessing
The downloaded paper will be in latex format and should be saved in json format
1. **Use the RedPajama script**
`
bash scripts/arxiv-kickoff-cleaning.sh
`

     * There is no cleaning after execution, so I try to use arxiv_cleaner.py directly ( arxiv_cleaner.py is the code for cleaning data by RedPajama)
     * Conclusion: It will be cleaned up too much, and the content such as title, author, abstract, etc. will be cleared

2. **Check online to see if there are any packages or codes available**
     * Conclusion: no suitable

3. **Write it myself** ✔
     * Idea: Use regex to find out the required content after observing the paper content ( not including references )
     * Method: divided into category, title, author, abstract, section (section is further divided into title, text, subsection)
     * Execution time: about 7 hours ( more than 2 million papers )
     * ⚠ The downloaded paper is a gz file, the encoding must use `ISO-8859-1` and `utf-8` is not available

* The result is as following
<br>⚠ Some papers have no category, so set `"category": ""`
<br>⚠ Some papers have no title after the abstract, so this part of the content will be treated as the same block

```json
{
    "id": "cond-mat0001001",
    "category": "cond-mat",
    "title": " Statistical thermodynamics of membrane bending mediated\nprotein-protein attractions",
    "author": "Tom Chou",
    "abstract": "Integral membrane proteins deform the surrounding bilayer\ncreating long-ranged forces that influence distant proteins. \nThese forces can be attractive or repulsive, depending on the\nproteins' shape, height, contact angle with the bilayer, as\nwell as the local membrane curvature.",
    "section": [
        {
            "title": "Introduction",
            "text": "Membrane proteins interact directly via screened\\nelectrostatic, van der Waal's, and hydrophobic forces. \\nThese are short ranged, operating typically over distances\\nof less than a nanometer.",
            "subsection": []
        },
        {
            "title": "Membrane inclusions and height deformation",
            "text": "Small membrane deformations (on the scale of the lipid or protein\\nmolecules) can be accurately modeled using standard plate theory.",
            "subsection": []
        },
        {
            "title": "Rotationally averaged interactions",
            "text": "",
            "subsection": [
                {
                    "title": "Zero background curvature",
                    "text": "\\n\\nFirst consider the case of two isolated proteins embedded in a\\nflat membrane.  In the absence of external mechanical forces\\nthat impose background membrane deformations, and with other\\ninclusions sufficiently far away."
                }
            ]
        }
    ]
}
```

* Run the following command to clean the downloaded files and save as json files:
```
python3 clean_data.py
```

## Data Filter
Almost every paper has a category displayed on the official website, which will appear in the file name ( exception: some papers will not have a category, the reason is unknown )
<br>https://arxiv.org/category_taxonomy

1. Filter out papers related to electricity
     * Filenames containing `eess` or `cond-mat` or `physics` are electricity-related categories
     * There are `2096748` articles in total, and there are `86035` articles related to electricity

2. Statistics and tokens
     * Filter out electricity-related paper statistics into the following json format
     * `each_file_token`: the number of tokens for each category of each paper
     * `each_file_token_total`: the total number of tokens for each category of all papers
     * `total`: There are a total of several papers and the total number of tokens of all papers and all categories

* Run the following command to count the tokens generated by the cleaning process:
```
python3 count_token.py
```
     
* Total tokens: `1080476015` ( "id": `491110`, "category": `233005`, "title": `1081319`, "author": `1064310`, "abstract": `13022915`, "section": `1064583356` )

* The format is as following

```json
{
    "each_file_token": [
        {
            "file": "physics0610057.json",
            "id": 4,
            "category": 1,
            "title": 19,
            "author": 5,
            "abstract": 453,
            "section": 22435
        },
        {
            "file": "cond-mat0001001.json",
            "id": 6,
            "category": 3,
            "title": 12,
            "author": 3,
            "abstract": 240,
            "section": 14532
        },
        {
            "file": "cond-mat0608474.json",
            "id": 6,
            "category": 3,
            "title": 10,
            "author": 5,
            "abstract": 118,
            "section": 5260
        },
    ],
    "each_file_token_total": {
        "id": 16,
        "category": 7,
        "title": 41,
        "author": 13,
        "abstract": 811,
        "section": 42227
    },
    "total": {
        "file": 3,
        "token": 43115
    }
}
```

## The size of data

* There are more than `2 million` arXiv papers (without preprocessing): `3.2T` in total
* There are more than `2 million` arXiv papers (pre-processed): `115G` in total
* There are more than `80,000` arXiv papers related to electricity (pre-processed): `3.3G` in total


## Merge json files
Merge the json files that filter out more than 80,000 papers related to electricity into one jsonl file

* Run the following command to merge json files into one jsonl file:
```
python3 merge_json.py
```

* The format is as following
```jsonl
{"id": "cond-mat0002097", "category": "cond-mat", "title": "Charge localization and phonon spectra in hole doped LaNiO", "author": "R. J. McQueeney, A. R. Bishop, and Ya-Sha Yi", "abstract": "The in-plane oxygen vibrations in La$_{2}$NiO$_{4}$ are investigated for \nseveral hole-doping concentrations both theoretically and experimentally via \ninelastic neutron scattering.  Using an inhomogeneous Hartree-Fock plus RPA \nnumerical method in a two-dimensional Peierls-Hubbard model, it is\nfound that the doping induces stripe ordering of localized charges,\nand that the strong electron-lattice coupling causes the in-plane \noxygen modes to split into two subbands. This result\nagrees with the phonon band splitting observed by inelastic neutron \nscattering in La$_{2-x}$Sr$_{x}$NiO$_{4}$.\nPredictions of strong electron-lattice coupling in La$_{2}$NiO$_{4}$,\nthe proximity of both oxygen-centered and nickel-centered charge\nordering, and the relation between charged stripe ordering and the\nsplitting of the in-plane phonon band upon doping are emphasized.", "section": [{"title": "Appendixes", "text": "", "subsection": []}]}
{"id": "cond-mat0004401", "category": "cond-mat", "title": "Particle dynamics in sheared granular matter", "author": "W. Losert, L. Bocquet,, T.C. Lubensky, \nand J.P. Gollub,", "abstract": "The particle dynamics and shear forces of granular\nmatter in a Couette geometry are determined experimentally.  \nThe normalized tangential velocity $V(y)$ declines strongly with distance\n$y$ from the moving wall,\nindependent of the shear rate and of the shear dynamics.\nLocal RMS velocity fluctuations \n$\\delta V(y)$\nscale with the local velocity gradient to the power $0.4 \\pm 0.05$. \nThese results agree with a locally Newtonian, \ncontinuum model, where the granular medium is assumed to behave as a \nliquid with a local temperature $\\delta V(y)^2$ and density dependent\nviscosity.", "section": [{"title": "Acknowledgments", "text": "We thank A. Liu, H. Jaeger and C. Bizon for helpful discussions.\\nPart of this work was supported by the National Science Foundation under \\nGrant DMR-9704301", "subsection": []}]}
```
<br>

>**⚠ It is normal for some data fields to be blank. The reasons are as followIing:**
>1. A small number of papers are formatted inconsistently, so this information is not available
>2. The paper does not have information in this field<br><br>
>**😊 Welcome to discuss with me how to solve the problem of inconsistent format 😊**

## Additional information
**ArXiv metadata set**
<br>https://github.com/mattbierbaum/arxiv-public-datasets

Someone organized the ArXiv data set ( json ), but it only contains the following items, and there is no full text

* The format is as following

```json
{
    "id": "ArXiv ID"
    "submitter": "Who submitted the paper"
    "authors": "Authors of the paper"
    "title": "Title of the paper"
    "comments": "Additional info, such as number of pages and figures"
    "journal-ref": "Information about the journal the paper was published in"
    "doi": "https://www.doi.org"
    "abstract": "The abstract of the paper"
    "categories": "Categories / tags in the ArXiv system"
    "versions": "A version history"
}
```
