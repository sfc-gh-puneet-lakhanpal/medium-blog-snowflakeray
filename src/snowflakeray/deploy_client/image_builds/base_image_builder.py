from abc import ABC, abstractmethod


class ImageBuilder(ABC):
    """
    Abstract class encapsulating image building and upload to SPCS.
    """

    @abstractmethod
    def build_and_upload_image(self) -> None:
        """Builds and uploads an image to SPCS."""
        pass
