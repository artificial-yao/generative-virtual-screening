<h2><img align="center" src="https://github.com/NVIDIA-BioNeMo-blueprints/generative-virtual-screening/blob/main/nvidia-logo.png?raw=true">NVIDIA BioNeMo Blueprint: Generative Virtual Screening for Drug Discovery</h2>

![Generative Virtual Screening for Drug Discovery-r2 (1)](https://github.com/user-attachments/assets/dbb1795a-7e3f-4363-9b20-4bc4d67d04bb)

The NVIDIA BioNeMo Blueprint for generative virtual screening shows how generative AI and accelerated NIM microservices can be used to design optimized small molecules smarter and faster.

<hr>

### Quick Start 

##### Steps to run the self-driving in-silico virtual screening pipeline
Step 1. Start docker container for MolMIM NIM and DiffDock NIM.

```bash
cd deploy
./launch.sh
```

Note: sometimes DiffDock container needs to restart (I am not sure why). The first time often times it fails.

Step 2. Set up bionemo-framework and folder structure. 

Since DSMBind model is not implemented as a NIM yet, we need to use bionemo-framework to start the docker container. Please use the ["release-v1.10-virtual-screening" forked and edited branch](https://github.com/artificial-yao/bionemo-framework/tree/release-v1.10-virtual-screening). 

My folder structure is shown below:
projects
├── generative-virtual-screening         # this repo
├── bionemo-framework                    # bionemo-framework repo as mentioned
...

Then, in order to see "generative-virtual-screening" folder inside of bionemo-framework docker container, create a symbolic link.

```bash
cd projects
ln -s generative-virtual-screening bionemo-framework/generative-virtual-screening
```


The steps to do this is to clone the above branch of bionemo-framework and start the bionemo-framework docker container. You want to follow steps in the README file step-by-step to set everything up. launch.sh is edited for this project. We use port 8002 and 8003 for MolMIM and DiffDock: the ports forwarding needs to happen so that we can call the NIMs inside of bionemmo-framework docker container. Volune mounting is added as well. 

Step 3. Start bionemo-framework docker container for development. 

After you follow the steps in README in bionemo-framework repo, then do the following:

```bash
cd bionemo-framework
./launch.sh dev -s
```

Step 4. Now you should have three docker containers running. If you use VS Code, start a docker container editing environment so you can edit and run jupyter notebooks and python files. You can attach VS Code to the running bionemo-framework docker container.

Step 5. You can either run the src/self-driving-demo.ipynb in an interactive environment, or run below commands:

```bash
cd generative-virtual-screening/src
python self-driving-demo.py
```

### Get Started

* [Deploy](deploy/)
* [Source code](src/)

### Set Up With Docker Compose

Navigate to the [deploy](deploy/) directory to learn how to start up the NIMs.

## Notebook

An example of how to call each generative virtual screening step is located in `src/generative-virtual-screening.ipynb`.

### Additional Documentation

Additional documentation can be found on [docs.nvidia.com](https://nim-docs-staging.s3.us-west-1.amazonaws.com/bionemo-caddvs/main/overview.html).

