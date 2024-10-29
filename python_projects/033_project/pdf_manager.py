import PySimpleGUI as sg
import PyPDF2
import os
from typing import List, Dict, Optional
from pathlib import Path

class PDFManager:
    def __init__(self):
        self.current_pdf = None
        self.pdf_reader = None
        
    def load_pdf(self, filepath: str) -> bool:
        try:
            self.current_pdf = open(filepath, 'rb')
            self.pdf_reader = PyPDF2.PdfReader(self.current_pdf)
            return True
        except Exception as e:
            sg.popup_error(f"Error loading PDF: {str(e)}")
            return False
            
    def merge_pdfs(self, pdf_files: List[str], output_path: str) -> bool:
        try:
            merger = PyPDF2.PdfMerger()
            for pdf in pdf_files:
                merger.append(pdf)
            merger.write(output_path)
            merger.close()
            return True
        except Exception as e:
            sg.popup_error(f"Error merging PDFs: {str(e)}")
            return False
            
    def extract_pages(self, output_path: str, pages: List[int]) -> bool:
        try:
            writer = PyPDF2.PdfWriter()
            for page_num in pages:
                if 0 <= page_num < len(self.pdf_reader.pages):
                    writer.add_page(self.pdf_reader.pages[page_num])
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            return True
        except Exception as e:
            sg.popup_error(f"Error extracting pages: {str(e)}")
            return False
            
    def extract_text(self, page_num: int = None) -> str:
        try:
            if page_num is not None:
                if 0 <= page_num < len(self.pdf_reader.pages):
                    return self.pdf_reader.pages[page_num].extract_text()
                return ""
            
            text = ""
            for page in self.pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            sg.popup_error(f"Error extracting text: {str(e)}")
            return ""

def create_layout():
    return [
        [sg.Text("PDF Manager", font=("Helvetica", 16))],
        [sg.Frame("Load PDF", [
            [sg.Input(key="-PDF-PATH-"), sg.FileBrowse(file_types=(("PDF Files", "*.pdf"),))],
            [sg.Button("Load PDF")]
        ])],
        [sg.Frame("Merge PDFs", [
            [sg.Listbox(values=[], size=(40, 5), key="-PDF-LIST-")],
            [sg.Button("Add PDF"), sg.Button("Remove PDF"), sg.Button("Merge PDFs")]
        ])],
        [sg.Frame("Extract Pages", [
            [sg.Text("Pages (comma-separated):"), sg.Input(key="-PAGES-")],
            [sg.Button("Extract Pages")]
        ])],
        [sg.Frame("Extract Text", [
            [sg.Text("Page Number (optional):"), sg.Input(key="-PAGE-NUM-")],
            [sg.Button("Extract Text")],
            [sg.Multiline(size=(50, 10), key="-TEXT-OUTPUT-", disabled=True)]
        ])],
        [sg.Button("Exit")]
    ]

def main():
    manager = PDFManager()
    window = sg.Window("PDF Manager", create_layout(), resizable=True)
    pdf_files = []
    
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, "Exit"):
            break
            
        if event == "Load PDF":
            if values["-PDF-PATH-"]:
                if manager.load_pdf(values["-PDF-PATH-"]):
                    sg.popup("PDF loaded successfully!")
                    
        if event == "Add PDF":
            filepath = sg.popup_get_file("Select PDF", file_types=(("PDF Files", "*.pdf"),))
            if filepath and filepath not in pdf_files:
                pdf_files.append(filepath)
                window["-PDF-LIST-"].update(values=[Path(f).name for f in pdf_files])
                
        if event == "Remove PDF":
            selected = values["-PDF-LIST-"]
            if selected:
                idx = window["-PDF-LIST-"].GetIndexes()[0]
                pdf_files.pop(idx)
                window["-PDF-LIST-"].update(values=[Path(f).name for f in pdf_files])
                
        if event == "Merge PDFs":
            if len(pdf_files) < 2:
                sg.popup_error("Please add at least 2 PDFs to merge!")
                continue
                
            output_path = sg.popup_get_file("Save Merged PDF", save_as=True, file_types=(("PDF Files", "*.pdf"),))
            if output_path:
                if manager.merge_pdfs(pdf_files, output_path):
                    sg.popup("PDFs merged successfully!")
                    
        if event == "Extract Pages":
            if not manager.pdf_reader:
                sg.popup_error("Please load a PDF first!")
                continue
                
            try:
                pages = [int(p.strip()) - 1 for p in values["-PAGES-"].split(",")]
                output_path = sg.popup_get_file("Save Extracted Pages", save_as=True, file_types=(("PDF Files", "*.pdf"),))
                if output_path:
                    if manager.extract_pages(output_path, pages):
                        sg.popup("Pages extracted successfully!")
            except ValueError:
                sg.popup_error("Please enter valid page numbers!")
                
        if event == "Extract Text":
            if not manager.pdf_reader:
                sg.popup_error("Please load a PDF first!")
                continue
                
            page_num = None
            if values["-PAGE-NUM-"]:
                try:
                    page_num = int(values["-PAGE-NUM-"]) - 1
                except ValueError:
                    sg.popup_error("Please enter a valid page number!")
                    continue
                    
            text = manager.extract_text(page_num)
            window["-TEXT-OUTPUT-"].update(text)
    
    if manager.current_pdf:
        manager.current_pdf.close()
    window.close()

if __name__ == "__main__":
    main() 