import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, \
    QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, \
    QListWidget, QListWidgetItem, QLabel, QMessageBox,\
    QScrollArea, QStackedWidget
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Простой просмотрщик изображений")
        self.setGeometry(100, 100, 800, 600)
        
        self.resizeEvent = self.on_resize

        # Главное окно
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)

        self.button = QPushButton("Выбрать папку", self)
        self.button.clicked.connect(self.select_folder)

        self.folder_list = QListWidget(self)
        self.folder_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)  # Изменение режима выбора на одиночный
        self.folder_list.itemClicked.connect(self.load_selected_folder)

        self.image_list = QListWidget(self)
        self.image_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.image_list.itemClicked.connect(self.show_image)

        self.default_folder_icon = QIcon('default_folder.png')  # Путь к вашей иконке для папок по умолчанию
        self.default_image_icon = QIcon('default_image.png')  # Путь к вашей иконке для изображений по умолчанию

        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.button)
        self.button_layout.addWidget(self.folder_list)

        self.button_container = QWidget()
        self.button_container.setLayout(self.button_layout)
        self.button_container.setFixedWidth(200)  # Устанавливаем фиксированную ширину

        self.list_layout = QVBoxLayout()
        self.list_layout.addWidget(self.image_list)

        self.main_layout.addWidget(self.button_container)
        self.main_layout.addLayout(self.list_layout)

        # Виджет для отображения изображения
        self.image_widget = QWidget()
        self.image_layout = QVBoxLayout(self.image_widget)
        
        self.back_button = QPushButton("Назад", self)
        self.back_button.clicked.connect(self.back_to_main_view)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.image_layout.addWidget(self.back_button)
        self.image_layout.addWidget(self.scroll_area)
        
        # Создаем стек виджетов
        self.stack = QStackedWidget(self)
        self.stack.addWidget(self.main_widget)
        self.stack.addWidget(self.image_widget)

       
        
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

    def load_icons(self, folder_path):
        self.image_list.clear()
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
                self.image_list.addItem(item)
        else:
            item = QListWidgetItem(self.default_image_icon, "В выбранной папке нет изображений.")
            self.image_list.addItem(item)



    def update_folder_list(self, folder_path):
        folders = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]
        if folder_path not in folders:
            self.folder_list.addItem(QListWidgetItem(self.default_folder_icon, folder_path))
        # Ensure a folder is always selected
        if self.folder_list.count() > 0:
            self.folder_list.setCurrentRow(0)
            self.load_selected_folder(self.folder_list.currentItem())

    def set_current_folder(self, folder_path):
        items = self.folder_list.findItems(folder_path, Qt.MatchFlag.MatchExactly)
        if items:
            self.folder_list.setCurrentItem(items[0])
            self.load_icons(folder_path)

    def load_selected_folder(self, item):
        folder_path = item.text()
        self.load_icons(folder_path)

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

            self.image_label.setPixmap(scaled_pixmap)
            self.stack.setCurrentWidget(self.image_widget)
        else:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите папку")

    def back_to_main_view(self):
        self.stack.setCurrentWidget(self.main_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec())
