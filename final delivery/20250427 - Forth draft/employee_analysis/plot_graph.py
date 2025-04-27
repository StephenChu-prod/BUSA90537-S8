import matplotlib.pyplot as plt # Reference: https://matplotlib.org/stable/gallery/index.html
import pandas as pd

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
    def plot_bar(data, x_column, y_column, title="Bar Chart", xlabel=None, ylabel=None, save_path=None):
        """
        Draw a bar chart.
        
        Parameters:
        - data: pandas DataFrame
        - x_column: column name for x-axis
        - y_column: column name for y-axis
        - title: title of the bar chart
        - xlabel: label for x-axis
        - ylabel: label for y-axis
        """
        plt.figure(figsize=(10, 6))
        plt.bar(data[x_column], data[y_column], color='skyblue', width=0.5)
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
