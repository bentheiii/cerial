from typing import Tuple, Optional

from abc import ABC, abstractmethod
from pathlib import Path


class VideoInterface(ABC):
    @abstractmethod
    def play(self, file: Path):
        pass

    @abstractmethod
    def status(self) -> Optional[Tuple[Path, float, float]]:
        # title of video, current time, total time
        pass

    @abstractmethod
    def close(self):
        pass
