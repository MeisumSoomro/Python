import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Dict, Tuple
import io
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from enum import Enum

class PlotType(Enum):
    LINE = "Line Plot"
    BAR = "Bar Plot"
    SCATTER = "Scatter Plot"
    HISTOGRAM = "Histogram"
    BOX = "Box Plot"
    HEATMAP = "Heatmap"

class DataVisualizer:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.current_file: Optional[str] = None
        self.numeric_columns: List[str] = []
        
    def load_data(self, filepath: str) -> bool:
        try:
            if filepath.endswith('.csv'):
                self.df = pd.read_csv(filepath)
            elif filepath.endswith(('.xls', '.xlsx')):
                self.df = pd.read_excel(filepath)
            else:
                return False
                
            self.current_file = filepath
            self.numeric_columns = self.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            return True
        except Exception as e:
            sg.popup_error(f"Error loading file: {str(e)}")
            return False
    
    def get_basic_stats(self) -> str:
        if self.df is None:
            return "No data loaded"
        
        stats = []
        stats.append(f"Rows: {len(self.df)}")
        stats.append(f"Columns: {len(self.df.columns)}")
        stats.append("\nNumerical Columns Statistics:")
        
        for col in self.numeric_columns:
            stats.append(f"\n{col}:")
            stats.append(f"  Mean: {self.df[col].mean():.2f}")
            stats.append(f"  Median: {self.df[col].median():.2f}")
            stats.append(f"  Std Dev: {self.df[col].std():.2f}")
            
        return "\n".join(stats)
    
    def create_plot(self, plot_type: PlotType, x_col: str, y_col: Optional[str] = None) -> Optional[bytes]:
        if self.df is None:
            return None
            
        plt.figure(figsize=(10, 6))
        try:
            if plot_type == PlotType.LINE:
                plt.plot(self.df[x_col], self.df[y_col] if y_col else self.df[x_col])
                plt.title(f"Line Plot: {y_col or x_col} over {x_col}")
                
            elif plot_type == PlotType.BAR:
                plt.bar(self.df[x_col], self.df[y_col] if y_col else self.df[x_col])
                plt.title(f"Bar Plot: {y_col or x_col} by {x_col}")
                
            elif plot_type == PlotType.SCATTER:
                plt.scatter(self.df[x_col], self.df[y_col] if y_col else self.df[x_col])
                plt.title(f"Scatter Plot: {y_col or x_col} vs {x_col}")
                
            elif plot_type == PlotType.HISTOGRAM:
                plt.hist(self.df[x_col], bins=30)
                plt.title(f"Histogram of {x_col}")
                
            elif plot_type == PlotType.BOX:
                plt.boxplot(self.df[x_col])
                plt.title(f"Box Plot of {x_col}")
                
            elif plot_type == PlotType.HEATMAP:
                if len(self.numeric_columns) > 1:
                    sns.heatmap(self.df[self.numeric_columns].corr(), annot=True)
                    plt.title("Correlation Heatmap")
            
            plt.xlabel(x_col)
            if y_col:
                plt.ylabel(y_col)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='PNG')
            plt.close()
            return buf.getvalue()
            
        except Exception as e:
            sg.popup_error(f"Error creating plot: {str(e)}")
            plt.close()
            return None

def create_layout():
    return [
        [sg.Menu([['File', ['Open', 'Save Plot', 'Exit']]])],
        [sg.Text("Data Visualization Tool", font=("Helvetica", 16))],
        [sg.Frame("Data Preview", [
            [sg.Table(
                values=[],
                headings=[],
                auto_size_columns=True,
                num_rows=5,
                key="-TABLE-"
            )]
        ])],
        [sg.Frame("Plot Controls", [
            [
                sg.Text("Plot Type:"),
                sg.Combo(
                    [plot_type.value for plot_type in PlotType],
                    key="-PLOT-TYPE-",
                    enable_events=True
                )
            ],
            [
                sg.Text("X Column:"),
                sg.Combo([], key="-X-COL-", enable_events=True)
            ],
            [
                sg.Text("Y Column:"),
                sg.Combo([], key="-Y-COL-", enable_events=True)
            ],
            [sg.Button("Generate Plot")]
        ])],
        [sg.Frame("Statistics", [
            [sg.Multiline(
                size=(60, 10),
                key="-STATS-",
                disabled=True
            )]
        ])],
        [sg.Image(key="-PLOT-")]
    ]

def main():
    visualizer = DataVisualizer()
    window = sg.Window("Data Visualizer", create_layout(), resizable=True)
    
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
            
        if event == 'Open':
            filepath = sg.popup_get_file(
                'Open Data File',
                file_types=(
                    ("CSV Files", "*.csv"),
                    ("Excel Files", "*.xlsx *.xls")
                )
            )
            if filepath and visualizer.load_data(filepath):
                # Update table preview
                window["-TABLE-"].update(
                    values=visualizer.df.head().values.tolist(),
                    headings=visualizer.df.columns.tolist()
                )
                
                # Update column selections
                all_columns = visualizer.df.columns.tolist()
                window["-X-COL-"].update(values=all_columns)
                window["-Y-COL-"].update(values=all_columns)
                
                # Update statistics
                window["-STATS-"].update(visualizer.get_basic_stats())
                
        if event == "Generate Plot" and visualizer.df is not None:
            plot_type = PlotType(values["-PLOT-TYPE-"])
            x_col = values["-X-COL-"]
            y_col = values["-Y-COL-"] if values["-Y-COL-"] else None
            
            if x_col:
                plot_data = visualizer.create_plot(plot_type, x_col, y_col)
                if plot_data:
                    window["-PLOT-"].update(data=plot_data)
                    
        if event == "Save Plot":
            filepath = sg.popup_get_file(
                'Save Plot As',
                save_as=True,
                file_types=(("PNG Files", "*.png"),)
            )
            if filepath and window["-PLOT-"].get():
                with open(filepath, 'wb') as f:
                    f.write(window["-PLOT-"].get())
    
    window.close()

if __name__ == "__main__":
    main() 