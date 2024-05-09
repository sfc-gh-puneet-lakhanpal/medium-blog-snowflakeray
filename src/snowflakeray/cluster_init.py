import logging
from snowflakeray.deploy_client.utils.cluster_init_helper import InternalSPCSRayCluster
from snowflake.snowpark import Session
from typing import Optional, List
logging.getLogger("snowflake.connector").setLevel(logging.FATAL)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class SnowflakeRay():
    def __init__(self, session: Session, project_name:str, head_compute_pool_name:Optional[str]=None, worker_compute_pool_name:Optional[str]=None) -> None:
        self.spcs_ray_cluster = InternalSPCSRayCluster(session=session, project_name=project_name, head_compute_pool_name=head_compute_pool_name, worker_compute_pool_name=worker_compute_pool_name)
    
    def setup_ray_cluster(self, stage_name_for_specs:str, stage_name_for_artifacts:str, compute_pool_type:Optional[str]='CPU', num_worker_nodes:Optional[int]=0, requested_num_worker_gpus:Optional[int]=None, requested_num_head_gpus:Optional[int]=None, requested_num_head_cores:Optional[int]=None, requested_num_worker_cores:Optional[int]=None, pip_requirements:Optional[List]=None, ray_requirements:Optional[List]=None, force_image_build:Optional[bool]=False, external_access_integrations:Optional[List]=[],need_block_storage_for_ray_logs:Optional[bool]=False, query_warehouse:Optional[str]="") -> dict:
        public_endpoints = self.spcs_ray_cluster.setup_ray_cluster(compute_pool_type=compute_pool_type, num_worker_nodes=num_worker_nodes, stage_name_for_specs=stage_name_for_specs, stage_name_for_artifacts=stage_name_for_artifacts, requested_num_worker_gpus=requested_num_worker_gpus, requested_num_head_gpus=requested_num_head_gpus, requested_num_head_cores=requested_num_head_cores, requested_num_worker_cores=requested_num_worker_cores, pip_requirements=pip_requirements, ray_requirements=ray_requirements, force_image_build=force_image_build, external_access_integrations=external_access_integrations, need_block_storage_for_ray_logs=need_block_storage_for_ray_logs, query_warehouse=query_warehouse)
        return public_endpoints

    def delete_all_services(self):
        self.spcs_ray_cluster.delete_all_services()

    def suspend_all_compute_pools(self):
        self.spcs_ray_cluster.suspend_all_compute_pools()
        
    def delete_all_compute_pools(self):
        self.spcs_ray_cluster.delete_all_compute_pools()
        
    def delete_ray_image_repo(self):
        self.spcs_ray_cluster.delete_ray_image_repository()
        
    def get_ray_head_logs(self):
        return self.spcs_ray_cluster.get_ray_head_logs()
        
    def get_ray_worker_logs(self):
        return self.spcs_ray_cluster.get_ray_worker_logs()
        
    def get_ray_head_service_status(self):
        return self.spcs_ray_cluster.get_ray_head_service_status()
        
    def get_ray_worker_service_status(self):
        return self.spcs_ray_cluster.get_ray_worker_service_status()
    
    def get_public_endpoints(self):
        return self.spcs_ray_cluster.get_public_endpoints()
 