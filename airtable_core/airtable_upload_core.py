import os

from construct import (
    get_dashboard_data,
    get_experimental_data,
    get_linearity_data,
    get_metadata,
    get_raw_data,
)
from dotenv import load_dotenv
from upload import add_all_to_airtable


class AirtableUploader:
    def __init__(
        self,
        file_path: str,
    ):
        self.file_path = file_path
        self.metadata = get_metadata(file_path)
        self.raw_data = get_raw_data(self.file_path)
        self.linearity_data = get_linearity_data(self.metadata, self.raw_data)
        self.experimental_data = get_experimental_data(self.metadata, self.raw_data)
        self.dashboard_data = get_dashboard_data(
            self.linearity_data, self.experimental_data
        )

    def upload(self):
        load_dotenv()
        AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
        AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
        AIRTABLE_LINEARITY = os.environ.get("ARITABLE_LINEARITY")
        AIRTABLE_EXPIRIMENTAL = os.environ.get("AIRTABLE_EXPIRIMENTAL")
        AIRTABLE_DASHBOARD = os.environ.get("AIRTABLE_DASHBOARD")

        add_all_to_airtable(
            f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_EXPIRIMENTAL}",
            AIRTABLE_API_KEY,
            self.experimental_data,
        )
        add_all_to_airtable(
            f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_LINEARITY}",
            AIRTABLE_API_KEY,
            self.linearity_data,
        )
        add_all_to_airtable(
            f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_DASHBOARD}",
            AIRTABLE_API_KEY,
            self.dashboard_data,
        )
