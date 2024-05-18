import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QListWidget,
    QLabel,
    QFileDialog,
    QGraphicsView,
    QGraphicsScene,
    QListWidgetItem,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCharts import (
    QChart,
    QChartView,
    QPieSeries,
    QBarSeries,
    QBarSet,
    QBarCategoryAxis,
    QValueAxis
)


class ImageClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Classifier')
        self.setGeometry(100, 100, 1200, 800)

        self.resizeEvent = self.on_resize

        main_layout = QHBoxLayout()

        # Left Panel
        left_panel = QVBoxLayout()

        self.default_folder_icon = QIcon('default_folder.png')  # Путь к вашей иконке для папок по умолчанию
        self.default_image_icon = QIcon('default_image.png')  # Путь к вашей иконке для изображений по умолчанию

        self.upload_button = QPushButton('+')
        self.upload_button.clicked.connect(self.select_folder)
        left_panel.addWidget(self.upload_button)

        self.classify_button = QPushButton('Классифицировать')
        self.classify_button.clicked.connect(self.classify_images)
        left_panel.addWidget(self.classify_button)

        self.folder_list = QListWidget(self)
        self.folder_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.folder_list.itemClicked.connect(self.load_selected_folder)
        left_panel.addWidget(self.folder_list)

        main_layout.addLayout(left_panel, 1)

        # Middle Panel
        middle_panel = QVBoxLayout()

        self.file_list = QListWidget()
        self.file_list.setViewMode(QListWidget.ViewMode.ListMode)
        self.file_list.itemClicked.connect(self.show_image)
        middle_panel.addWidget(self.file_list)

        self.image_preview = QGraphicsView()
        self.scene = QGraphicsScene()
        self.image_preview.setScene(self.scene)
        middle_panel.addWidget(self.image_preview)

        main_layout.addLayout(middle_panel, 2)

        # Right Panel
        right_panel = QVBoxLayout()

        self.stats_label = QLabel('Статистика')
        right_panel.addWidget(self.stats_label)

        self.bar_chart_view = QChartView()
        right_panel.addWidget(self.bar_chart_view)

        self.pie_chart_view = QChartView()
        right_panel.addWidget(self.pie_chart_view)

        main_layout.addLayout(right_panel, 1)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def set_current_folder(self, folder_path):
        items = self.folder_list.findItems(folder_path, Qt.MatchFlag.MatchExactly)
        if items:
            self.folder_list.setCurrentItem(items[0])
            self.load_icons(folder_path)

    def update_folder_list(self, folder_path):
        folders = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]
        if folder_path not in folders:
            self.folder_list.addItem(QListWidgetItem(self.default_folder_icon, folder_path))
        # Ensure a folder is always selected
        if self.folder_list.count() > 0:
            self.folder_list.setCurrentRow(0)
            self.load_selected_folder(self.folder_list.currentItem())

    def show_image(self, item):
        image_name = item.text()
        current_folder_items = self.folder_list.selectedItems()
        if current_folder_items:
            folder_path = current_folder_items[0].text()
            image_path = os.path.join(folder_path, image_name)

            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение.")
                return

            screen_geometry = QApplication.primaryScreen().geometry()
            max_width, max_height = int(screen_geometry.width() * 0.8), int(screen_geometry.height() * 0.8)
            scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio)

            self.scene.clear()
            self.scene.addPixmap(scaled_pixmap)
            self.image_preview.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        else:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите папку")

    def load_icons(self, folder_path):
        self.file_list.clear()
        image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]

        if image_files:
            for index, image_file in enumerate(image_files):
                new_name = os.path.join(folder_path, f"img_{index}.png")
                while os.path.exists(new_name):
                    index += 1
                    new_name = os.path.join(folder_path, f"img_{index}.png")
                old_path = os.path.join(folder_path, image_file)
                os.rename(old_path, new_name)
                item = QListWidgetItem(self.default_image_icon, f"img_{index}.png")
                self.file_list.addItem(item)
        else:
            item = QListWidgetItem(self.default_image_icon, "В выбранной папке нет изображений.")
            self.file_list.addItem(item)

    def load_selected_folder(self, item):
        folder_path = item.text()
        self.load_icons(folder_path)

    def on_resize(self, event):
        # Get the current folder path
        current_folder_item = self.folder_list.currentItem()
        if current_folder_item:
            folder_path = current_folder_item.text()
            # Update the icons in the current folder
            self.load_icons(folder_path)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку", options=QFileDialog.Option.DontUseNativeDialog)
        if folder_path:
            self.load_icons(folder_path)
            self.update_folder_list(folder_path)
            self.set_current_folder(folder_path)

    def classify_images(self):
        try:
            if not os.path.exists('classified'):
                os.makedirs('classified')
            if not os.path.exists('classified/Олень'):
                os.makedirs('classified/Олень')
            if not os.path.exists('classified/Кабарга'):
                os.makedirs('classified/Кабарга')
            if not os.path.exists('classified/Косуля'):
                os.makedirs('classified/Косуля')

            for index in range(self.file_list.count()):
                file_path = os.path.join(self.folder_list.currentItem().text(), self.file_list.item(index).text())
                # Вставьте здесь логику классификации
                # Например: result = classify(file_path)
                result = 'Олень'  # Заглушка для результата
                if result == 'Олень':
                    shutil.copy(file_path, 'classified/Олень')
                elif result == 'Кабарга':
                    shutil.copy(file_path, 'classified/Кабарга')
                elif result == 'Косуля':
                    shutil.copy(file_path, 'classified/Косуля')

            self.show_statistics()
        except Exception as e:
            print(f"Error during classification: {e}")

    def show_statistics(self):
        try:
            deer_count = len(os.listdir('classified/Олень'))
            musk_deer_count = len(os.listdir('classified/Кабарга'))
            roe_deer_count = len(os.listdir('classified/Косуля'))

            # Гистограмма
            bar_set = QBarSet('Classified Images')
            bar_set << deer_count << musk_deer_count << roe_deer_count

            series = QBarSeries()
            series.append(bar_set)

            bar_chart = QChart()
            bar_chart.addSeries(series)
            bar_chart.setTitle('Image Classification Statistics')

            categories = ['Олень', 'Кабарга', 'Косуля']
            axisX = QBarCategoryAxis()
            axisX.append(categories)
            bar_chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axisX)

            axisY = QValueAxis()
            axisY.setRange(0, max(deer_count, musk_deer_count, roe_deer_count) + 1)
            bar_chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)
            series.attachAxis(axisY)

            self.bar_chart_view.setChart(bar_chart)

            # Круговая диаграмма
            pie_series = QPieSeries()
            pie_series.append('Олень', deer_count)
            pie_series.append('Кабарга', musk_deer_count)
            pie_series.append('Косуля', roe_deer_count)

            pie_chart = QChart()
            pie_chart.addSeries(pie_series)
            pie_chart.setTitle('Image Classification Distribution')

            self.pie_chart_view.setChart(pie_chart)
        except Exception as e:
            print(f"Error during statistics display: {e}")

    def preview_image(self, item):
        try:
            file_path = item.text()
            pixmap = QPixmap(file_path)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.image_preview.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        except Exception as e:
            print(f"Error during image preview: {e}")


def main():
    app = QApplication(sys.argv)
    ex = ImageClassifierApp()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
