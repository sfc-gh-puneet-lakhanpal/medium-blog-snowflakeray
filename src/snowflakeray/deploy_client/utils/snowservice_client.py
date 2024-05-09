import json
import logging
import textwrap
import time
from typing import List, Optional

from snowflakeray.deploy_client.utils import log_stream_processor
from snowflakeray.deploy_client.utils import constants
from snowflake.snowpark import Session

logger = logging.getLogger(__name__)


class SnowServiceClient:
    """
    SnowService client implementation: a Python wrapper for SnowService SQL queries.
    """

    def __init__(self, session: Session) -> None:
        """Initialization

        Args:
            session: Snowpark session
        """
        self.session = session

    def create_image_repo(self, repo_name: str) -> None:
        self.session.sql(f"CREATE IMAGE REPOSITORY IF NOT EXISTS {repo_name}").collect()

    def create_or_replace_service(
        self,
        service_name: str,
        compute_pool: str,
        spec_stage_location: str,
        spec_file_name: str,
        external_access_integrations: List[str],
        *,
        min_instances: Optional[int] = 1,
        max_instances: Optional[int] = 1,
        query_warehouse: Optional[str] = ""
    ) -> None:
        """Create or replace service. Since SnowService doesn't support the CREATE OR REPLACE service syntax, we will
        first attempt to drop the service if it exists, and then create the service. Please note that this approach may
        have side effects due to the lack of transaction support.

        Args:
            service_name: Name of the service.
            min_instances: Minimum number of service replicas.
            max_instances: Maximum number of service replicas.
            external_access_integrations: EAIs for network connection.
            compute_pool: Name of the compute pool.
            spec_stage_location: Stage path for the service spec.
            spec_file_name: Spec file name
        """
        self._drop_service_if_exists(service_name)
        if len(query_warehouse)>0:
            sql = textwrap.dedent(
                f"""
                CREATE SERVICE {service_name}
                    IN COMPUTE POOL {compute_pool}
                    FROM {spec_stage_location}
                    SPEC = '{spec_file_name}'
                    MIN_INSTANCES={min_instances}
                    MAX_INSTANCES={max_instances}
                    EXTERNAL_ACCESS_INTEGRATIONS = ({', '.join(external_access_integrations)})
                    QUERY_WAREHOUSE = {query_warehouse}
                """
            )
        else:
            sql = textwrap.dedent(
                f"""
                CREATE SERVICE {service_name}
                    IN COMPUTE POOL {compute_pool}
                    FROM {spec_stage_location}
                    SPEC = '{spec_file_name}'
                    MIN_INSTANCES={min_instances}
                    MAX_INSTANCES={max_instances}
                    EXTERNAL_ACCESS_INTEGRATIONS = ({', '.join(external_access_integrations)})
                """
            )
        logger.info(f"Creating service {service_name}")
        logger.debug(f"Create service with SQL: \n {sql}")
        self.session.sql(sql).collect()


    def _drop_service_if_exists(self, service_name: str) -> None:
        """Drop service if it already exists.

        Args:
            service_name: Name of the service.
        """
        self.session.sql(f"DROP SERVICE IF EXISTS {service_name}").collect()

    def block_until_resource_is_ready(
        self,
        resource_name: str,
        resource_type: constants.ResourceType,
        *,
        max_retries: int = 180,
        container_name: str,
        retry_interval_secs: int = 10,
    ) -> None:
        """Blocks execution until the specified resource is ready.
        Note that this is a best-effort approach because when launching a service, it's possible for it to initially
        fail due to a system error. However, SnowService may automatically retry and recover the service, leading to
        potential false-negative information.

        Args:
            resource_name: Name of the resource.
            resource_type: Type of the resource.
            container_name: The container to query the log from.
            max_retries: The maximum number of retries to check the resource readiness (default: 60).
            retry_interval_secs: The number of seconds to wait between each retry (default: 10).

        Raises:
            SnowflakeMLException: If the resource received the following status [failed, not_found, internal_error,
                deleting]
            SnowflakeMLException: If the resource does not reach the ready/done state within the specified number
                of retries.
        """
        assert resource_type == constants.ResourceType.SERVICE or resource_type == constants.ResourceType.JOB
        query_command = ""
        if resource_type == constants.ResourceType.SERVICE:
            query_command = f"CALL SYSTEM$GET_SERVICE_LOGS('{resource_name}', '0', '{container_name}')"
        elif resource_type == constants.ResourceType.JOB:
            query_command = f"CALL SYSTEM$GET_JOB_LOGS('{resource_name}', '{container_name}')"
        logger.warning(
            f"Best-effort log streaming from SPCS will be enabled when python logging level is set to INFO."
            f"Alternatively, you can also query the logs by running the query '{query_command}'"
        )
        lsp = log_stream_processor.LogStreamProcessor()

        for attempt_idx in range(max_retries):
            if logger.level <= logging.INFO:
                resource_log = self.get_resource_log(
                    resource_name=resource_name,
                    resource_type=resource_type,
                    container_name=container_name,
                )
                lsp.process_new_logs(resource_log, log_level=logging.INFO)

            status = self.get_resource_status(resource_name=resource_name, resource_type=resource_type)
            
            if resource_type == constants.ResourceType.JOB and status == constants.ResourceStatus.DONE:
                return
            elif resource_type == constants.ResourceType.SERVICE and status == constants.ResourceStatus.READY:
                return

            if (
                status
                in [
                    constants.ResourceStatus.FAILED,
                    constants.ResourceStatus.NOT_FOUND,
                    constants.ResourceStatus.INTERNAL_ERROR,
                    constants.ResourceStatus.DELETING,
                ]
                or attempt_idx >= max_retries - 1
            ):
                if logger.level > logging.INFO:
                    resource_log = self.get_resource_log(
                        resource_name=resource_name,
                        resource_type=resource_type,
                        container_name=container_name,
                    )
                    # Show full error log when logging level is above INFO level. For INFO level and below, we already
                    # show the log through logStreamProcessor above.
                    logger.error(resource_log)

                error_message = "failed"
                if attempt_idx >= max_retries - 1:
                    error_message = "does not reach ready/done status"

                if resource_type == constants.ResourceType.SERVICE:
                    self._drop_service_if_exists(service_name=resource_name)

                raise Exception("{resource_type} {resource_name} {error_message}." f"\nStatus: {status if status else ''} \n")
            time.sleep(retry_interval_secs)

    def get_resource_log(
        self, resource_name: str, resource_type: constants.ResourceType, container_name: str
    ) -> Optional[str]:
        if resource_type == constants.ResourceType.SERVICE:
            try:
                row = self.session.sql(
                    f"CALL SYSTEM$GET_SERVICE_LOGS('{resource_name}', '0', '{container_name}')"
                ).collect()
                return str(row[0]["SYSTEM$GET_SERVICE_LOGS"])
            except Exception:
                return None
        elif resource_type == constants.ResourceType.JOB:
            try:
                row = self.session.sql(f"CALL SYSTEM$GET_JOB_LOGS('{resource_name}', '{container_name}')").collect()
                return str(row[0]["SYSTEM$GET_JOB_LOGS"])
            except Exception:
                return None
        else:
            raise Exception(f"{resource_type.name} is not yet supported in get_resource_log function")

    def get_resource_status(
        self, resource_name: str, resource_type: constants.ResourceType
    ) -> Optional[constants.ResourceStatus]:
        """Get resource status.

        Args:
            resource_name: Name of the resource.
            resource_type: Type of the resource.

        Raises:
            SnowflakeMLException: If resource type does not have a corresponding system function for querying status.
            SnowflakeMLException: If corresponding status call failed.

        Returns:
            Optional[constants.ResourceStatus]: The status of the resource, or None if the resource status is empty.
        """
        if resource_type not in constants.RESOURCE_TO_STATUS_FUNCTION_MAPPING:
            raise Exception(f"Status querying is not supported for resources of type '{resource_type}'.")
        status_func = constants.RESOURCE_TO_STATUS_FUNCTION_MAPPING[resource_type]
        try:
            row = self.session.sql(f"CALL {status_func}('{resource_name}');").collect()
        except Exception:
            # Silent fail as SPCS status call is not guaranteed to return in time. Will rely on caller to retry.
            return None

        resource_metadata = json.loads(row[0][status_func])[0]
        logger.debug(f"Resource status metadata: {resource_metadata}")
        if resource_metadata and resource_metadata["status"]:
            try:
                status = resource_metadata["status"]
                return constants.ResourceStatus(status)
            except ValueError:
                logger.warning(f"Unknown status returned: {status}")
        return None
