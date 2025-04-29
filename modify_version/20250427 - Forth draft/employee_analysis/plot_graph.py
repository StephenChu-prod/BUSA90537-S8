import matplotlib.pyplot as plt # Reference: https://matplotlib.org/stable/gallery/index.html
import pandas as pd
import numpy as np 

class Plotter:
    """
    Plotter class to handle different types of charts for data visualization.
    Reference: https://matplotlib.org/stable/gallery/index.html
    """

    @staticmethod
    def plot_pie(data, labels_column, values_column, title="Pie Chart", save_path=None):
        """
        Draw a pie chart.
        
        Parameters:
        - data: pandas DataFrame
        - labels_column: column name for labels
        - values_column: column name for values
        - title: title of the pie chart
        """
        labels = data[labels_column]
        sizes = data[values_column]

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title(title)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        if save_path:
            path = f"{save_path}.png"
            plt.savefig(path)
            print(f"Plot saved to {path}")
            plt.close()
        else:
            plt.show()
        
    @staticmethod
    def plot_bar(data, x_column, y_column, title="Bar Chart", xlabel=None, ylabel=None, save_path=None, clr='skyblue'):
        """
        Draw a bar chart.
        
        Parameters:
        - data: pandas DataFrame
        - x_column: column name for x-axis
        - y_column: column name for y-axis
        - title: title of the bar chart
        - xlabel: label for x-axis
        - ylabel: label for y-axis
        - color: color of the bars (default is 'skyblue')
        """
        plt.figure(figsize=(10, 6))
        plt.bar(data[x_column], data[y_column], color=clr, width=0.5)
        plt.axhline(0, color='black', linewidth=1)
        plt.title(title)
        plt.xlabel(xlabel if xlabel else x_column)
        plt.ylabel(ylabel if ylabel else y_column)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if save_path:
            path = f"{save_path}.png"
            plt.savefig(path)
            print(f"Plot saved to {path}")
            plt.close()
        else:
            plt.show()

    @staticmethod
    def plot_line(data, x_column, y_column, title="Line Chart", xlabel=None, ylabel=None, save_path=None):
        """
        Draw a line chart.
        
        Parameters:
        - data: pandas DataFrame
        - x_column: column name for x-axis
        - y_column: column name for y-axis
        - title: title of the line chart
        - xlabel: label for x-axis
        - ylabel: label for y-axis
        """
        plt.figure(figsize=(10, 6))
        plt.plot(data[x_column], data[y_column], marker='o', linestyle='-')
        plt.title(title)
        plt.xlabel(xlabel if xlabel else x_column)
        plt.ylabel(ylabel if ylabel else y_column)
        plt.grid(True)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        if save_path:
            path = f"{save_path}.png"
            plt.savefig(path)
            print(f"Plot saved to {path}")
            plt.close()
        else:
            plt.show()


    @staticmethod
    def plot_stacked_bar(data, x_column, y_columns, title="Stacked Bar Chart", xlabel=None, ylabel=None, colors=None, save_path=None):
        """
        Draw a stacked bar chart.

        Parameters:
        - data: pandas DataFrame
        - x_column: column name for x-axis
        - y_columns: list of column names to stack on y-axis
        - title: title of the bar chart
        - xlabel: label for x-axis
        - ylabel: label for y-axis
        - colors: list of two colors
        - save_path: if given, save the plot
        """
        # Make sure columns are strings
        data.columns = data.columns.map(str)

        # Set the x-axis
        ax = data.set_index(x_column)[y_columns].plot(
            kind='bar',
            stacked=True,
            figsize=(12, 6),
            color=colors if colors else ['skyblue', 'salmon']
        )

        ax.legend(y_columns, loc='upper left')
        plt.title(title)
        plt.ylabel(ylabel if ylabel else 'Value')
        plt.xlabel(xlabel if xlabel else 'Category')
        plt.axhline(0, color='black', linewidth=0.8)  # Draw horizontal line at y=0
        plt.xticks(rotation=90, fontsize=7)
        plt.tight_layout()

        if save_path:
            plt.savefig(f"{save_path}.png")
            print(f"Plot saved to {save_path}.png")
            plt.close()
        else:
            plt.show()  

    @staticmethod
    def plot_grouped_bar(data, x_column, y_columns, title="Grouped Bar Chart", xlabel=None, ylabel=None, colors=None, save_path=None):
        """
        Draw a grouped (side-by-side) bar chart.
   
        Parameters:
        - data: pandas DataFrame
        - x_column: column name for x-axis
        - y_columns: list of two column names to compare
        - title: title of the bar chart
        - xlabel: label for x-axis
        - ylabel: label for y-axis
        - colors: list of colors for the bars
        - save_path: if given, save the plot
        """


        data.columns = data.columns.map(str)
        x = np.arange(len(data[x_column]))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width/2, data[y_columns[0]], width, label=y_columns[0], color=colors[0] if colors else 'skyblue')
        bars2 = ax.bar(x + width/2, data[y_columns[1]], width, label=y_columns[1], color=colors[1] if colors else 'salmon')

        ax.set_ylabel(ylabel if ylabel else 'Value')
        ax.set_xlabel(xlabel if xlabel else x_column)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(data[x_column], rotation=45, ha='right')
        ax.axhline(0, color='black', linewidth=0.8)
        ax.legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(f"{save_path}.png")
            print(f"Plot saved to {save_path}.png")
            plt.close()
        else:
            plt.show()