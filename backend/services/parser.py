import re
from typing import Optional, Dict

class ParserService:
    """
    A service to parse structured data (Total Amount, Date, Vendor) from OCR text.
    """

    def extract_total(self, ocr_text: str) -> Optional[str]:
        """
        Extract the total amount from the OCR text using regular expressions.
        Supports INR (₹), numbers with commas, and variations in label.
        """
        total_patterns = [
            r"(?i)(total|grand total|amount due|amount)\s*[:\-]?\s*[₹$]?([0-9]{1,3}(?:,[0-9]{3})*(?:\.\d{2})?)",  # e.g. Total: ₹1,500.00
            r"(?i)(total|grand total|amount due|amount)\s*[:\-]?\s*[₹$]?([0-9]+(?:\.\d{2})?)",  # e.g. Grand Total 1500
        ]
        for pattern in total_patterns:
            match = re.search(pattern, ocr_text)
            if match:
                return match.group(2)
        return None

    def extract_date(self, ocr_text: str) -> Optional[str]:
        """
        Extract the date from the OCR text using regular expressions.
        """
        date_patterns = [
            r"\b(\d{2}[/-]\d{2}[/-]\d{4})\b",  # Matches 'DD-MM-YYYY' or 'DD/MM/YYYY'
            r"\b(\d{2}[/-]\d{2}[/-]\d{2})\b",  # Matches 'DD-MM-YY' or 'DD/MM/YY'
            r"\b(\d{2}\s+[A-Za-z]{3}\s+\d{4})\b",  # Matches 'DD Mon YYYY'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, ocr_text)
            if match:
                return match.group(1)
        return None

    def extract_vendor(self, ocr_text: str) -> Optional[str]:
        """
        Extract the vendor name from the OCR text.
        Assume the vendor is the first non-empty line of text.
        """
        lines = ocr_text.splitlines()
        for line in lines:
            line = line.strip()
            if line:  # Return the first non-empty line
                return line
        return None

    def parse(self, ocr_text: str) -> Dict[str, Optional[str]]:
        """
        Parse the OCR text to extract structured data.
        """
        return {
            "total": self.extract_total(ocr_text),
            "date": self.extract_date(ocr_text),
            "vendor": self.extract_vendor(ocr_text),
        }

# Example usage
if __name__ == "__main__":
    parser = ParserService()
    sample_text = """
    SuperMart Grocery
    123 Main Street, Springfield, USA
    Date: 08/31/2025
    Time: 12:45 PM
    Receipt #: 1234567890

    Qty   Description         Unit Price   Total
    1     Milk                $2.50        $2.50
    2     Bread               $1.50        $3.00
    1     Eggs                $3.00        $3.00

    Subtotal: $8.50
    Tax (5%): $0.43
    Total: $7.93
    """
    parsed_data = parser.parse(sample_text)
    print(parsed_data)
