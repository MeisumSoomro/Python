import PySimpleGUI as sg
import sqlite3
from typing import List, Dict, Optional, Tuple
import json
import os
from datetime import datetime

class DatabaseGUI:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.current_table = None
        self.connect()
        
    def connect(self) -> bool:
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            sg.popup_error(f"Error connecting to database: {str(e)}")
            return False
            
    def get_tables(self) -> List[str]:
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [table[0] for table in self.cursor.fetchall()]
        except:
            return []
            
    def get_table_schema(self, table_name: str) -> List[Tuple]:
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            return self.cursor.fetchall()
        except:
            return []
            
    def execute_query(self, query: str) -> Tuple[bool, Optional[List], str]:
        try:
            self.cursor.execute(query)
            if query.strip().upper().startswith("SELECT"):
                results = self.cursor.fetchall()
                return True, results, "Query executed successfully"
            else:
                self.conn.commit()
                return True, None, "Query executed successfully"
        except Exception as e:
            return False, None, str(e)
            
    def get_table_data(self, table_name: str, limit: int = 1000) -> List[List]:
        try:
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            return self.cursor.fetchall()
        except:
            return []
            
    def create_table(self, table_name: str, columns: List[Dict]) -> bool:
        try:
            cols = [f"{col['name']} {col['type']}" for col in columns]
            query = f"CREATE TABLE {table_name} ({', '.join(cols)})"
            self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            sg.popup_error(f"Error creating table: {str(e)}")
            return False
            
    def insert_data(self, table_name: str, data: Dict) -> bool:
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, list(data.values()))
            self.conn.commit()
            return True
        except Exception as e:
            sg.popup_error(f"Error inserting data: {str(e)}")
            return False

def create_layout():
    return [
        [sg.Text("Database GUI", font=("Helvetica", 16))],
        [sg.Frame("Database Connection", [
            [sg.Input(key="-DB-PATH-"), sg.FileBrowse(file_types=(("SQLite DB", "*.db"),))],
            [sg.Button("Connect"), sg.Button("Create New DB")]
        ])],
        [sg.Frame("Tables", [
            [sg.Listbox(values=[], size=(30, 5), key="-TABLES-", enable_events=True)],
            [sg.Button("Create Table"), sg.Button("Drop Table"), sg.Button("View Data")]
        ])],
        [sg.Frame("Query", [
            [sg.Multiline(size=(50, 5), key="-QUERY-")],
            [sg.Button("Execute Query")]
        ])],
        [sg.Frame("Results", [
            [sg.Table(
                values=[],
                headings=[],
                auto_size_columns=True,
                num_rows=10,
                key="-RESULTS-"
            )]
        ])],
        [sg.Button("Export Results"), sg.Button("Exit")]
    ]

def main():
    window = sg.Window("Database GUI", create_layout(), resizable=True)
    db_gui = None
    
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, "Exit"):
            break
            
        if event == "Connect":
            if values["-DB-PATH-"]:
                db_gui = DatabaseGUI(values["-DB-PATH-"])
                tables = db_gui.get_tables()
                window["-TABLES-"].update(values=tables)
                
        if event == "Create New DB":
            path = sg.popup_get_file("Create Database", save_as=True, file_types=(("SQLite DB", "*.db"),))
            if path:
                db_gui = DatabaseGUI(path)
                window["-DB-PATH-"].update(path)
                window["-TABLES-"].update(values=[])
                
        if event == "Create Table":
            if not db_gui:
                sg.popup_error("Please connect to a database first!")
                continue
                
            layout = [
                [sg.Text("Table Name:"), sg.Input(key="-TABLE-NAME-")],
                [sg.Text("Columns:")],
                [sg.Table(
                    values=[],
                    headings=["Column Name", "Data Type"],
                    auto_size_columns=True,
                    num_rows=5,
                    key="-COLUMNS-"
                )],
                [sg.Button("Add Column"), sg.Button("Create"), sg.Button("Cancel")]
            ]
            
            create_window = sg.Window("Create Table", layout)
            columns = []
            
            while True:
                create_event, create_values = create_window.read()
                
                if create_event in (sg.WIN_CLOSED, "Cancel"):
                    break
                    
                if create_event == "Add Column":
                    col_layout = [
                        [sg.Text("Column Name:"), sg.Input(key="-COL-NAME-")],
                        [sg.Text("Data Type:"), sg.Combo(
                            ["INTEGER", "TEXT", "REAL", "BLOB"],
                            key="-COL-TYPE-"
                        )],
                        [sg.Button("Add"), sg.Button("Cancel")]
                    ]
                    
                    col_window = sg.Window("Add Column", col_layout)
                    col_event, col_values = col_window.read(close=True)
                    
                    if col_event == "Add":
                        columns.append({
                            'name': col_values["-COL-NAME-"],
                            'type': col_values["-COL-TYPE-"]
                        })
                        create_window["-COLUMNS-"].update(values=[
                            [col['name'], col['type']] for col in columns
                        ])
                        
                if create_event == "Create":
                    if create_values["-TABLE-NAME-"] and columns:
                        if db_gui.create_table(create_values["-TABLE-NAME-"], columns):
                            sg.popup("Table created successfully!")
                            window["-TABLES-"].update(values=db_gui.get_tables())
                            break
                            
            create_window.close()
            
        if event == "Drop Table":
            if not db_gui:
                sg.popup_error("Please connect to a database first!")
                continue
                
            selected_table = values["-TABLES-"]
            if selected_table:
                if sg.popup_yes_no(f"Are you sure you want to drop table {selected_table[0]}?") == "Yes":
                    success, _, msg = db_gui.execute_query(f"DROP TABLE {selected_table[0]}")
                    if success:
                        sg.popup("Table dropped successfully!")
                        window["-TABLES-"].update(values=db_gui.get_tables())
                    else:
                        sg.popup_error(msg)
                        
        if event == "View Data":
            if not db_gui:
                sg.popup_error("Please connect to a database first!")
                continue
                
            selected_table = values["-TABLES-"]
            if selected_table:
                schema = db_gui.get_table_schema(selected_table[0])
                headings = [col[1] for col in schema]
                data = db_gui.get_table_data(selected_table[0])
                window["-RESULTS-"].update(values=data, headings=headings)
                
        if event == "Execute Query":
            if not db_gui:
                sg.popup_error("Please connect to a database first!")
                continue
                
            query = values["-QUERY-"].strip()
            if query:
                success, results, msg = db_gui.execute_query(query)
                if success and results:
                    window["-RESULTS-"].update(values=results)
                sg.popup(msg)
                
        if event == "Export Results":
            results = window["-RESULTS-"].get()
            if results:
                filename = f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(filename, 'w') as f:
                    if window["-RESULTS-"].ColumnHeadings:
                        f.write(','.join(window["-RESULTS-"].ColumnHeadings) + '\n')
                    for row in results:
                        f.write(','.join(map(str, row)) + '\n')
                sg.popup(f"Results exported to {filename}")
    
    if db_gui and db_gui.conn:
        db_gui.conn.close()
    window.close()

if __name__ == "__main__":
    main() 