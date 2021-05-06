"""
Include code to unpack manufacturer-specific data files into an interoperable netCDF format.
"""

from .metadata_convention import define_metadata_structure
from .metadata_convention import IMR_metadata_fill_in_Cruise
from .metadata_convention import IMR_metadata_fill_in_Calibration
from .metadata_convention import IMR_metadat_fill_in_AcousticCategory
from .metadata_convention import RAW_metadat_fill_in_Tables
from .metadata_convention import LSSS_config_maker