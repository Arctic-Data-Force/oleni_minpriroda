import os
import shutil
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QListWidget, QLabel, QFileDialog, QGraphicsView, QGraphicsScene,
    QListWidgetItem, QMessageBox, QSlider, QSpinBox, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from classifier import classify_images

class ImageClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_folder = None
        self.classified_folder_path = None
        self.button_active = False
        self.confidence_threshold = 0.5  # Default confidence threshold
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Classifier')
        self.setGeometry(100, 100, 1200, 800)

        self.resizeEvent = self.on_resize

        main_layout = QHBoxLayout()

        # Left Panel
        left_panel = QVBoxLayout()

        self.default_folder_icon = QIcon('default_folder.png')  # Path to your default folder icon
        self.default_image_icon = QIcon('default_image.png')  # Path to your default image icon

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
        middle_layout = QVBoxLayout()

        self.file_list = QListWidget()
        self.file_list.setViewMode(QListWidget.ViewMode.ListMode)
        self.file_list.itemClicked.connect(self.show_image)
        middle_layout.addWidget(self.file_list)

        button_layout = QHBoxLayout()

        self.deer_button = QPushButton('Олень')
        self.deer_button.clicked.connect(lambda: self.move_image_to_class('Олень'))
        button_layout.addWidget(self.deer_button)

        self.musk_deer_button = QPushButton('Кабарга')
        self.musk_deer_button.clicked.connect(lambda: self.move_image_to_class('Кабарга'))
        button_layout.addWidget(self.musk_deer_button)

        self.roe_deer_button = QPushButton('Косуля')
        self.roe_deer_button.clicked.connect(lambda: self.move_image_to_class('Косуля'))
        button_layout.addWidget(self.roe_deer_button)

        middle_layout.addLayout(button_layout)

        self.image_preview = QGraphicsView()
        self.scene = QGraphicsScene()
        self.image_preview.setScene(self.scene)
        middle_layout.addWidget(self.image_preview)

        confidence_layout = QVBoxLayout()
        confidence_label = QLabel("Уровень уверенности:")
        confidence_layout.addWidget(confidence_label)
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(int(self.confidence_threshold * 100))
        self.confidence_slider.valueChanged.connect(self.update_confidence_threshold)
        confidence_layout.addWidget(self.confidence_slider)
        self.confidence_spinbox = QSpinBox()
        self.confidence_spinbox.setRange(0, 100)
        self.confidence_spinbox.setValue(int(self.confidence_threshold * 100))
        self.confidence_spinbox.valueChanged.connect(self.update_confidence_threshold)
        confidence_layout.addWidget(self.confidence_spinbox)

        middle_layout.addLayout(confidence_layout)

        main_layout.addLayout(middle_layout, 2)

        # Right Panel
        right_panel = QVBoxLayout()

        self.stats_label = QLabel('Статистика')
        right_panel.addWidget(self.stats_label)

        self.bar_chart_view = QChartView()
        right_panel.addWidget(self.bar_chart_view)

        self.pie_chart_view = QChartView()
        right_panel.addWidget(self.pie_chart_view)

        # Predefined folders panel
        predefined_panel = QVBoxLayout()

        self.predefined_folder_list = QListWidget(self)
        self.predefined_folder_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.predefined_folder_list.itemClicked.connect(self.load_predefined_folder)
        predefined_panel.addWidget(self.predefined_folder_list)

        self.update_predefined_folders([])

        right_panel.addLayout(predefined_panel)

        main_layout.addLayout(right_panel, 1)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Disable buttons initially
        self.update_buttons_state()

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
        if self.current_folder:
            image_path = os.path.join(self.current_folder, image_name)

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
        self.current_folder = folder_path
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
            item = QListWidgetItem(self.default_image_icon, "No images found")
            self.file_list.addItem(item)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Выберите папку', options=QFileDialog.Option.DontUseNativeDialog)
        if folder_path:
            self.update_folder_list(folder_path)

    def load_selected_folder(self, item):
        folder_path = item.text()
        print(f"Загружена папка: {folder_path}")
        self.load_icons(folder_path)
        if "Низкая уверенность" in folder_path:
            self.button_active = True
            print("Кнопки должны быть активны")
        else:
            self.button_active = False
            print("Кнопки должны быть неактивны")
        self.update_buttons_state()  # Обновляем состояние кнопок

    def load_predefined_folder(self, item):
        folder_path = item.text()
        print(f"Загружена предопределенная папка: {folder_path}")
        self.load_icons(folder_path)
        self.button_active = "Низкая уверенность" in folder_path
        print(f"button_active: {self.button_active}")
        self.update_buttons_state()

    def classify_images(self):
        classified_folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения классифицированных изображений", options=QFileDialog.Option.DontUseNativeDialog)
        if not classified_folder:
            return

        self.classified_folder_path = os.path.join(classified_folder, 'classified')
        classified_folders = classify_images(self.current_folder, self.classified_folder_path, self.confidence_threshold)
        if classified_folders:
            self.update_predefined_folders(classified_folders)
            self.show_statistics()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось классифицировать изображения.")

    def update_predefined_folders(self, folders):
        self.predefined_folder_list.clear()
        for folder in folders:
            item = QListWidgetItem(self.default_folder_icon, folder)
            self.predefined_folder_list.addItem(item)

    def move_image_to_class(self, class_name):
        selected_items = self.file_list.selectedItems()
        self.show_statistics()
        if selected_items and self.current_folder and self.classified_folder_path:
            file_name = selected_items[0].text()
            file_path = os.path.join(self.current_folder, file_name)
            dest_path = os.path.join(self.classified_folder_path, class_name, file_name)
            if os.path.exists(file_path):
                shutil.move(file_path, dest_path)
                self.load_icons(self.current_folder)
            else:
                QMessageBox.warning(self, "Ошибка", f"Файл не найден: {file_path}")

    def show_statistics(self):
        try:
            deer_count = len(os.listdir(os.path.join(self.classified_folder_path, 'Олень')))
            musk_deer_count = len(os.listdir(os.path.join(self.classified_folder_path, 'Кабарга')))
            roe_deer_count = len(os.listdir(os.path.join(self.classified_folder_path, 'Косуля')))
            uncertain_count = len(os.listdir(os.path.join(self.classified_folder_path, 'Низкая уверенность')))

            # Bar chart
            bar_set = QBarSet('Classified Images')
            bar_set << deer_count << musk_deer_count << roe_deer_count << uncertain_count

            series = QBarSeries()
            series.append(bar_set)

            bar_chart = QChart()
            bar_chart.addSeries(series)
            bar_chart.setTitle('Image Classification Statistics')

            categories = ['Олень', 'Кабарга', 'Косуля', 'Низкая уверенность']
            axisX = QBarCategoryAxis()
            axisX.append(categories)
            bar_chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axisX)

            axisY = QValueAxis()
            axisY.setRange(0, max(deer_count, musk_deer_count, roe_deer_count, uncertain_count) + 1)
            bar_chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)
            series.attachAxis(axisY)

            self.bar_chart_view.setChart(bar_chart)

            # Pie chart
            pie_series = QPieSeries()
            pie_series.append('Олень', deer_count)
            pie_series.append('Кабарга', musk_deer_count)
            pie_series.append('Косуля', roe_deer_count)
            pie_series.append('Низкая уверенность', uncertain_count)

            pie_chart = QChart()
            pie_chart.addSeries(pie_series)
            pie_chart.setTitle('Image Classification Distribution')

            self.pie_chart_view.setChart(pie_chart)
        except Exception as e:
            print(f"Error during statistics display: {e}")

    def update_buttons_state(self):
        selected_items = self.file_list.selectedItems()
        print(f"Выбранные элементы: {[item.text() for item in selected_items]}")

        buttons_enabled = self.button_active or (
                    bool(selected_items) and self.current_folder == self.classified_folder_path)
        print(f"Кнопки должны быть активны: {buttons_enabled}")

        self.deer_button.setEnabled(buttons_enabled)
        self.musk_deer_button.setEnabled(buttons_enabled)
        self.roe_deer_button.setEnabled(buttons_enabled)

    def set_button_active(self, active):
        self.button_active = active
        self.update_buttons_state()

    def preview_image(self, item):
        try:
            file_path = item.text()
            pixmap = QPixmap(file_path)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.image_preview.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        except Exception as e:
            print(f"Error during image preview: {e}")

    def update_confidence_threshold(self, value):
        self.confidence_threshold = value / 100.0
        self.confidence_slider.setValue(value)
        self.confidence_spinbox.setValue(value)

    def on_resize(self, event):
        self.image_preview.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)