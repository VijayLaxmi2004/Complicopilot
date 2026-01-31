import unittest
from backend.services.parser import ParserService

class TestParserService(unittest.TestCase):

    def setUp(self):
        self.parser = ParserService()
        self.sample_gst_invoice_text = """
        Tech Solutions Pvt. Ltd.
        GSTIN: 29AAFCT6192H1ZV
        Invoice No: INV-2025-00123
        Date: 15/09/2025

        Description of Goods   HSN/SAC   Amount
        -------------------------------------------
        Software Development    9983      10000.00
        Consulting Services     9983      5000.00
        -------------------------------------------
        Subtotal: 15000.00
        CGST @ 9%: 1350.00
        SGST @ 9%: 1350.00
        Total: 17700.00
        """

    def test_parse_full_gst_invoice(self):
        """
        Test parsing a typical Indian GST invoice.
        """
        parsed_data = self.parser.parse(self.sample_gst_invoice_text)

        # Validate extracted data
        self.assertEqual(parsed_data.get("vendor"), "Tech Solutions Pvt. Ltd.")
        self.assertEqual(parsed_data.get("gstin"), "29AAFCT6192H1ZV")
        self.assertEqual(parsed_data.get("invoice_number"), "INV-2025-00123")
        self.assertEqual(parsed_data.get("date"), "15/09/2025")
        self.assertEqual(parsed_data.get("total"), "17700.00")
        self.assertEqual(parsed_data.get("cgst"), "1350.00")
        self.assertEqual(parsed_data.get("sgst"), "1350.00")
        self.assertIsNone(parsed_data.get("igst"))
        
        # HSN code extraction can be noisy, so we check if the expected code is present
        self.assertIn("9983", parsed_data.get("hsn_codes", []))

    def test_gstin_checksum_validation(self):
        """
        Test the GSTIN checksum validation logic with valid and invalid numbers.
        """
        # Valid GSTIN
        self.assertTrue(self.parser._is_valid_gstin("29AAFCT6192H1ZV"))
        # Invalid GSTIN (wrong checksum)
        self.assertFalse(self.parser._is_valid_gstin("29AAFCT6192H1Z5"))
        # Invalid format
        self.assertFalse(self.parser._is_valid_gstin("INVALIDGSTIN"))

if __name__ == '__main__':
    unittest.main()
