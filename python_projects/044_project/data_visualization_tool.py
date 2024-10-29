import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
from typing import List, Dict, Optional
import json
import numpy as np
from datetime import datetime

class ChartType:
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    BOX = "box"
    HEATMAP = "heatmap"

class DataVisualizer:
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.config_file = Path("chart_config.json")
        self.load_config()
        self.theme = "default"
        self.figure_size = (10, 6)
        self.current_file: Optional[Path] = None
        
    def load_config(self):
        """Load chart configuration settings"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "themes": {
                    "default": {
                        "style": "seaborn",
                        "palette": "deep"
                    },
                    "dark": {
                        "style": "dark_background",
                        "palette": "dark"
                    },
                    "light": {
                        "style": "whitegrid",
                        "palette": "pastel"
                    }
                },
                "default_size": [10, 6],
                "save_format": "png",
                "dpi": 300
            }
            self.save_config()

    def save_config(self):
        """Save chart configuration settings"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def load_data(self, file_path: str) -> bool:
        """Load data from CSV or Excel file"""
        try:
            file_path = Path(file_path)
            if file_path.suffix.lower() == '.csv':
                self.data = pd.read_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                self.data = pd.read_excel(file_path)
            else:
                print("Unsupported file format!")
                return False
            
            self.current_file = file_path
            print(f"Loaded data with {len(self.data)} rows and {len(self.data.columns)} columns")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def set_theme(self, theme_name: str):
        """Set the visualization theme"""
        if theme_name in self.config["themes"]:
            theme = self.config["themes"][theme_name]
            plt.style.use(theme["style"])
            sns.set_palette(theme["palette"])
            self.theme = theme_name
            print(f"Theme set to {theme_name}")
        else:
            print("Invalid theme name!")

    def create_chart(self, chart_type: str, x_column: str, y_column: str = None,
                    title: str = "", **kwargs) -> bool:
        """Create a chart based on the specified type"""
        if self.data is None:
            print("No data loaded!")
            return False

        try:
            plt.figure(figsize=self.figure_size)
            
            if chart_type == ChartType.LINE:
                self._create_line_chart(x_column, y_column, title, **kwargs)
            elif chart_type == ChartType.BAR:
                self._create_bar_chart(x_column, y_column, title, **kwargs)
            elif chart_type == ChartType.SCATTER:
                self._create_scatter_plot(x_column, y_column, title, **kwargs)
            elif chart_type == ChartType.PIE:
                self._create_pie_chart(x_column, y_column, title, **kwargs)
            elif chart_type == ChartType.HISTOGRAM:
                self._create_histogram(x_column, title, **kwargs)
            elif chart_type == ChartType.BOX:
                self._create_box_plot(x_column, y_column, title, **kwargs)
            elif chart_type == ChartType.HEATMAP:
                self._create_heatmap(title, **kwargs)
            else:
                print("Unsupported chart type!")
                return False

            plt.title(title)
            return True
        except Exception as e:
            print(f"Error creating chart: {e}")
            return False

    def _create_line_chart(self, x_column: str, y_column: str, title: str, **kwargs):
        plt.plot(self.data[x_column], self.data[y_column], **kwargs)
        plt.xlabel(x_column)
        plt.ylabel(y_column)

    def _create_bar_chart(self, x_column: str, y_column: str, title: str, **kwargs):
        plt.bar(self.data[x_column], self.data[y_column], **kwargs)
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.xticks(rotation=45)

    def _create_scatter_plot(self, x_column: str, y_column: str, title: str, **kwargs):
        plt.scatter(self.data[x_column], self.data[y_column], **kwargs)
        plt.xlabel(x_column)
        plt.ylabel(y_column)

    def _create_pie_chart(self, x_column: str, y_column: str, title: str, **kwargs):
        plt.pie(self.data[y_column], labels=self.data[x_column], autopct='%1.1f%%', **kwargs)

    def _create_histogram(self, column: str, title: str, **kwargs):
        plt.hist(self.data[column], **kwargs)
        plt.xlabel(column)
        plt.ylabel("Frequency")

    def _create_box_plot(self, x_column: str, y_column: str, title: str, **kwargs):
        sns.boxplot(x=self.data[x_column], y=self.data[y_column], **kwargs)
        plt.xlabel(x_column)
        plt.ylabel(y_column)

    def _create_heatmap(self, title: str, **kwargs):
        correlation = self.data.corr()
        sns.heatmap(correlation, annot=True, cmap='coolwarm', **kwargs)

    def save_chart(self, output_path: str = None):
        """Save the current chart"""
        if output_path is None and self.current_file is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.current_file.with_name(
                f"{self.current_file.stem}_chart_{timestamp}.{self.config['save_format']}"
            )
        
        try:
            plt.savefig(output_path, dpi=self.config["dpi"], bbox_inches='tight')
            print(f"Chart saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving chart: {e}")
            return False

    def show_chart(self):
        """Display the current chart"""
        plt.show()

    def get_data_info(self) -> Dict:
        """Get information about the loaded data"""
        if self.data is None:
            return {}
        
        return {
            "rows": len(self.data),
            "columns": list(self.data.columns),
            "data_types": self.data.dtypes.to_dict(),
            "missing_values": self.data.isnull().sum().to_dict()
        }

    def get_column_statistics(self, column: str) -> Dict:
        """Get statistical information about a specific column"""
        if self.data is None or column not in self.data.columns:
            return {}
        
        if pd.api.types.is_numeric_dtype(self.data[column]):
            return {
                "mean": self.data[column].mean(),
                "median": self.data[column].median(),
                "std": self.data[column].std(),
                "min": self.data[column].min(),
                "max": self.data[column].max()
            }
        else:
            return {
                "unique_values": self.data[column].nunique(),
                "most_common": self.data[column].value_counts().head().to_dict()
            }

