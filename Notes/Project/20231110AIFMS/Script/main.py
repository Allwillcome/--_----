import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
import pandas as pd
import subprocess #Mac 电脑专用，调用 LibreOffice
from PyPDF2 import PdfReader, PdfWriter

class ExcelToPDFConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # 设置窗口的标题和大小
        self.setWindowTitle("智能FMS功能性筛查训练方案")
        self.setGeometry(300, 300, 350, 200)

        # 布局和组件
        layout = QVBoxLayout()

        self.label = QLabel('📢请选择原始评分文件', self)
        layout.addWidget(self.label)

        select_button = QPushButton("📜请选择评分文件", self)
        select_button.clicked.connect(self.openFileNameDialog)
        layout.addWidget(select_button)

        print_button = QPushButton("🏋️生成训练方案", self)
        print_button.clicked.connect(self.ExcelToPdf)
        layout.addWidget(print_button)

        self.setLayout(layout)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "选择 Excel 文件", "", "Excel Files(*.xlsx)", options=options)
        
        if fileName:
            self.label.setText(fileName)

    #  将 excel 导出为 pdf
    def ExcelToPdf(self):
        excel_path = self.label.text()
        excel_dir,_ = os.path.split(excel_path)
        output_pdf_path = excel_dir
        pdf_path = excel_path.replace(".xlsx", ".pdf")
        try:
            # 使用 Libreoffice 将excel 转变为 pdf
            subprocess.run(["/Applications/LibreOffice.app/Contents/MacOS/soffice", 
                            "--headless", "--convert-to", "pdf", excel_path, 
                            "--outdir", output_pdf_path], check=True)
            print("打印成功")

            reader = PdfReader(pdf_path)
            writer = PdfWriter()

            # 获取最后一页并添加到新的 PDF
            last_page = reader.pages[-1]  
            writer.add_page(last_page)  

            # 保存新的 PDF
            output_pdf_path =  pdf_path
            with open(output_pdf_path, "wb") as output_pdf:
                writer.write(output_pdf)
            self.label.setText("✅训练方案已保存至：\n"+ pdf_path)
        except subprocess.CalledProcessError as e:
            print("方案生成失败:\n ", e)
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ExcelToPDFConverter()
    ex.show()
    sys.exit(app.exec_())
