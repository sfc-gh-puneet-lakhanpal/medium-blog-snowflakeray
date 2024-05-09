from enum import Enum


class ResourceType(Enum):
    SERVICE = "service"
    JOB = "job"
    
class RayImageType(Enum):
    IMAGE_TYPE_BASE = "BASE"
    IMAGE_TYPE_HEAD = "HEAD"
    IMAGE_TYPE_WORKER = "WORKER"
    
class ResourceStatus(Enum):
    UNKNOWN = "UNKNOWN"  # status is unknown because we have not received enough data from K8s yet.
    PENDING = "PENDING"  # resource set is being created, can't be used yet
    READY = "READY"  # resource set has been deployed.
    DELETING = "DELETING"  # resource set is being deleted
    FAILED = "FAILED"  # resource set has failed and cannot be used anymore
    DONE = "DONE"  # resource set has finished running
    NOT_FOUND = "NOT_FOUND"  # not found or deleted
    INTERNAL_ERROR = "INTERNAL_ERROR"  # there was an internal service error.


RESOURCE_TO_STATUS_FUNCTION_MAPPING = {
    ResourceType.SERVICE: "SYSTEM$GET_SERVICE_STATUS",
    ResourceType.JOB: "SYSTEM$GET_JOB_STATUS",
}

CPU_CONSTANT = 'CPU'
GPU_CONSTANT = 'GPU'
HIGH_MEM_CONSTANT = 'HIGH_MEM'

INSTANCE_TYPE_MAPPING = {
    'CPU_X64_XS': CPU_CONSTANT,
    'CPU_X64_S': CPU_CONSTANT,
    'CPU_X64_M': CPU_CONSTANT,
    'CPU_X64_L': CPU_CONSTANT,
    'HIGHMEM_X64_S': CPU_CONSTANT,
    'HIGHMEM_X64_M': CPU_CONSTANT,
    'HIGHMEM_X64_L': CPU_CONSTANT,
    'GPU_NV_S': GPU_CONSTANT,
    'GPU_NV_M': GPU_CONSTANT,
    'GPU_NV_L': GPU_CONSTANT
}

CPU_COMPUTE_POOL_CORES_MAPPING = {
    2: 'CPU_X64_XS',
    4: 'CPU_X64_S',
    8: 'CPU_X64_M',
    32: 'CPU_X64_L'
}

HIGH_MEMORY_COMPUTE_POOL_CORES_MAPPING = {
    8: 'HIGHMEM_X64_S',
    32: 'HIGHMEM_X64_M',
    128: 'HIGHMEM_X64_L'
}

GPU_COMPUTE_POOL_MAPPING = {
    1: 'GPU_NV_S',
    4: 'GPU_NV_M',
    8: 'GPU_NV_L'
}

CPU_COMPUTE_POOL_CORES_LIST = list(CPU_COMPUTE_POOL_CORES_MAPPING.keys())
HIGH_MEMORY_COMPUTE_POOL_CORES_LIST = list(HIGH_MEMORY_COMPUTE_POOL_CORES_MAPPING.keys())
GPU_COMPUTE_POOL_LIST = list(GPU_COMPUTE_POOL_MAPPING.keys())


COMPUTE_POOL_MEMORY_MAPPING = {
    'CPU_X64_XS': 8,
    'CPU_X64_S': 16,
    'CPU_X64_M': 32,
    'CPU_X64_L': 128,
    'HIGHMEM_X64_S': 64,
    'HIGHMEM_X64_M': 256,
    'HIGHMEM_X64_L': 1024,
    'GPU_NV_S': 32,
    'GPU_NV_M': 192,
    'GPU_NV_L': 1152
}

COMPUTE_POOL_CORES_MAPPING = {
    'CPU_X64_XS': 2,
    'CPU_X64_S': 4,
    'CPU_X64_M': 8,
    'CPU_X64_L': 32,
    'HIGHMEM_X64_S': 8,
    'HIGHMEM_X64_M': 32,
    'HIGHMEM_X64_L': 128,
    'GPU_NV_S': 8,
    'GPU_NV_M': 48,
    'GPU_NV_L': 96
}

COMPUTE_POOL_GPU_MAPPING = {
    'CPU_X64_XS': None,
    'CPU_X64_S': None,
    'CPU_X64_M': None,
    'CPU_X64_L': None,
    'HIGHMEM_X64_S': None,
    'HIGHMEM_X64_M': None,
    'HIGHMEM_X64_L': None,
    'GPU_NV_S': 1,
    'GPU_NV_M': 4,
    'GPU_NV_L': 8
}


GPU_COMPUTE_POOL_CORES_MAPPING = {
    'GPU_NV_S': 8,
    'GPU_NV_M': 48,
    'GPU_NV_L': 96
}


RAY_HEAD_COMPUTE_POOL_NAME = "RAY_HEAD_CP"
RAY_WORKER_COMPUTE_POOL_NAME = "RAY_WORKER_CP"

"""Image build related constants"""
RAY_IMAGE_REPO_NAME = "spcs_ray_image_repo"
RAY_HEAD_CONTAINER_NAME = "head"
RAY_WORKER_CONTAINER_NAME = "worker"
RAY_HEAD_SERVICE_NAME = "SPCSRAYHEADSERVICE"
RAY_WORKER_SERVICE_NAME = "SPCSRAYWORKERSERVICE"
PUBLIC_ENDPOINTS_WAIT_TIME_SECS = 20
DHSM_MEMORY_FACTOR = 0.1
INSTANCE_AVAILABLE_MEMORY_FOR_RAY_FACTOR = 0.8
RAY_PROMETHEUS_CONTAINER_NAME = "prometheus"
RAY_GRAFANA_CONTAINER_NAME = "grafana"
RAY_BASE_IMAGE_NAME_IN_IMAGE_REPO = "ray_base"
RAY_GRAFANA_IMAGE_NAME_IN_IMAGE_REPO = "ray_grafana"
RAY_PROMETHEUS_IMAGE_NAME_IN_IMAGE_REPO = "ray_prometheus"
RAY_HEAD_IMAGE_NAME_IN_IMAGE_REPO = "ray_head"
RAY_WORKER_IMAGE_NAME_IN_IMAGE_REPO = "ray_worker"
RAY_HEAD_SPEC_TEMPLATE = "ray_head_template.yaml"
RAY_WORKER_SPEC_TEMPLATE = "ray_worker_template.yaml"
RAY_HEAD_SPEC_OUTPUT = "ray_head.yaml"
RAY_WORKER_SPEC_OUTPUT = "ray_worker.yaml"
UI_PORTS = 4
RAY_LOGS_REGULAR_STORAGE_NAME = "ray_logs"
BLOCK_STORAGE_NAME = 'block'
DEFAULT_BLOCK_STORAGE_SIZE_FOR_RAY_LOGS = '10Gi'
SNOW_OBJECT_IDENTIFIER_MAX_LENGTH = 255
MIN_DSHM_MEMORY = 11