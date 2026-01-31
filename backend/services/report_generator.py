import os
import google.generativeai as genai
from fpdf import FPDF
import json
import logging

logger = logging.getLogger(__name__)

class ReportGeneratorService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set it as an environment variable 'GEMINI_API_KEY'.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_json_from_text(self, text: str) -> dict:
        """
        Uses the Gemini API to extract structured data from raw receipt text.
        """
        prompt = f"""
        Analyze the following receipt text and extract the following information in JSON format:
        - "merchant_name": The name of the merchant.
        - "transaction_date": The date of the transaction (in YYYY-MM-DD format).
        - "items": a list of objects, each with "description", "quantity", and "price".
        - "total_amount": The total amount of the transaction.

        Here is the receipt text:
        ---
        {text}
        ---

        Please provide the output in a single JSON object.
        """
        try:
            response = self.model.generate_content(prompt)
            # The response from Gemini can sometimes include markdown formatting.
            # We need to clean it up to get a valid JSON string.
            json_string = response.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(json_string)
        except Exception as e:
            logger.error(f"Failed to generate JSON from text: {e}")
            return {}

    def create_pdf_report(self, data: dict) -> bytes:
        """
        Generates a PDF report from the structured data.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Receipt Report", ln=True, align='C')

        pdf.cell(200, 10, txt=f"Merchant: {data.get('merchant_name', 'N/A')}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {data.get('transaction_date', 'N/A')}", ln=True)
        pdf.cell(200, 10, txt="", ln=True) # Spacer

        pdf.set_font("Arial", 'B', 10)
        pdf.cell(100, 10, "Description", 1)
        pdf.cell(40, 10, "Quantity", 1)
        pdf.cell(40, 10, "Price", 1, ln=True)
        pdf.set_font("Arial", size=10)

        items = data.get("items", [])
        for item in items:
            pdf.cell(100, 10, str(item.get("description", "")), 1)
            pdf.cell(40, 10, str(item.get("quantity", "")), 1)
            pdf.cell(40, 10, str(item.get("price", "")), 1, ln=True)

        pdf.cell(200, 10, txt="", ln=True) # Spacer

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(140, 10, "Total", 1)
        pdf.cell(40, 10, str(data.get("total_amount", "N/A")), 1, ln=True)

        return pdf.output(dest='S').encode('latin-1')

report_generator_service = ReportGeneratorService()
