import os
import pandas as pd
import mimetypes
import treelib
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import numpy as np
from fpdf import FPDF

def get_file_info(directory):
    """
    Scans the given directory and returns file details including size, type, and path.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError("The specified file path does not exist. Please provide a valid directory.")
    
    file_data = []
    file_structure = treelib.Tree()
    file_structure.create_node(directory, directory)  # Root node
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            file_type, _ = mimetypes.guess_type(file_path)
            
            file_data.append({
                "Folder": root,
                "File Name": file,
                "File Size (KB)": round(file_size / 1024, 2),
                "File Type": str(file_type) if file_type else "Unknown"
            })
            
            if not file_structure.contains(root):
                file_structure.create_node(root, root, parent=directory)
            file_structure.create_node(file, file_path, parent=root)
    
    return file_data, file_structure

def save_pdf_report(df, output_filename="file_analysis_report.pdf"):
    """
    Generates a PDF report containing the file analysis summary.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="File Analysis Report", ln=True, align='C')
    pdf.ln(10)
    
    for index, row in df.iterrows():
        pdf.cell(200, 10, txt=f"Folder: {row['Folder']}", ln=True)
        pdf.cell(200, 10, txt=f"File Name: {row['File Name']}", ln=True)
        pdf.cell(200, 10, txt=f"File Size (KB): {row['File Size (KB)']}", ln=True)
        pdf.cell(200, 10, txt=f"File Type: {row['File Type']}", ln=True)
        pdf.ln(5)
    
    pdf.output(output_filename)
    print(f"PDF report saved as {output_filename}")

def display_results(file_data, file_structure):
    """
    Displays file data in a GUI format with multiple plots and a scrollable layout.
    """
    df = pd.DataFrame(file_data)
    if df.empty:
        print("No files found in the specified directory.")
        return
    
    app = QtWidgets.QApplication([])
    win = QtWidgets.QScrollArea()
    container = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    container.setLayout(layout)
    win.setWidget(container)
    win.setWidgetResizable(True)
    win.setWindowTitle("File Analysis")
    win.resize(1000, 800)
    
    plot_widget = pg.GraphicsLayoutWidget()
    layout.addWidget(plot_widget)
    
    def create_bar_chart(plot, x_data, y_data, title):
        plot.setTitle(title)
        x_ticks = list(range(len(x_data)))
        bar_chart = pg.BarGraphItem(x=x_ticks, height=y_data, width=0.6, brush='b')
        plot.addItem(bar_chart)
        shortened_labels = [os.path.basename(x) if len(x) > 15 else x for x in x_data]
        plot.getAxis('bottom').setTicks([list(enumerate(shortened_labels))])
    
    p1 = plot_widget.addPlot()
    file_size_by_type = df.groupby("File Type")['File Size (KB)'].sum()
    create_bar_chart(p1, file_size_by_type.index.tolist(), file_size_by_type.values, "File Size Distribution By Type")
    
    plot_widget.nextRow()
    p2 = plot_widget.addPlot()
    folder_count = df["Folder"].value_counts()
    create_bar_chart(p2, folder_count.index.tolist(), folder_count.values, "File Count Per Folder")
    
    plot_widget.nextRow()
    p3 = plot_widget.addPlot()
    file_type_count = df["File Type"].value_counts()
    create_bar_chart(p3, file_type_count.index.tolist(), file_type_count.values, "File Type Count")
    
    plot_widget.nextRow()
    p4 = plot_widget.addPlot()
    folder_size = df.groupby("Folder")['File Size (KB)'].sum()
    create_bar_chart(p4, folder_size.index.tolist(), folder_size.values, "Folder-Wise File Size")
    
    plot_widget.nextRow()
    p5 = plot_widget.addPlot()
    type_size_dist = df.groupby("File Type")['File Size (KB)'].sum()
    create_bar_chart(p5, type_size_dist.index.tolist(), type_size_dist.values, "File Type-Wise Size Distribution")
    
    win.show()
    save_pdf_report(df)
    QtWidgets.QApplication.instance().exec()

def main():
    """
    Main function to execute the script.
    """
    directory = input("Enter the directory path: ")
    try:
        file_data, file_structure = get_file_info(directory)
        display_results(file_data, file_structure)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()