from dataclasses import dataclass
import re


PERMISSION_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_-]+\.[a-z][a-z0-9_-]+$')


@dataclass(frozen=True, slots=True)
class FeaturePermission:
    name: str
    resource: str
    action: str

    def __post_init__(self) -> None:
        if not PERMISSION_NAME_PATTERN.fullmatch(self.name):
            raise ValueError(f'Invalid permission name: {self.name}')
        if self.name != f'{self.resource}.{self.action}':
            raise ValueError(
                f'Permission {self.name} must match {self.resource}.{self.action}.'
            )
