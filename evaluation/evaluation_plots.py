from typing import List

from matplotlib import pyplot as plt


def save_histogram(data: List[float], title: str, x_label: str, y_label: str, filename: str, bins: int = 20):
    """
    Plots a histogram from the given data and saves it as a PNG file.

    :param data: List of numerical values to plot.
    :param title: Title of the histogram.
    :param x_label: Label for the X-axis.
    :param y_label: Label for the Y-axis.
    :param filename: Name of the file to save the histogram as.
    :param bins: Number of bins in the histogram.
    """
    plt.figure(figsize=(8, 6))
    plt.hist(data, bins=bins, color='blue', edgecolor='black', alpha=0.7)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()  # Prevents displaying the plot in a GUI
