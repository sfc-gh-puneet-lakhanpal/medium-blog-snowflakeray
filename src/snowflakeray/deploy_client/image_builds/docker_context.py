import os
from typing import Optional
from typing import List
import os
import os
import shutil
import importlib_resources
from pathlib import Path
import string
from snowflakeray.docker_context_dir import ray_head, ray_worker
from snowflakeray.deploy_client.utils.constants import RayImageType
class DockerContext:
    """
    Constructs the Docker context directory required for image building.
    """

    def __init__(
        self,
        context_dir: str,
        image_type: str=RayImageType.IMAGE_TYPE_BASE,
        compute_pool_type: Optional[str]="CPU",
        base_full_image_name: Optional[str]="",
        pip_requirements: Optional[List]=None,
        ray_requirements: Optional[List]=None,
    ) -> None:
        """Initialization

        Args:
            context_dir: Path to context directory.
        """
        self.context_dir = context_dir
        self.compute_pool_type = compute_pool_type
        self.image_type = image_type
        if self.image_type not in [RayImageType.IMAGE_TYPE_BASE, RayImageType.IMAGE_TYPE_HEAD, RayImageType.IMAGE_TYPE_WORKER]:
            raise Exception("Invalid image type in docker context")
        if self.image_type in [RayImageType.IMAGE_TYPE_HEAD, RayImageType.IMAGE_TYPE_WORKER] and len(base_full_image_name)==0:
            raise Exception("Docker context for head and worker must contain base image full name")
        self.base_full_image_name = base_full_image_name
        if self.image_type == RayImageType.IMAGE_TYPE_BASE:
            self.pip_requirements = pip_requirements
            self.ray_requirements = ray_requirements
            self.pip_requirements_file_name = 'usecase_requirements.txt'
            self.ray_requirements_file_name = 'ray_requirements.txt'
        
    def _generate_pip_requirements_file(self) -> None:
        """
        Generates requirements based on pip requirements.
        """
        pip_requirements_file_path = os.path.join(self.context_dir, self.pip_requirements_file_name)
        with open(pip_requirements_file_path, "w", newline="") as pip_requirements_file:
            pip_requirements_file.writelines(line + '\n' for line in self.pip_requirements)
                
    def _generate_ray_requirements_file(self) -> None:
        ray_requirements_file_path = os.path.join(self.context_dir, self.ray_requirements_file_name)
        with open(ray_requirements_file_path, "w", newline="\n") as ray_requirements_file:
            ray_requirements_file.writelines(line + '\n' for line in self.ray_requirements)
    
    def _copy_cpu_or_gpu_docker_file(self) -> None:
        src_dir_path = os.path.join(self.context_dir, "templates")
        dest_dir_path = self.context_dir
        dest_name = "Dockerfile"
        if self.compute_pool_type.upper() == 'GPU':
            src_name = "Dockerfile.gpu"
        else:
            src_name = "Dockerfile.cpu"
        self._copy_and_rename(src_dir_path, dest_dir_path, src_name, dest_name)
        
    def _copy_docker_file_from_template_into_context_dir(self) -> None:
        src_dir_path = os.path.join(self.context_dir, "templates")
        dest_dir_path = self.context_dir
        dest_name = "Dockerfile"
        src_name = "Dockerfile"
        self._copy_and_rename(src_dir_path, dest_dir_path, src_name, dest_name)
        
    
    def _copy_and_rename(self, src_dir_path, dest_dir_path, src_name, dest_name):
        # Copy the file
        shutil.copy(os.path.join(src_dir_path, src_name), os.path.join(dest_dir_path, dest_name))
            
    def modify_docker_file_dependent_upon_base(self):
        if self.image_type == RayImageType.IMAGE_TYPE_HEAD:
            docker_file_template = (
                importlib_resources.files(ray_head)
                .joinpath("Dockerfile")  # type: ignore[no-untyped-call]
                .read_text("utf-8")
            )
        elif self.image_type == RayImageType.IMAGE_TYPE_WORKER:
            docker_file_template = (
                importlib_resources.files(ray_worker)
                .joinpath("Dockerfile")  # type: ignore[no-untyped-call]
                .read_text("utf-8")
            )
        if self.image_type in [RayImageType.IMAGE_TYPE_HEAD, RayImageType.IMAGE_TYPE_WORKER]:
            docker_file_path = os.path.join(self.context_dir, "Dockerfile")
            with open(docker_file_path, "w", encoding="utf-8") as dockerfile:
                dockerfile_content = string.Template(docker_file_template).safe_substitute(
                    {
                        "ray_base_container_image": self.base_full_image_name
                    }
                )
                dockerfile.write(dockerfile_content)
            
    def build(self):
        if self.image_type is RayImageType.IMAGE_TYPE_BASE:
            self._generate_pip_requirements_file()
            self._generate_ray_requirements_file()
            self._copy_cpu_or_gpu_docker_file()
        else:
            self._copy_docker_file_from_template_into_context_dir()
            self.modify_docker_file_dependent_upon_base()
