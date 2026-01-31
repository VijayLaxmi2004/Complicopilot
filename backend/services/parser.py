import re
from typing import Optional, Dict, List

class ParserService:
    """
    A service to parse structured data (Total Amount, Date, Vendor) from OCR text.
    """

    def extract_total(self, ocr_text: str) -> Optional[str]:
        """
        Extract the total amount from the OCR text using a prioritized strategy.
        """
        candidates = []
        
        # Priority 1: Find amounts on lines with a 'total' keyword.
        total_keywords = ['total', 'grand total', 'amount due', 'net amount', 'final amount']
        for line in ocr_text.splitlines():
            if any(keyword in line.lower() for keyword in total_keywords):
                matches = re.findall(r'([0-9,]+\.\d{2})', line)
                for amount in matches:
                    try:
                        float_amount = float(amount.replace(',', ''))
                        if 1 <= float_amount <= 100000:
                            candidates.append(float_amount)
                    except ValueError:
                        continue
        
        if candidates:
            # Return the largest valid amount from the 'total' lines.
            return f"{max(candidates):.2f}"

        # Priority 2 (Fallback): Find the largest amount anywhere on the receipt.
        all_amounts = []
        matches = re.findall(r'([0-9,]+\.\d{2})', ocr_text)
        for amount in matches:
            try:
                float_amount = float(amount.replace(',', ''))
                if 1 <= float_amount <= 100000:
                    all_amounts.append(float_amount)
            except ValueError:
                continue
        
        if all_amounts:
            # Return the overall largest valid amount.
            return f"{max(all_amounts):.2f}"
            
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

    def _is_valid_gstin(self, gstin: str) -> bool:
        """
        Validate a GSTIN using the checksum algorithm.
        """
        if len(gstin) != 15:
            return False

        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        char_map = {char: i for i, char in enumerate(chars)}
        
        try:
            input_digits = [char_map[char] for char in gstin[:-1]]
        except KeyError:
            return False # Invalid character in GSTIN

        total = 0
        for i, digit in enumerate(input_digits):
            multiplier = (i % 2) + 1
            product = digit * multiplier
            quotient = product // 36
            remainder = product % 36
            total += quotient + remainder

        final_remainder = total % 36
        checksum_code = (36 - final_remainder) % 36
        calculated_checksum_char = chars[checksum_code]

        return gstin[14] == calculated_checksum_char

    def extract_gstin(self, ocr_text: str) -> Optional[str]:
        """
        Extract and validate the GSTIN from the OCR text.
        """
        gstin_pattern = r'\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})\b'
        labeled_pattern = r'(?i)(?:GSTIN|GST\s*No|GST\s*Number)\s*[:\-]?\s*' + gstin_pattern
        
        for pattern in [labeled_pattern, gstin_pattern]:
            matches = re.findall(pattern, ocr_text)
            for match in matches:
                gstin = match if isinstance(match, str) else match[-1]
                gstin_clean = re.sub(r'[\s-]', '', gstin).upper()
                
                if self._is_valid_gstin(gstin_clean):
                    return gstin_clean
        return None

    def extract_tax_breakdown(self, ocr_text: str) -> Dict[str, Optional[str]]:
        """
        Extract CGST, SGST, and IGST amounts from the OCR text.
        """
        # Pattern to find tax type (CGST, SGST, IGST) and its corresponding amount.
        # It looks for the tax label, followed by an optional percentage,
        # and then captures the numeric amount.
        tax_pattern = r"(?i)(CGST|SGST|IGST)\s*(?:@\s*[\d.]+%?)?\s*[:\-]?\s*[₹$]?\s*([0-9,]+\.\d{2})"
        
        matches = re.findall(tax_pattern, ocr_text)
        
        tax_data = {
            "cgst": None,
            "sgst": None,
            "igst": None,
        }

        for tax_type, amount in matches:
            tax_key = tax_type.lower()
            if tax_key in tax_data:
                # Store the first valid amount found for each tax type
                if tax_data[tax_key] is None:
                    tax_data[tax_key] = amount.replace(',', '')
        
        return tax_data

    def extract_invoice_number(self, ocr_text: str) -> Optional[str]:
        """
        Extract the invoice number from the OCR text.
        """
        # Patterns to look for invoice number, bill number, etc.
        # It captures an alphanumeric string that follows the label.
        invoice_patterns = [
            r"(?i)(?:Invoice\s*No|Inv\s*No|Bill\s*No|Receipt\s*#)\s*[:\-]?\s*([A-Za-z0-9/-]+)",
        ]

        for pattern in invoice_patterns:
            match = re.search(pattern, ocr_text)
            if match:
                invoice_number = match.group(1).strip()
                if 2 <= len(invoice_number) <= 30:
                    return invoice_number
        return None

    def extract_hsn_codes(self, ocr_text: str) -> List[str]:
        """
        Extract HSN/SAC codes from the OCR text.
        HSN/SAC codes are typically 4, 6, or 8 digits.
        """
        # This pattern looks for 4, 6, or 8 digit numbers that are likely HSN/SAC codes.
        # It is a simple regex and may need refinement for complex layouts.
        hsn_pattern = r"\b(\d{4}|\d{6}|\d{8})\b"
        
        # Using a set to avoid duplicate codes
        found_codes = set()
        
        # Find all potential codes in the text
        matches = re.findall(hsn_pattern, ocr_text)
        
        # Simple validation: avoid numbers that are clearly something else (e.g., years)
        for code in matches:
            if not (code.startswith('19') or code.startswith('20')):
                found_codes.add(code)
                
        return list(found_codes)

    def parse(self, ocr_text: str) -> Dict[str, any]:
        """
        Parse the OCR text to extract structured data.
        """
        parsed_data = {
            "total": self.extract_total(ocr_text),
            "date": self.extract_date(ocr_text),
            "vendor": self.extract_vendor(ocr_text),
            "gstin": self.extract_gstin(ocr_text),
            "invoice_number": self.extract_invoice_number(ocr_text),
            "hsn_codes": self.extract_hsn_codes(ocr_text),
        }
        tax_data = self.extract_tax_breakdown(ocr_text)
        parsed_data.update(tax_data)
        return parsed_data

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
