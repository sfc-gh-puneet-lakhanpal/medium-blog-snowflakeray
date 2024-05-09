use role container_user_role;

use database container_hol_db;
use schema public;

SHOW COMPUTE POOLS LIKE 'RAY_HEAD_CPDISTRIBUTEDMODELTRAININGONGPU';

show compute pools like 'RAY_WORKER_CPDISTRIBUTEDMODELTRAININGONGPU';

CALL SYSTEM$GET_SERVICE_STATUS('CONTAINER_HOL_DB.PUBLIC.SPCSRAYHEADSERVICEDISTRIBUTEDMODELTRAININGONGPU');

SHOW endpoints in service SPCSRAYHEADSERVICE;

CALL SYSTEM$GET_SERVICE_STATUS('CONTAINER_HOL_DB.PUBLIC.SPCSRAYHEADSERVICEDISTRIBUTEDMODELTRAININGONGPU');