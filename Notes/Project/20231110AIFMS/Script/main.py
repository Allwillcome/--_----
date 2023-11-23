import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
import pandas as pd
from reportlab.lib import pagesizes
from reportlab.pdfgen import canvas

class ExcelToPDFConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # 设置窗口的标题和大小
        self.setWindowTitle("Excel 到 PDF 转换器")
        self.setGeometry(300, 300, 350, 200)

        # 布局和组件
        layout = QVBoxLayout()

        self.label = QLabel('请选择 Excel 文件', self)
        layout.addWidget(self.label)

        select_button = QPushButton("选择文件", self)
        select_button.clicked.connect(self.openFileNameDialog)
        layout.addWidget(select_button)

        print_button = QPushButton("转换为 PDF", self)
        print_button.clicked.connect(self.print_to_pdf)
        layout.addWidget(print_button)

        self.setLayout(layout)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "选择 Excel 文件", "", "Excel Files(*.xlsx)", options=options)
        
        if fileName:
            self.label.setText(fileName)

    def print_to_pdf(self):
        file_path = self.label.text()
        try:
            df = pd.read_excel(file_path, sheet_name="输出报告")

            pdf_path = file_path.replace(".xlsx", ".pdf")
            c = canvas.Canvas(pdf_path, pagesizes.letter)

            width, height = pagesizes.letter

            text_obj = c.beginText(40, height - 40)
            for index, row in df.iterrows():
                line = ", ".join(map(str, row))
                text_obj.textLine(line)

            c.drawText(text_obj)
            c.save()

            self.label.setText("PDF 已保存至："+ pdf_path)
        except Exception as e:
            self.label.setText("错误：" + str(e))
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ExcelToPDFConverter()
    ex.show()
    sys.exit(app.exec_())
