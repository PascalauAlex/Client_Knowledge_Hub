import time

from llama_cloud import LlamaCloud
from pathlib import Path
from pydantic import BaseModel, Field
from datetime import datetime
from dotenv import load_dotenv
import os

from config import settings


def _get_client() -> LlamaCloud:
    _client = LlamaCloud(api_key=settings.llama_api_key)
    return _client



class InvoiceData(BaseModel):
    vendor : str = Field(description="Vendor name")
    invoice_date : datetime
    due_date : datetime
    invoice_number : str
    total_due : str
    items : list[str] = Field(description="Items of the current invoice, as a list")


def structured_invoice_summary(file_name : str,document : bytes):
    client = _get_client()
    file_obj = client.files.create(file=(file_name,document),purpose="extract")

    invoice = client.extract.create(
        file_input=file_obj.id,
        configuration={
            "data_schema": InvoiceData.model_json_schema(),
            "extraction_target": "per_doc",
            "tier": "agentic",
        },
    )
    while invoice.status not in ("COMPLETED", "FAILED", "CANCELLED"):
        print(f"EXTRACT STAGE: {invoice.status}...")
        time.sleep(2)
        invoice = client.extract.get(invoice.id)
    print(f"\n--- Final state LLAMA: {invoice.status} ---")
    if invoice.status != "COMPLETED":
        print(f"ERROR : {invoice}")
    return invoice.extract_result