def main():
    visualizer = DataVisualizer()
    
    while True:
        print("\nData Visualization Tool")
        print("1. Load Data")
        print("2. Create Chart")
        print("3. Set Theme")
        print("4. Show Data Info")
        print("5. Show Column Statistics")
        print("6. Save Chart")
        print("7. Show Chart")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == "1":
            file_path = input("Enter data file path (CSV or Excel): ")
            visualizer.load_data(file_path)
        
        elif choice == "2":
            if visualizer.data is None:
                print("Please load data first!")
                continue
            
            print("\nAvailable chart types:")
            print("1. Line Chart")
            print("2. Bar Chart")
            print("3. Scatter Plot")
            print("4. Pie Chart")
            print("5. Histogram")
            print("6. Box Plot")
            print("7. Heatmap")
            
            chart_choice = input("Choose chart type (1-7): ")
            chart_types = {
                "1": ChartType.LINE,
                "2": ChartType.BAR,
                "3": ChartType.SCATTER,
                "4": ChartType.PIE,
                "5": ChartType.HISTOGRAM,
                "6": ChartType.BOX,
                "7": ChartType.HEATMAP
            }
            
            if chart_choice not in chart_types:
                print("Invalid chart type!")
                continue
            
            chart_type = chart_types[chart_choice]
            
            if chart_type == ChartType.HEATMAP:
                title = input("Enter chart title: ")
                visualizer.create_chart(chart_type, None, None, title)
            else:
                print("\nAvailable columns:", ", ".join(visualizer.data.columns))
                x_column = input("Enter X-axis column: ")
                y_column = input("Enter Y-axis column (leave empty for histogram): ").strip()
                title = input("Enter chart title: ")
                
                if y_column:
                    visualizer.create_chart(chart_type, x_column, y_column, title)
                else:
                    visualizer.create_chart(chart_type, x_column, title=title)
        
        elif choice == "3":
            print("\nAvailable themes:")
            for theme in visualizer.config["themes"]:
                print(f"- {theme}")
            theme = input("Enter theme name: ")
            visualizer.set_theme(theme)
        
        elif choice == "4":
            info = visualizer.get_data_info()
            if info:
                print("\nData Information:")
                print(f"Rows: {info['rows']}")
                print(f"Columns: {', '.join(info['columns'])}")
                print("\nData Types:")
                for col, dtype in info['data_types'].items():
                    print(f"{col}: {dtype}")
                print("\nMissing Values:")
                for col, count in info['missing_values'].items():
                    print(f"{col}: {count}")
            else:
                print("No data loaded!")
        
        elif choice == "5":
            if visualizer.data is None:
                print("Please load data first!")
                continue
            
            print("\nAvailable columns:", ", ".join(visualizer.data.columns))
            column = input("Enter column name: ")
            stats = visualizer.get_column_statistics(column)
            
            if stats:
                print(f"\nStatistics for {column}:")
                for key, value in stats.items():
                    print(f"{key}: {value}")
            else:
                print("Invalid column name!")
        
        elif choice == "6":
            output_path = input("Enter output path (or press Enter for auto-name): ").strip()
            if output_path:
                visualizer.save_chart(output_path)
            else:
                visualizer.save_chart()
        
        elif choice == "7":
            visualizer.show_chart()
        
        elif choice == "8":
            print("Thank you for using Data Visualization Tool!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 