import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QFileDialog, QMessageBox,
    QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image


class PDFConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """初始化界面"""
        self.setWindowTitle("图片合成 PDF")
        self.setGeometry(100, 100, 600, 500)

        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 拖放区域
        self.drop_label = QLabel("拖动图片到这里或点击下方按钮选择图片", self)
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 20px;
                border: 2px dashed #ccc;
                font-size: 16px;
            }
        """)
        self.drop_label.setAcceptDrops(True)
        layout.addWidget(self.drop_label)

        # 图片列表
        self.image_listbox = QListWidget(self)
        self.image_listbox.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.image_listbox)

        # 按钮布局
        button_layout = QHBoxLayout()

        self.select_button = QPushButton("选择图片", self)
        self.select_button.clicked.connect(self.select_files)
        button_layout.addWidget(self.select_button)

        self.move_up_button = QPushButton("上移", self)
        self.move_up_button.clicked.connect(self.move_up)
        button_layout.addWidget(self.move_up_button)

        self.move_down_button = QPushButton("下移", self)
        self.move_down_button.clicked.connect(self.move_down)
        button_layout.addWidget(self.move_down_button)

        self.generate_button = QPushButton("生成 PDF", self)
        self.generate_button.clicked.connect(self.generate_pdf)
        button_layout.addWidget(self.generate_button)

        layout.addLayout(button_layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖放文件进入窗口时触发"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """拖放文件释放时触发"""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.image_listbox.addItem(file_path)
            else:
                QMessageBox.warning(self, "警告", f"不支持的文件格式: {file_path}")

    def select_files(self):
        """选择图片文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        for file in files:
            self.image_listbox.addItem(file)

    def move_up(self):
        """将选中的图片上移"""
        selected = self.image_listbox.selectedItems()
        if not selected:
            return
        for item in selected:
            row = self.image_listbox.row(item)
            if row > 0:
                self.image_listbox.takeItem(row)
                self.image_listbox.insertItem(row - 1, item)
                self.image_listbox.setCurrentRow(row - 1)

    def move_down(self):
        """将选中的图片下移"""
        selected = self.image_listbox.selectedItems()
        if not selected:
            return
        for item in reversed(selected):
            row = self.image_listbox.row(item)
            if row < self.image_listbox.count() - 1:
                self.image_listbox.takeItem(row)
                self.image_listbox.insertItem(row + 1, item)
                self.image_listbox.setCurrentRow(row + 1)

    def generate_pdf(self):
        """生成 PDF"""
        if self.image_listbox.count() == 0:
            QMessageBox.warning(self, "警告", "请先选择图片")
            return

        output_pdf, _ = QFileDialog.getSaveFileName(
            self,
            "保存 PDF",
            "",
            "PDF 文件 (*.pdf)"
        )
        if not output_pdf:
            return

        image_paths = [self.image_listbox.item(i).text() for i in range(self.image_listbox.count())]
        self.create_pdf(image_paths, output_pdf)

    def create_pdf(self, image_paths, output_pdf):
        """将图片合成 PDF，保留原始分辨率"""
        c = canvas.Canvas(output_pdf, pagesize=A4)
        width, height = A4

        for image_path in image_paths:
            try:
                # 使用 PIL 打开图片以获取原始尺寸
                img = Image.open(image_path)
                img_width, img_height = img.size
                aspect = img_height / float(img_width)

                # 计算图片在 A4 页面上的位置和尺寸
                if aspect > 1:  # 竖图
                    draw_width = min(width, height / aspect)
                    draw_height = draw_width * aspect
                else:  # 横图
                    draw_height = min(height, width * aspect)
                    draw_width = draw_height / aspect

                # 居中绘制图片
                x = (width - draw_width) / 2
                y = (height - draw_height) / 2

                # 使用 reportlab 绘制图片
                c.drawImage(image_path, x, y, width=draw_width, height=draw_height, preserveAspectRatio=True)
                c.showPage()  # 结束当前页，开始新的一页
            except Exception as e:
                print(f"无法处理图片 {image_path}: {e}")

        c.save()
        QMessageBox.information(self, "成功", f"PDF 已生成并保存到 {output_pdf}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFConverterApp()
    window.show()
    sys.exit(app.exec_())
