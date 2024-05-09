# TODO[shchen]:  Remove this file and use session_token_manager instead.
import base64
import contextlib
import json
from typing import Generator, TypedDict

from snowflake import snowpark
import logging
logging.getLogger("snowflake.snowpark").setLevel(logging.FATAL)

from snowflakeray.deploy_client.utils import query_result_checker


class SessionToken(TypedDict):
    token: str
    expires_in: str


@contextlib.contextmanager
def generate_image_registry_credential(session: snowpark.Session) -> Generator[str, None, None]:
    """Construct basic auth credential that is specific to SPCS image registry. For image registry authentication, we
    will use a session token obtained from the Snowpark session object. The token authentication mechanism is
    automatically used when the username is set to "0sessiontoken" according to the registry implementation.

    As a workaround for SNOW-841699: Fail to authenticate to image registry with session token generated from
    Snowpark. We need to temporarily set the json query format in order to process GS token response. Note that we
    should set the format back only after registry authentication is complete, otherwise authentication will fail.

    Args:
        session: snowpark session

    Yields:
        base64-encoded credentials.
    """

    query_result = (
        query_result_checker.SqlResultValidator(
            session,
            query="SHOW PARAMETERS LIKE 'PYTHON_CONNECTOR_QUERY_RESULT_FORMAT' IN SESSION",
        )
        .has_dimensions(expected_rows=1)
        .validate()
    )
    prev_format = query_result[0].value
    try:
        session.sql("ALTER SESSION SET PYTHON_CONNECTOR_QUERY_RESULT_FORMAT = 'json'").collect()
        token = _get_session_token(session)
        yield _get_base64_encoded_credentials(username="0sessiontoken", password=json.dumps(token))
    finally:
        session.sql(f"ALTER SESSION SET PYTHON_CONNECTOR_QUERY_RESULT_FORMAT = '{prev_format}'").collect()


def _get_session_token(session: snowpark.Session) -> SessionToken:
    """
    This function retrieves the session token from a given Snowpark session object.

    Args:
        session: snowpark session.

    Returns:
        The session token string value.
    """
    ctx = session._conn._conn
    assert ctx._rest, "SnowflakeRestful is not set in session"
    token_data = ctx._rest._token_request("ISSUE")
    session_token = token_data["data"]["sessionToken"]
    validity_in_seconds = token_data["data"]["validityInSecondsST"]
    assert session_token, "session_token is not obtained successfully from the session object"
    assert validity_in_seconds, "validityInSecondsST is not obtained successfully from the session object"
    return {"token": session_token, "expires_in": validity_in_seconds}


def _get_base64_encoded_credentials(username: str, password: str) -> str:
    """This function returns the base64 encoded username:password, which is compatible with registry, such as
    SnowService image registry, that uses Docker credential helper.

    Args:
        username: username for authentication.
        password: password for authentication.

    Returns:
        base64 encoded credential string.

    """
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    return encoded_credentials
