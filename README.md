# DoTerra HK Price Scraper

This tool automates the extraction of product pricing and categorization from the official doTERRA Hong Kong price list.

## Source Data
The scraper targets the following PDF:
https://media.doterra.com/hk-otg/zh/brochures/hkotg-price-list.pdf

## File Descriptions
* oil_scraper.py: The Python source code used to download the PDF, parse the text, and compare price changes. → requires 'pip install pdfplumber'
* DoTerra_Pricing_Tool.exe: A standalone Windows executable of the scraper can be made locally ("pause" already added):
   1. 'pip install pyinstaller'
   2. 'python -m PyInstaller --onefile --clean --name "DoTerra_Update_Tool" scrape_oils_final.py'
   3. large .exe file cannot be pushed to git.
* doterra_products.json: The extracted data in JSON format, current as of 2026-01-01.

## Features
* Price Recovery: Logic to reattach truncated digits from PDF text layers to ensure price accuracy.
* Bilingual Support: Separates English and Chinese names for products, units, and categories.
* Change Tracking: Compares the new scan against existing JSON data to report new items, removed items, and average price percentage shifts.
* Auto-Categorization: Detects section headers in the PDF to assign products to categories like Single Oils or Proprietary Blends.

## Usage
Run the .exe file in the same directory as the .json file. The program will output a summary of changes to the console and update the .json file automatically.
