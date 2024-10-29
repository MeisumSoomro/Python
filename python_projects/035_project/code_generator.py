import PySimpleGUI as sg
from typing import Dict, List, Optional
import os
import json
from datetime import datetime

class CodeGenerator:
    def __init__(self):
        self.templates_dir = "templates"
        self.templates = self.load_templates()
        
    def load_templates(self) -> Dict:
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            self.create_default_templates()
        
        templates = {}
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.templates_dir, filename)) as f:
                    templates[filename[:-5]] = json.load(f)
        return templates
    
    def create_default_templates(self):
        default_templates = {
            'python_class': {
                'template': '''class {class_name}:
    def __init__(self{params}):
        {init_body}
    
    {methods}''',
                'params': {
                    'class_name': 'str',
                    'params': 'str',
                    'init_body': 'str',
                    'methods': 'str'
                }
            },
            'python_script': {
                'template': '''#!/usr/bin/env python3
"""
{description}
Created on: {date}
Author: {author}
"""

{imports}

def main():
    {main_code}

if __name__ == "__main__":
    main()''',
                'params': {
                    'description': 'str',
                    'date': 'str',
                    'author': 'str',
                    'imports': 'str',
                    'main_code': 'str'
                }
            },
            'html_template': {
                'template': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {css}
    </style>
</head>
<body>
    {body}
    <script>
        {javascript}
    </script>
</body>
</html>''',
                'params': {
                    'title': 'str',
                    'css': 'str',
                    'body': 'str',
                    'javascript': 'str'
                }
            }
        }
        
        for name, template in default_templates.items():
            with open(os.path.join(self.templates_dir, f"{name}.json"), 'w') as f:
                json.dump(template, f, indent=4)
    
    def generate_code(self, template_name: str, params: Dict) -> str:
        if template_name not in self.templates:
            return "Template not found"
        
        template = self.templates[template_name]['template']
        try:
            return template.format(**params)
        except Exception as e:
            return f"Error generating code: {str(e)}"
    
    def save_template(self, name: str, template: str, params: Dict) -> bool:
        try:
            template_data = {
                'template': template,
                'params': params
            }
            with open(os.path.join(self.templates_dir, f"{name}.json"), 'w') as f:
                json.dump(template_data, f, indent=4)
            self.templates[name] = template_data
            return True
        except Exception as e:
            sg.popup_error(f"Error saving template: {str(e)}")
            return False

def create_layout():
    return [
        [sg.Text("Code Generator", font=("Helvetica", 16))],
        [sg.Frame("Template", [
            [
                sg.Text("Select Template:"),
                sg.Combo([], key="-TEMPLATE-", enable_events=True)
            ],
            [sg.Button("New Template"), sg.Button("Edit Template")]
        ])],
        [sg.Frame("Parameters", [
            [sg.Column([], key="-PARAMS-COL-", scrollable=True, size=(400, 200))]
        ])],
        [sg.Frame("Generated Code", [
            [sg.Multiline(size=(50, 10), key="-CODE-", disabled=True)]
        ])],
        [sg.Button("Generate"), sg.Button("Copy"), sg.Button("Save"), sg.Button("Exit")]
    ]

def main():
    generator = CodeGenerator()
    window = sg.Window("Code Generator", create_layout(), resizable=True)
    window["-TEMPLATE-"].update(values=list(generator.templates.keys()))
    
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, "Exit"):
            break
            
        if event == "-TEMPLATE-":
            if values["-TEMPLATE-"]:
                template = generator.templates[values["-TEMPLATE-"]]
                layout = []
                for param, param_type in template['params'].items():
                    layout.append([
                        sg.Text(f"{param}:"),
                        sg.Input(key=f"-PARAM-{param}-")
                    ])
                window["-PARAMS-COL-"].update(layout)
                
        if event == "Generate":
            if not values["-TEMPLATE-"]:
                sg.popup_error("Please select a template!")
                continue
                
            template = generator.templates[values["-TEMPLATE-"]]
            params = {}
            for param in template['params']:
                params[param] = values[f"-PARAM-{param}-"]
                
            code = generator.generate_code(values["-TEMPLATE-"], params)
            window["-CODE-"].update(code)
            
        if event == "Copy":
            code = values["-CODE-"]
            if code:
                sg.clipboard_set(code)
                sg.popup("Code copied to clipboard!")
                
        if event == "Save":
            code = values["-CODE-"]
            if code:
                filename = sg.popup_get_file("Save Code", save_as=True)
                if filename:
                    with open(filename, 'w') as f:
                        f.write(code)
                    sg.popup(f"Code saved to {filename}")
                    
        if event == "New Template":
            layout = [
                [sg.Text("Template Name:"), sg.Input(key="-TEMP-NAME-")],
                [sg.Text("Template:")],
                [sg.Multiline(size=(50, 10), key="-TEMP-CODE-")],
                [sg.Text("Parameters (one per line, format: name:type):")],
                [sg.Multiline(size=(50, 5), key="-TEMP-PARAMS-")],
                [sg.Button("Save Template"), sg.Button("Cancel")]
            ]
            
            temp_window = sg.Window("New Template", layout)
            while True:
                temp_event, temp_values = temp_window.read()
                
                if temp_event in (sg.WIN_CLOSED, "Cancel"):
                    break
                    
                if temp_event == "Save Template":
                    name = temp_values["-TEMP-NAME-"]
                    template = temp_values["-TEMP-CODE-"]
                    params = {}
                    
                    for line in temp_values["-TEMP-PARAMS-"].split('\n'):
                        if ':' in line:
                            param_name, param_type = line.strip().split(':')
                            params[param_name] = param_type
                            
                    if name and template and params:
                        if generator.save_template(name, template, params):
                            sg.popup("Template saved successfully!")
                            window["-TEMPLATE-"].update(values=list(generator.templates.keys()))
                            break
                            
            temp_window.close()
    
    window.close()

if __name__ == "__main__":
    main() 