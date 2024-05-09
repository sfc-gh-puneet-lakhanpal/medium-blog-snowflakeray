import copy
import logging
import os
import posixpath
import string
import tempfile
import time
from contextlib import contextmanager
from snowflake.snowpark import Session
from snowflake.core import Root
from snowflake.core.image_repository import ImageRepository
from typing import Any, Dict, Generator, Optional, cast
from snowflakeray.deploy_client.snowservice.file_utils import hash_directory
import importlib_resources
import yaml
from packaging import requirements
from typing_extensions import Unpack

from snowflakeray.deploy_client import snowservice
from snowflakeray.deploy_client.image_builds import (
    base_image_builder,
    client_image_builder,
    docker_context
)
from snowflakeray.deploy_client.snowservice import deploy_options, instance_types
from snowflakeray.deploy_client.utils import constants, snowservice_client

logging.getLogger("snowflake.snowpark").setLevel(logging.FATAL)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_or_create_image_repo(session: Session, image_repo_name: str) -> str:
    conn = session._conn._conn
    db = conn._database
    schema =conn._schema
    assert isinstance(db, str) and isinstance(schema, str)
    api_root = Root(session)
    image_repositories = api_root.databases[db].schemas[schema].image_repositories
    try:
        image_repo_model = image_repositories[image_repo_name].fetch()
    except Exception as e:
        new_image_repository = ImageRepository(
            name=image_repo_name
        )
        image_repo_model = image_repositories.create(new_image_repository).fetch()
    return str(image_repo_model.repository_url)

def _delete_image_repo(session: Session, image_repo_name: str) -> str:
    conn = session._conn._conn
    db = conn._database
    schema =conn._schema
    assert isinstance(db, str) and isinstance(schema, str)
    api_root = Root(session)
    image_repositories = api_root.databases[db].schemas[schema].image_repositories
    try:
        image_repo_properties = image_repositories[image_repo_name].fetch()
        image_repositories[image_repo_name].delete()
    except Exception as e:
        pass
def _get_full_image_name(image_repo: str, context_dir: str, image_name: str) -> str:
    """Return a valid full image name that consists of image name and tag. e.g
    org-account.registry.snowflakecomputing.com/db/schema/repo/image:latest

    Args:
        image_repo: image repo path, e.g. org-account.registry.snowflakecomputing.com/db/schema/repo
        context_dir: the local docker context directory, which consists everything needed to build the docker image.

    Returns:
        Full image name.
    """
    docker_context_dir_hash = hash_directory(
        context_dir, ignore_hidden=True
    )
    # By default, we associate a 'latest' tag with each of our created images for easy existence checking.
    # Additional tags are added for readability.
    return f"{image_repo}/{image_name}:{docker_context_dir_hash}"
    #return f"{image_repo}/{docker_context_dir_hash}:{constants.LATEST_IMAGE_TAG}"

def _get_full_image_name_latest(image_repo: str, image_name: str) -> str:
    """Return a valid full image name that consists of image name and tag. e.g
    org-account.registry.snowflakecomputing.com/db/schema/repo/image:latest

    Args:
        image_repo: image repo path, e.g. org-account.registry.snowflakecomputing.com/db/schema/repo
        context_dir: the local docker context directory, which consists everything needed to build the docker image.

    Returns:
        Full image name.
    """
    # By default, we associate a 'latest' tag with each of our created images for easy existence checking.
    # Additional tags are added for readability.
    return f"{image_repo}/{image_name}"
    #return f"{image_repo}/{docker_context_dir_hash}:{constants.LATEST_IMAGE_TAG}"


def _build_and_upload_image(session: Session, context_dir: str, image_repo: str, full_image_name: str) -> None:
    """Handles image build and upload to image registry.

    Args:
        context_dir: the local docker context directory, which consists everything needed to build the docker image.
        image_repo: image repo path, e.g. org-account.registry.snowflakecomputing.com/db/schema/repo
        full_image_name: Full image name consists of image name and image tag.
    """
    image_builder: base_image_builder.ImageBuilder
    image_builder = client_image_builder.ClientImageBuilder(
            context_dir=context_dir, full_image_name=full_image_name, image_repo=image_repo, session=session
    )
    image_builder.build_and_upload_image()
