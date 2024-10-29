import PySimpleGUI as sg
import os
from typing import Optional, Dict
import re

class TextEditor:
    def __init__(self):
        self.current_file: Optional[str] = None
        self.syntax_patterns: Dict[str, list] = {
            '.py': [
                (r'\b(def|class|if|else|elif|for|while|try|except|import|from|return|break|continue)\b', '#FF8C00'),  # Keywords
                (r'#.*', '#228B22'),  # Comments
                (r'["\'](.*?)["\']', '#4169E1'),  # Strings
                (r'\b\d+\b', '#9370DB')  # Numbers
            ],
            '.txt': []  # No syntax highlighting for txt files
        }
    
    def load_file(self, filepath: str) -> str:
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                self.current_file = filepath
                return file.read()
        except Exception as e:
            sg.popup_error(f'Error loading file: {str(e)}')
            return ''

    def save_file(self, filepath: str, content: str) -> bool:
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            self.current_file = filepath
            return True
        except Exception as e:
            sg.popup_error(f'Error saving file: {str(e)}')
            return False

    def apply_syntax_highlighting(self, text: str) -> str:
        if not self.current_file:
            return text
            
        file_ext = os.path.splitext(self.current_file)[1]
        if file_ext not in self.syntax_patterns:
            return text

        highlighted_text = text
        for pattern, color in self.syntax_patterns[file_ext]:
            highlighted_text = re.sub(
                pattern,
                lambda m: f'#{color}#{m.group()}#default#',
                highlighted_text
            )
        return highlighted_text

def create_layout():
    menu_def = [
        ['File', ['New', 'Open', 'Save', 'Save As', '---', 'Exit']],
        ['Edit', ['Undo', 'Redo', '---', 'Cut', 'Copy', 'Paste', '---', 'Find', 'Replace']],
        ['View', ['Word Wrap', 'Line Numbers', 'Syntax Highlighting']]
    ]

    return [
        [sg.Menu(menu_def)],
        [sg.Multiline(
            size=(80, 25),
            key='-EDITOR-',
            font=('Courier New', 11),
            right_click_menu=['&Right', ['Cut', 'Copy', 'Paste', '---', 'Find', 'Replace']],
            expand_x=True,
            expand_y=True
        )],
        [
            sg.StatusBar(
                'Ready',
                key='-STATUS-',
                size=(55, 1),
                expand_x=True
            ),
            sg.StatusBar(
                'Ln 1, Col 1',
                key='-POSITION-',
                size=(15, 1)
            )
        ]
    ]

def main():
    editor = TextEditor()
    window = sg.Window(
        'Text Editor',
        create_layout(),
        resizable=True,
        return_keyboard_events=True,
        finalize=True
    )
    
    window['-EDITOR-'].expand(expand_x=True, expand_y=True)
    
    # Track changes for unsaved work
    content_changed = False
    last_content = ''

    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, 'Exit'):
            if content_changed:
                if sg.popup_yes_no('Save changes before closing?') == 'Yes':
                    if editor.current_file:
                        editor.save_file(editor.current_file, values['-EDITOR-'])
                    else:
                        filepath = sg.popup_get_file('Save As', save_as=True, file_types=(("Text Files", "*.txt"), ("Python Files", "*.py")))
                        if filepath:
                            editor.save_file(filepath, values['-EDITOR-'])
            break

        if event == 'New':
            if content_changed:
                if sg.popup_yes_no('Save changes?') == 'Yes':
                    if editor.current_file:
                        editor.save_file(editor.current_file, values['-EDITOR-'])
            window['-EDITOR-'].update('')
            editor.current_file = None
            content_changed = False

        if event == 'Open':
            filepath = sg.popup_get_file('Open File', file_types=(("Text Files", "*.txt"), ("Python Files", "*.py")))
            if filepath:
                content = editor.load_file(filepath)
                window['-EDITOR-'].update(content)
                last_content = content
                content_changed = False

        if event == 'Save':
            if editor.current_file:
                if editor.save_file(editor.current_file, values['-EDITOR-']):
                    content_changed = False
                    last_content = values['-EDITOR-']
            else:
                event = 'Save As'  # Redirect to Save As if no file is open

        if event == 'Save As':
            filepath = sg.popup_get_file('Save As', save_as=True, file_types=(("Text Files", "*.txt"), ("Python Files", "*.py")))
            if filepath:
                if editor.save_file(filepath, values['-EDITOR-']):
                    content_changed = False
                    last_content = values['-EDITOR-']

        # Check for content changes
        if values['-EDITOR-'] != last_content:
            content_changed = True
            window['-STATUS-'].update('Modified' if content_changed else 'Ready')

        # Update cursor position
        if event.endswith('_UP') or event.endswith('_DOWN'):
            text = values['-EDITOR-']
            cursor_pos = window['-EDITOR-'].Widget.index('insert')
            line, col = cursor_pos.split('.')
            window['-POSITION-'].update(f'Ln {line}, Col {int(col)+1}')

    window.close()

if __name__ == "__main__":
    main() 