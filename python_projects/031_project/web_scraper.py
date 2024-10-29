import PySimpleGUI as sg
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Optional, Tuple
import re
from urllib.parse import urljoin
import os
from datetime import datetime

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.current_url: Optional[str] = None
        self.soup: Optional[BeautifulSoup] = None
        self.scraped_data: List[Dict] = []
    
    def fetch_page(self, url: str) -> bool:
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, 'html.parser')
            self.current_url = url
            return True
        except Exception as e:
            sg.popup_error(f"Error fetching page: {str(e)}")
            return False
    
    def extract_elements(self, tag: str, class_name: Optional[str] = None) -> List[Dict]:
        if not self.soup:
            return []
        
        elements = self.soup.find_all(tag, class_=class_name)
        extracted_data = []
        
        for element in elements:
            data = {
                'tag': tag,
                'text': element.get_text(strip=True),
                'html': str(element)
            }
            
            # Extract attributes
            if element.attrs:
                data['attributes'] = element.attrs
            
            # Extract links
            if tag == 'a':
                href = element.get('href')
                if href:
                    data['link'] = urljoin(self.current_url, href)
            
            # Extract images
            if tag == 'img':
                src = element.get('src')
                if src:
                    data['image_url'] = urljoin(self.current_url, src)
            
            extracted_data.append(data)
        
        self.scraped_data.extend(extracted_data)
        return extracted_data
    
    def save_to_csv(self, filepath: str) -> bool:
        try:
            df = pd.DataFrame(self.scraped_data)
            df.to_csv(filepath, index=False)
            return True
        except Exception as e:
            sg.popup_error(f"Error saving data: {str(e)}")
            return False
    
    def clear_data(self):
        self.scraped_data = []

def create_layout():
    return [
        [sg.Text("Web Scraper", font=("Helvetica", 16))],
        [
            sg.Text("URL:"),
            sg.Input(key="-URL-", size=(40, 1)),
            sg.Button("Fetch")
        ],
        [sg.Frame("Scraping Options", [
            [
                sg.Text("HTML Tag:"),
                sg.Input(key="-TAG-", size=(10, 1)),
                sg.Text("Class (optional):"),
                sg.Input(key="-CLASS-", size=(15, 1))
            ],
            [sg.Button("Extract Elements")]
        ])],
        [sg.Frame("Results", [
            [sg.Table(
                values=[],
                headings=["Tag", "Text", "Attributes"],
                auto_size_columns=True,
                num_rows=10,
                key="-TABLE-"
            )]
        ])],
        [
            sg.Button("Save to CSV"),
            sg.Button("Clear"),
            sg.Button("Exit")
        ]
    ]

def main():
    scraper = WebScraper()
    window = sg.Window("Web Scraper", create_layout(), resizable=True)
    
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, "Exit"):
            break
        
        if event == "Fetch":
            url = values["-URL-"]
            if url:
                if scraper.fetch_page(url):
                    sg.popup("Page fetched successfully!")
                    scraper.clear_data()
                    window["-TABLE-"].update([])
        
        if event == "Extract Elements":
            if not scraper.soup:
                sg.popup_error("Please fetch a page first!")
                continue
            
            tag = values["-TAG-"]
            class_name = values["-CLASS-"] if values["-CLASS-"] else None
            
            if tag:
                elements = scraper.extract_elements(tag, class_name)
                table_data = [
                    [
                        elem['tag'],
                        elem['text'][:50] + "..." if len(elem['text']) > 50 else elem['text'],
                        str(elem.get('attributes', ''))[:50] + "..."
                            if len(str(elem.get('attributes', ''))) > 50 else str(elem.get('attributes', ''))
                    ]
                    for elem in elements
                ]
                window["-TABLE-"].update(table_data)
                sg.popup(f"Extracted {len(elements)} elements!")
        
        if event == "Save to CSV":
            if not scraper.scraped_data:
                sg.popup_error("No data to save!")
                continue
            
            filename = f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            if scraper.save_to_csv(filename):
                sg.popup(f"Data saved to {filename}")
        
        if event == "Clear":
            scraper.clear_data()
            window["-TABLE-"].update([])
    
    window.close()

if __name__ == "__main__":
    main() 