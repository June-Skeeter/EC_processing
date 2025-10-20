# Writes high-frequency data file in the custom "EPF32" format.
from ..siteMetadata.siteAttributes import siteAttributes
from dataclasses import dataclass, field

@dataclass(kw_only=True)
class epf32(siteAttributes):
    sourceFile: str
    measurementType: str = 'highfrequency'

    def __post_init__(self):
        super().__post_init__()


