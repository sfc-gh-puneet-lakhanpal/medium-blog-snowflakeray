import inspect
import logging
from typing import Any, Dict, List, Optional
from snowflakeray.deploy_client.utils import constants
logging.getLogger("snowflake.snowpark").setLevel(logging.FATAL)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class SnowServiceDeployOptions:
    def __init__(
        self,
        compute_pool: str,
        *,
        external_access_integrations: List[str],
        image_repo: Optional[str] = None,
        min_instances: Optional[int] = 1,
        max_instances: Optional[int] = 1,
        prebuilt_snowflake_image: Optional[str] = None,
        num_gpus: Optional[int] = 0,
        num_workers: Optional[int] = None,
        enable_remote_image_build: Optional[bool] = False,
        force_image_build: Optional[bool] = False,
        model_in_image: Optional[bool] = False,
        debug_mode: Optional[bool] = False,
        enable_ingress: Optional[bool] = False,
    ) -> None:
        """Initialization

        When updated, please ensure the type hint is updated accordingly at: //snowflake/ml/model/type_hints

        Args:
            compute_pool: SnowService compute pool name. Please refer to official doc for how to create a
                compute pool:
                https://docs.snowflake.com/en/developer-guide/snowpark-container-services/working-with-compute-pool
            external_access_integrations: External Access Integrations name used to build image and deploy the model.
                Please refer to the doc for how to create an External Access Integrations: https://docs.snowflake.com/
                developer-guide/snowpark-container-services/additional-considerations-services-jobs
                #configuring-network-capabilities .
                To make sure your image could be built, access to the following endpoint must be allowed.
                docker.com:80, docker.com:443, anaconda.com:80, anaconda.com:443, anaconda.org:80, anaconda.org:443,
                pypi.org:80, pypi.org:443
            image_repo: SnowService image repo path. e.g. "<image_registry>/<db>/<schema>/<repo>". Default to auto
                inferred based on session information.
            min_instances: Minimum number of service replicas. Default to 1.
            max_instances: Maximum number of service replicas. Default to 1.
            prebuilt_snowflake_image: When provided, the image-building step is skipped, and the pre-built image from
                Snowflake is used as is. This option is for users who consistently use the same image for multiple use
                cases, allowing faster deployment. The snowflake image used for deployment is logged to the console for
                future use. Default to None.
            num_gpus: Number of GPUs to be used for the service. Default to 0.
            num_workers: Number of workers used for model inference. Please ensure that the number of workers is set
                lower than the total available memory divided by the size of model to prevent memory-related issues.
                Default is number of CPU cores * 2 + 1.
            enable_remote_image_build: When set to True, will enable image build on a remote SnowService job.
                Default is True.
            force_image_build: When set to True, an image rebuild will occur. The default is False, which means the
                system will automatically check whether a previously built image can be reused
            model_in_image: When set to True, image would container full model weights. The default if False, which
                means image without model weights and we do stage mount to access weights.
            debug_mode: When set to True, deployment artifacts will be persisted in a local temp directory.
            enable_ingress: When set to True, will expose HTTP endpoint for access to the predict method of the created
                service. Default to False.
        """

        self.compute_pool = compute_pool
        self.image_repo = image_repo
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.prebuilt_snowflake_image = prebuilt_snowflake_image
        self.num_gpus = num_gpus
        self.num_workers = num_workers
        self.enable_remote_image_build = enable_remote_image_build
        self.force_image_build = force_image_build
        self.model_in_image = model_in_image
        self.debug_mode = debug_mode
        self.enable_ingress = enable_ingress
        self.external_access_integrations = external_access_integrations

        if self.num_workers is None and self.use_gpu:
            logger.info("num_workers has been defaulted to 1 when using GPU.")
            self.num_workers = 1

    @property
    def use_gpu(self) -> bool:
        return self.num_gpus is not None and self.num_gpus > 0

    @classmethod
    def from_dict(cls, options_dict: Dict[str, Any]) -> "SnowServiceDeployOptions":
        """Construct SnowServiceDeployOptions instance based from an option dictionary.

        Args:
            options_dict: The dict containing various deployment options.

        Raises:
            SnowflakeMLException: When required option is missing.

        Returns:
            A SnowServiceDeployOptions object
        """
        required_options = [constants.COMPUTE_POOL]
        missing_keys = [key for key in required_options if options_dict.get(key) is None]
        if missing_keys:
            raise Exception(f"Must provide options when deploying to Snowpark Container Services: {', '.join(missing_keys)}")
        supported_options_keys = inspect.signature(cls.__init__).parameters.keys()
        filtered_options = {k: v for k, v in options_dict.items() if k in supported_options_keys}
        return cls(**filtered_options)
