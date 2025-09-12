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
        # More comprehensive patterns for amounts
        total_patterns = [
            r"(?i)(total|grand total|amount due|amount|net amount|final amount)\s*[:\-]?\s*[₹$]?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.\d{2})?)",
            r"(?i)(total|grand total|amount due|amount|net amount|final amount)\s*[:\-]?\s*[₹$]?\s*([0-9]+(?:\.\d{2})?)",
            r"[₹$]\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.\d{2})?)",  # Just currency symbol followed by number
            r"([0-9]{1,3}(?:,[0-9]{3})*(?:\.\d{2})?)\s*[₹$]",  # Number followed by currency
            r"([0-9]+\.\d{2})",  # Any decimal number (as fallback)
        ]
        
        for pattern in total_patterns:
            matches = re.findall(pattern, ocr_text)
            for match in matches:
                amount = match[-1] if isinstance(match, tuple) else match
                # Validate amount is reasonable (between 1 and 100000)
                try:
                    float_amount = float(amount.replace(',', ''))
                    if 1 <= float_amount <= 100000:
                        return amount
                except ValueError:
                    continue
        return None

    def extract_date(self, ocr_text: str) -> Optional[str]:
        """
        Extract the date from the OCR text using regular expressions.
        """
        date_patterns = [
            r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b",  # DD-MM-YYYY or DD/MM/YYYY
            r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2})\b",  # DD-MM-YY or DD/MM/YY
            r"\b(\d{2}\s+[A-Za-z]{3}\s+\d{4})\b",  # DD Mon YYYY
            r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",  # YYYY-MM-DD or YYYY/MM/DD
            r"(?i)(date|dated)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",  # "Date: DD/MM/YYYY"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, ocr_text)
            if match:
                # Get the date part - handle both single group and tuple matches
                date_str = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
                # Basic validation - check if it looks like a reasonable date
                if len(date_str) >= 6:  # At least DDMMYY format
                    return date_str
        return None

    def extract_vendor(self, ocr_text: str) -> Optional[str]:
        """
        Extract the vendor name from the OCR text.
        Try to find the most likely vendor name using multiple strategies.
        """
        lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
        
        if not lines:
            return None
        
        # Strategy 1: Look for lines that look like business names
        for line in lines[:5]:  # Check first 5 lines
            # Skip lines that are clearly not vendor names
            if any(keyword in line.lower() for keyword in ['receipt', 'bill', 'invoice', 'date', 'time', 'total', 'amount']):
                continue
            
            # Skip lines with mostly numbers or symbols
            if len(re.sub(r'[^a-zA-Z\s]', '', line)) < len(line) * 0.5:
                continue
            
            # Skip very short lines (less than 3 characters)
            if len(line) < 3:
                continue
            
            # If line contains common business words, it's likely the vendor
            business_indicators = ['restaurant', 'cafe', 'coffee', 'shop', 'store', 'market', 'mart', 'ltd', 'inc', 'pvt']
            if any(indicator in line.lower() for indicator in business_indicators):
                return line
            
            # If it's a reasonable length and mostly alphabetic, use it
            if 3 <= len(line) <= 50 and re.search(r'[a-zA-Z]{3,}', line):
                return line
        
        # Strategy 2: If no good candidate found, use the first non-empty line
        for line in lines:
            if len(line) >= 3 and not line.isdigit():
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
