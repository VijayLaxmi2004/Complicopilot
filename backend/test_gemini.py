import os
from backend.services.report_generator import ReportGeneratorService

def test_gemini_api_key():
    """
    Tests if the Gemini API key is correctly set up in the environment.
    """
    print("Checking for Gemini API key...")
    try:
        # Attempt to initialize the service
        service = ReportGeneratorService()
        print("\n✅ Success! Gemini API key is configured correctly.")
        print("The application should be able to connect to the Gemini API.")

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease follow these steps to set up your Gemini API key:")
        print("1. Get your API key from Google AI Studio.")
        print("2. Set it as an environment variable named 'GEMINI_API_KEY'.")
        # Instructions for Windows
        if os.name == 'nt':
            print("\n   To set it temporarily (for the current command prompt session), run:")
            print("   AIzaSyDO4U0TArpZcUXi3V56lHdKuj9gucoo7KA")
            print("\n   To set it permanently, you can use the System Properties dialog:")
            print("   - Search for 'Edit the system environment variables' in the Start Menu.")
            print("   - Click the 'Environment Variables...' button.")
            print("   - In the 'User variables' section, click 'New...' and enter:")
            print("     - Variable name: GEMINI_API_KEY")
            print("     - Variable value: YOUR_API_KEY_HERE")
            print("   - Click OK and restart your command prompt or IDE for the change to take effect.")
        else: # Instructions for macOS/Linux
            print("\n   To set it temporarily (for the current terminal session), run:")
            print("   export GEMINI_API_KEY='YOUR_API_KEY_HERE'")
            print("\n   To set it permanently, add the export line to your shell's startup file (e.g., ~/.bashrc, ~/.zshrc) and restart your terminal.")

if __name__ == "__main__":
    test_gemini_api_key()
