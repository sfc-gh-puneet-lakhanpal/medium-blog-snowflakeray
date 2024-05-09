# SnowflakeRay - Python library for setting up Ray in Snowpark Container Services with ease (EC2 setup guidelines)

Note: This library is not under the scope for Snowflake Support. 

### Prerequisites

1. Docker Desktop or Docker Community edition with BuildKit instaled.
2. Snowpark Container Services (SPCS) Port ranges enabled on the Snowflake account (opt-in currently). Reach out to your Snowflake account team. 

### Step 1: Pre-requisites
Run the SQL based code in `use cases/setup-ray-prerequisites.sql`. Either use SQL worksheet or Visual Studio with Snowflake extension.

#### Connect to EC2
Connect via AWS SSM
#### Update and install aws cli and anaconda

```sudo apt-get update
sudo apt-get install unzip
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws configure
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
. ~/.bashrc
```

#### Update and install docker

```sudo apt-get update && sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl start docker
sudo docker run hello-world
sudo systemctl enable docker
sudo usermod -a -G docker $(whoami)
```

#### Logout and log back in
In order for docker to take effect, we need to logout and log back in. Run `docker info` to make sure docker installation worked.

Setup SSH to connect via AWS SSM on your local machine: https://dev.to/aws-builders/how-to-set-up-session-manager-and-enable-ssh-over-ssm-43k9 and then upload `creds.json`, `setup-ray-for-llmserving.py` and `snowflakeray-1.0.0-py3-none-any.whl` using scp by using the syntax below.

`scp -i ~/Downloads/<yourkey.pem> <yourfile> ubuntu@<instance-id>:/home/ubuntu/<yourfile>`


### Step 2: Create a conda environment and install SnowflakeRay

```
conda create -n snowflakeray python=3.11
conda activate snowflakeray
pip install ./dist/snowflakeray-1.0.0-py3-none-any.whl
pip install ipykernel
```

### Step 3: Execute the python script to setup Ray on SPCS

Put your credentials in `creds.json` on the ec2 machine and run python script with the following syntax `python setup-ray-for-llmserving.py` within the conda environment snowflakeray. 

Once the snowflake_ray.setup_ray_cluster command is run, it will spit out endpoints for notebook. Use that public endpoint and login into jupyter.

### Optional step:
Upload the content from `use cases/llmserving/notebooks` folder into the jupyter service hosted in SPCS under the path `/home/artifacts`. This path is a persistent path and the content in this folder is backed by a snowflake stage. Even after the compute pools or services are destroyed, the snowflake stage and the content within the stage stays as designed.

Then execute `Ray Serve Deployment.ipynb` first followed by `test_local_vllm_chat.ipynb`

##### Things to note:
* Block storage PrPr is optional here. you can add or remove need_block_storage_for_ray_logs parameter. If need_block_storage_for_ray_logs = True, it automatically uses SPCS block storage for storing Ray metrics. If the parameter is omitted, regular SPCS S3 backed storage is used. Ray dashboard metrics load much faster with SPCS block storage, so SPCS block storage PrPr is recommended.
* If pip_requirements list is left empty or pip_requirements parameter is not provided, it will automatically install ["jupyterlab", "pandas", "py-spy", "ipywidgets", "virtualenv", "starlette<=0.34.0"]
* If ray_requirements list is left empty or ray_requirements parameter is not provided, it will automatically install 
["ray[data]==2.9.3", "ray[client]==2.9.3", "ray[default]==2.9.3", "ray[serve]==2.9.3"]
* Use admin username and admin password to login into grafana url.