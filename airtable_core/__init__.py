# -*- coding: utf-8 -*-

"""Top-level package for airtable_core."""

__author__ = "Brian Whitney"
__email__ = "brian.whitney@alleninstitute.org"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.0.0"


def get_module_version():
    return __version__


from .airtable_upload_core import AirtableUploader
