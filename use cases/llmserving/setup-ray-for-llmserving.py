from snowflakeray.cluster_init import SnowflakeRay
from snowflake.snowpark import Session
import json
from pprint import pprint
def get_snowpark_session()->Session:
    with open('creds.json') as f:
        data = json.load(f)
        username = data['username']
        password = data['password']
        account = data["account"]
        warehouse = data["warehouse"]
        database = data["database"]
        schema = data["schema"]
        role = data["role"]


    CONNECTION_PARAMETERS = {
        'account': account,
        'user': username,
        'password': password,
        'schema': schema,
        'database': database,
        'warehouse': warehouse,
        'role': role,
        "session_parameters": {"PYTHON_CONNECTOR_QUERY_RESULT_FORMAT": "json"}
    }
    session = Session.builder.configs(CONNECTION_PARAMETERS).create()
    return session
    
def create_my_custom_compute_pools(session:Session):
    head_compute_pool_name = "RAY_HEAD_CP_LLM_SERVING"
    ray_head_cp_sql = f"""
        create compute pool if not exists {head_compute_pool_name}
            min_nodes = 1
            max_nodes = 1
            instance_family = GPU_NV_S
            auto_resume = TRUE
            AUTO_SUSPEND_SECS = 3600;
    """
    worker_compute_pool_name = "RAY_WORKER_CP_LLM_SERVING"
    ray_worker_cp_sql = f"""
        create compute pool if not exists {worker_compute_pool_name}
            min_nodes = 2
            max_nodes = 2
            instance_family = GPU_NV_M
            auto_resume = TRUE
            AUTO_SUSPEND_SECS = 3600;
    """
    session.sql(ray_head_cp_sql).collect()
    session.sql(ray_worker_cp_sql).collect()
    return [head_compute_pool_name, worker_compute_pool_name]

def setupmyraycluster():
    session = get_snowpark_session()
    project_name = "llm serving"
    [head_compute_pool_name, worker_compute_pool_name] = create_my_custom_compute_pools(session)
    snowflake_ray = SnowflakeRay(session=session, project_name=project_name, 
                             head_compute_pool_name=head_compute_pool_name, 
                             worker_compute_pool_name=worker_compute_pool_name)
    endpoints = snowflake_ray.setup_ray_cluster(stage_name_for_specs="RAY_SPECS", stage_name_for_artifacts="ARTIFACTS", 
                                            external_access_integrations=["ALLOW_ALL_EAI"], 
                                            ray_requirements=["ray[data]==2.10.0", "ray[client]==2.10.0", "ray[default]==2.10.0", 
                                                              "ray[serve]==2.10.0"],
                                            pip_requirements=["jupyterlab", "py-spy", "ipywidgets", "virtualenv", "datasets==2.18.0", 
                                                              "numpy", "transformers==4.39.3", "evaluate", "torch==2.1.2", 
                                                              "accelerate==0.29.3", "tokenizers==0.15.2", "pandas==1.5.3", 
                                                              "pytorch_lightning==2.0.3", "deepspeed==0.14.1", "sentencepiece==0.2.0", 
                                                              "torchvision==0.16.2", "bitsandbytes==0.43.1", "tiktoken==0.6.0", 
                                                              "tqdm==4.66.2", "vllm==0.4.0", "xformers==0.0.23.post1", 
                                                              "huggingface-hub==0.22.2", "sentence-transformers"])
    print("Printing public endpoints")
    pprint(endpoints)
    session.close()
    
if __name__ == '__main__':
    setupmyraycluster()