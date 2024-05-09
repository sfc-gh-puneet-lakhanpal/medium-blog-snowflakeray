# SnowflakeRay - Python library for setting up Ray in Snowpark Container Services with ease

Note: This library is not under the scope for Snowflake Support. 

### Prerequisites

1. Docker Desktop or Docker Community edition with BuildKit instaled.
2. Snowpark Container Services (SPCS) Port ranges enabled on the Snowflake account (opt-in currently). Reach out to your Snowflake account team. 

### Step 1: Pre-requisites
Run the SQL based code in `use cases/setup-ray-prerequisites.sql`. Either use SQL worksheet or Visual Studio with Snowflake extension.

### Step 2: Create a conda environment and install SnowflakeRay

```
conda create -n snowflakeray python=3.11
conda activate snowflakeray
pip install ./dist/snowflakeray-1.0.0-py3-none-any.whl
pip install ipykernel
```

### Step 3: Execute the notebook to setup Ray on SPCS

Put your credentials in `use cases/llmserving/creds.json` and Run notebook `use cases/llmserving/setup-ray-for-llmserving.ipynb` as an example. 

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