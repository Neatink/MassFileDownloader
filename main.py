import os
import requests
import subprocess
import json
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QWidget,QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QProgressBar, QFileDialog,QGraphicsOpacityEffect,QFrame
from PyQt5.QtGui import QIcon,QDesktopServices
from PyQt5.QtCore import Qt, QThread, pyqtSignal,QUrl,QTimer
import webbrowser
import sys
import os

class DownloadThread(QThread):
    progress_update = pyqtSignal(str, int, int, int, str)
    download_complete = pyqtSignal(str, str)

    def __init__(self, app_name, download_url, file_name):
        super().__init__()
        self.app_name = app_name
        self.download_url = download_url
        self.file_name = file_name

    def run(self):
        global total_size
        response = requests.get(self.download_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        buffer_size = 1024 * 1024
        downloaded_size = 0

        with open(self.file_name, 'wb') as output_file:
            for data_chunk in response.iter_content(chunk_size=buffer_size):
                if data_chunk:
                    output_file.write(data_chunk)
                    downloaded_size += len(data_chunk)
                    if total_size > 0:
                        progress_percentage = int(downloaded_size * 100 / total_size)
                    else:
                        progress_percentage = 0

                    if total_size > 0:
                        self.progress_update.emit(self.app_name, progress_percentage, downloaded_size, total_size, os.path.abspath(self.file_name))
                    else:
                        self.progress_update.emit(self.app_name, "Error", downloaded_size, total_size, os.path.abspath(self.file_name))
        self.download_complete.emit(self.app_name, os.path.abspath(self.file_name))


def load_apps_config():
    with open('C:\\Projects\\Python\\MassFileDownloader\\programs.json', 'r') as config_file:
        return json.load(config_file)


def run_installer(file_path, command_template):
    command = file_path
    subprocess.run(command, shell=True)


class DownloadingWindow(QWidget):
    def __init__(self, app_name, main_window):
        super().__init__()
        self.app_name = app_name
        self.main_window = main_window 
        self.setWindowIcon(QIcon('Photos\\downloading.png'))
        self.initialize_ui()

    def initialize_ui(self):
        global GeometryWindow,xGL,yGL
        self.setWindowTitle('Завантаження...')
        self.setGeometry(xGL, yGL, 400, 250)

        layout = QVBoxLayout()

        self.message_label = QLabel(f'Завантаження {self.app_name}...')
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.download_info_label = QLabel('')
        self.download_info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.download_info_label)

        self.file_path_label = QLabel('')
        self.file_path_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.file_path_label)

        self.setLayout(layout)

    def showEvent(self, event):
        self.main_window.hide()

    def update_progress(self, value, downloaded, total, file_path):
        global total_size
        if total_size == 0:
            self.progress_bar.setVisible(False)
            self.progress_bar.setValue(value)
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.download_info_label.setText(f'Завантажено: {downloaded_mb:.2f} МБ із {total_mb:.2f} МБ')
            self.file_path_label.setText(f'Шлях: {file_path}')
        else:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(value)
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.download_info_label.setText(f'Завантажено: {downloaded_mb:.2f} МБ із {total_mb:.2f} МБ')
            self.file_path_label.setText(f'Шлях: {file_path}')


class FolderSelectionWindow(QWidget):
    folder_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        global file_path,xGL,yGL
        self.setWindowIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\folder1.png'))
        self.setWindowTitle('Вибір папки для файлiв')
        self.setGeometry(xGL, yGL, 400, 150)
        
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()

        self.back_button = QPushButton('')
        self.back_button.clicked.connect(self.backbaton)
        self.back_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\back.png'))
        self.back_button.setToolTip('Назад') 
        self.back_button.setIconSize(QSize(16, 16))
        self.back_button.setFixedSize(30, 30)

        self.back_button.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel('Оберіть папку для завантаження:')

        self.label.setContentsMargins(30, 0, 0, 0)
        if Step != 2:
            top_layout.addWidget(self.back_button)
        top_layout.addWidget(self.label)

        top_layout.setSpacing(0)

        layout.addLayout(top_layout)

        self.select_button = QPushButton('Вибрати папку')
        self.select_button.setToolTip('Вибрати папку для завантаження') 
        self.select_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.select_button)

        self.setLayout(layout)


    def backbaton(self):
        global GeometryWindow,xGL,yGL
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        self.hide()
        self.installer_window = InstallerWindow()
        self.installer_window.show()

    def open_file_dialog(self):
        global file_path
        folder = QFileDialog.getExistingDirectory(self, 'Оберання папки для завантаження:')
        if folder:
            self.folder_selected.emit(folder)
            file_path = folder
            self.close()

class InfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\info1.png'))
        self.setup_ui()
        self.folder_selected = None 

    def setup_ui(self):
        global Step, start_button,xGL,yGL
        Step = 1

        self.setWindowTitle('Iнформація')
        self.setGeometry(800, 400, 400, 200)

        self.layout = QVBoxLayout()
        self.layout1 = QHBoxLayout()

        self.greeting_label = QLabel('Це інсталятор програм!\nЗавантажте та встановіть необхідні програми легко і швидко.', self)
        self.greeting_label.setAlignment(Qt.AlignCenter)
        self.layout1.addWidget(self.greeting_label)

        self.skip_button = QPushButton('', self)
        self.skip_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\skip.png'))
        self.skip_button.setIconSize(QSize(15, 15))
        self.skip_button.setFixedSize(30, 30)
        self.skip_button.setToolTip('Пропустити всi кроки')
        self.skip_button.clicked.connect(self.open_installer)
        self.layout1.addWidget(self.skip_button, alignment=Qt.AlignRight)

        self.layout.addLayout(self.layout1)

        start_button = QPushButton('Далi', self)
        start_button.setFixedSize(350, 40)
        start_button.setEnabled(False)
        start_button.setToolTip('Наступний крок')
        start_button.clicked.connect(self.pred_next_step)
        self.layout.addWidget(start_button, alignment=Qt.AlignCenter)

        self.info_link_label = QLabel('<a href="#" style="color: rgba(216, 222, 233, 0.7); text-decoration: none;">Додаткова інформація</a>', self)
        self.info_link_label.setToolTip('Додаткова інформація про програму')
        self.info_link_label.setAlignment(Qt.AlignCenter)
        self.info_link_label.setOpenExternalLinks(True)
        self.info_link_label.mousePressEvent = self.open_info_html
        self.layout.addWidget(self.info_link_label)

        self.remaining_time_label = QLabel(self)
        self.remaining_time_label.setAlignment(Qt.AlignCenter)
        self.remaining_time_label.setStyleSheet("color: rgba(216, 222, 233, 0.7);")
        self.layout.addWidget(self.remaining_time_label)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.enable_button) 
        self.timer.start(6000)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_remaining_time)
        self.update_timer.start(100)


        self.check_folder_timer = QTimer(self)
        self.check_folder_timer.timeout.connect(self.check_folder_path)
        self.check_folder_timer.start(500) 



    def open_installer(self):
        global GeometryWindow,xGL,yGL
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        self.installer_window = InstallerWindow()
        self.installer_window.show()
        self.close()

    def open_info_html(self, event):
        webbrowser.open('C:\\Projects\\Python\\MassFileDownloader\\info.html')

    def enable_button(self):
        global start_button  
        start_button.setEnabled(True)

    def check_folder_path(self):
        if Step == 2: 
            if self.folder_selected != None:
                start_button.setEnabled(True)
            else:
                start_button.setEnabled(False) 

    def update_remaining_time(self):
        if Step != 2: 
            remaining_time = self.timer.remainingTime()
            if remaining_time > 0:
                self.remaining_time_label.setText(f"{remaining_time // 1000}")
            else:
                if Step == 3:
                    self.remaining_time_label.setText('')
                    self.layout.addWidget(self.remaining_time_label, alignment=Qt.AlignLeft)
                else:
                    self.remaining_time_label.setText('')
                    self.layout1.addWidget(self.remaining_time_label, alignment=Qt.AlignCenter)

    def folder_selected_callback(self, folder_path):
        self.folder_selected = folder_path

    def pred_next_step(self):
        global GeometryWindow,xGL,yGL
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        self.next_step()

    def next_step(self):
        global Step
        Step += 1

        if Step == 2 or Step == 3:
            self.info_link_label.hide()

        if Step == 2:
            self.greeting_label.setText("Крок 2:\nВиберіть папку для встановки файлiв:")
            start_button.setEnabled(False) 
            self.remaining_time_label.setText('')  
            self.layout.addWidget(self.greeting_label, alignment=Qt.AlignCenter)

            self.layout1.addWidget(self.skip_button, alignment=Qt.AlignRight)  

            folder_button = QPushButton('Вибрати папку', self)
            folder_button.setToolTip('Вибрати папку для завантаження')
            folder_button.setFixedSize(350, 40)
            folder_button.clicked.connect(self.open_folder_selection)
            self.layout.addWidget(folder_button, alignment=Qt.AlignCenter) 
            self.layout.addWidget(start_button, alignment=Qt.AlignCenter)
            self.layout.addWidget(self.remaining_time_label, alignment=Qt.AlignCenter)

        elif Step == 3:
            self.greeting_label.setText("Крок 3\nНалаштуйте програму пiд себе")
            start_button.setEnabled(False)

            for i in reversed(range(self.layout.count())):
                widget = self.layout.itemAt(i).widget()
                if isinstance(widget, QPushButton) and widget.text() == 'Вибрати папку':
                    widget.deleteLater()
            settings_button = QPushButton('Вiдкрити налаштування', self)
            settings_button.setToolTip('Вiдкрити налаштування програми')
            settings_button.setFixedSize(350, 40)
            settings_button.clicked.connect(self.open_settings_window)

            self.remaining_time_label.setText('')

            self.layout.addWidget(self.greeting_label, alignment=Qt.AlignCenter)
            self.layout.addWidget(settings_button, alignment=Qt.AlignCenter)
            self.layout.addWidget(start_button, alignment=Qt.AlignCenter)
            self.layout.addWidget(self.remaining_time_label, alignment=Qt.AlignCenter)
            self.layout1.addWidget(self.skip_button, alignment=Qt.AlignRight)

            self.layout.addWidget(self.remaining_time_label, alignment=Qt.AlignCenter)
            self.timer.start(4000)
            self.update_timer.start(100)
        

        elif Step == 4:
            self.open_software()

    def open_installer(self):
        response = QMessageBox.question(self, 'Пропуск', "Ви впевненi що хочете пропустити всi кроки?", QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            self.installer_window = InstallerWindow()
            self.installer_window.show()
            self.close()

    def open_software(self):
        self.installer_window = InstallerWindow()
        self.installer_window.show()
        self.close()


    def open_folder_selection(self):
        self.folder_window = FolderSelectionWindow()
        self.folder_window.folder_selected.connect(self.folder_selected_callback) 
        self.folder_window.show()

    def open_settings_window(self):
        global StepWindow
        StepWindow = True
        self.settings_window = SettingsWindow()
        self.settings_window.show()

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\settings.png'))
        self.initialize_ui()
        self.app_data = load_apps_config()
        self.current_app_index = 0

    def initialize_ui(self):
        global GeometryWindow, xGL, yGL,SetupStart,SitesORInstallWindow1,StepWindow

        self.setWindowTitle('Налаштування')
        self.setGeometry(xGL, yGL, 600, 450)

        button_layout = QHBoxLayout()
        layout = QVBoxLayout()

        self.back_button = QPushButton('')
        self.back_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\back.png'))
        self.back_button.setToolTip('Назад') 
        self.back_button.setIconSize(QSize(16, 16))
        self.back_button.setFixedSize(30, 30)
        self.back_button.clicked.connect(self.backbutton)
        try:
            if StepWindow == True:
                StepWindow = False
            else:
                layout.addWidget(self.back_button)
        except:
            layout.addWidget(self.back_button)

        self.label1 = QLabel("Відкривати всі сетапи зразу")
        self.label1.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label1)

        button_layout.setAlignment(Qt.AlignCenter)
        
        try:
            if SetupStart == True:
                self.galochka_button = QPushButton(self)
                self.galochka_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\galochka.png'))
                self.galochka_button.setIconSize(QSize(25, 25))
                self.galochka_button.setFixedSize(30, 30)
                self.galochka_opacity_effect = QGraphicsOpacityEffect()
                self.galochka_opacity_effect.setOpacity(1)
                self.galochka_button.setGraphicsEffect(self.galochka_opacity_effect)
                self.galochka_button.clicked.connect(self.increase_galochka_opacity)
                button_layout.addWidget(self.galochka_button)

                self.krest_button = QPushButton(self)
                self.krest_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\krest.png'))
                self.krest_button.setIconSize(QSize(25, 25))
                self.krest_button.setFixedSize(30, 30)
                self.krest_opacity_effect = QGraphicsOpacityEffect()
                self.krest_opacity_effect.setOpacity(0.3)
                self.krest_button.setGraphicsEffect(self.krest_opacity_effect)
                self.krest_button.clicked.connect(self.increase_krest_opacity)
                button_layout.addWidget(self.krest_button)
            elif SetupStart == False:
                self.galochka_button = QPushButton(self)
                self.galochka_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\galochka.png'))
                self.galochka_button.setIconSize(QSize(25, 25))
                self.galochka_button.setFixedSize(30, 30)
                self.galochka_opacity_effect = QGraphicsOpacityEffect()
                self.galochka_opacity_effect.setOpacity(0.3)
                self.galochka_button.setGraphicsEffect(self.galochka_opacity_effect)
                self.galochka_button.clicked.connect(self.increase_galochka_opacity)
                button_layout.addWidget(self.galochka_button)

                self.krest_button = QPushButton(self)
                self.krest_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\krest.png'))
                self.krest_button.setIconSize(QSize(25, 25))
                self.krest_button.setFixedSize(30, 30)
                self.krest_opacity_effect = QGraphicsOpacityEffect()
                self.krest_opacity_effect.setOpacity(1)
                self.krest_button.setGraphicsEffect(self.krest_opacity_effect)
                self.krest_button.clicked.connect(self.increase_krest_opacity)
                button_layout.addWidget(self.krest_button)

        except:
            SetupStart = False
            if SetupStart == False:
                self.galochka_button = QPushButton(self)
                self.galochka_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\galochka.png'))
                self.galochka_button.setIconSize(QSize(25, 25))
                self.galochka_button.setFixedSize(30, 30)
                self.galochka_opacity_effect = QGraphicsOpacityEffect()
                self.galochka_opacity_effect.setOpacity(0.3)
                self.galochka_button.setGraphicsEffect(self.galochka_opacity_effect)
                self.galochka_button.clicked.connect(self.increase_galochka_opacity)
                button_layout.addWidget(self.galochka_button)

                self.krest_button = QPushButton(self)
                self.krest_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\krest.png'))
                self.krest_button.setIconSize(QSize(25, 25))
                self.krest_button.setFixedSize(30, 30)
                self.krest_opacity_effect = QGraphicsOpacityEffect()
                self.krest_opacity_effect.setOpacity(1)
                self.krest_button.setGraphicsEffect(self.krest_opacity_effect)
                self.krest_button.clicked.connect(self.increase_krest_opacity)
                button_layout.addWidget(self.krest_button)



        # self.label2 = QLabel("Інший текст для другої кнопки")
        # self.label2.setAlignment(Qt.AlignCenter)
        # layout.addWidget(self.label2)

        # button_layout.setAlignment(Qt.AlignCenter)

        # self.galochka_button1 = QPushButton(self)
        # self.galochka_button1.setIcon(QIcon('Photos/galochka.png'))
        # self.galochka_button1.setIconSize(QSize(25, 25))
        # self.galochka_button1.setFixedSize(30, 30)
        # self.galochka_opacity_effect1 = QGraphicsOpacityEffect()
        # self.galochka_opacity_effect1.setOpacity(0.3)
        # self.galochka_button1.setGraphicsEffect(self.galochka_opacity_effect1)
        # self.galochka_button1.clicked.connect(self.increase_galochka_opacity1)
        # button_layout.addWidget(self.galochka_button1)

        # self.krest_button1 = QPushButton(self)
        # self.krest_button1.setIcon(QIcon('Photos/krest.png'))
        # self.krest_button1.setIconSize(QSize(25, 25))
        # self.krest_button1.setFixedSize(30, 30)
        # self.krest_opacity_effect1 = QGraphicsOpacityEffect()
        # self.krest_opacity_effect1.setOpacity(1)
        # self.krest_button1.setGraphicsEffect(self.krest_opacity_effect1)
        # self.krest_button1.clicked.connect(self.increase_krest_opacity1)
        # button_layout.addWidget(self.krest_button1)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def backbutton(self):
        global GeometryWindow,xGL,yGL,SitesORInstallWindow1
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        self.hide()
        if SitesORInstallWindow1 == "InstallerWindow":
            self.info_window = InstallerWindow()
            self.info_window.show()
        else:
            self.info_window = SitesWindow()
            self.info_window.show()

    def increase_krest_opacity1(self):
        self.krest_opacity_effect1.setOpacity(1)
        self.galochka_opacity_effect1.setOpacity(0.3)

    def increase_galochka_opacity1(self):
        self.galochka_opacity_effect1.setOpacity(1)
        self.krest_opacity_effect1.setOpacity(0.3)

    def increase_krest_opacity(self):
        global SetupStart
        SetupStart = False
        self.krest_opacity_effect.setOpacity(1)
        self.galochka_opacity_effect.setOpacity(0.3)

    def increase_galochka_opacity(self):
        global SetupStart
        SetupStart = True
        self.galochka_opacity_effect.setOpacity(1)
        self.krest_opacity_effect.setOpacity(0.3)



class SitesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\sites.png'))
        self.initialize_ui()
        self.app_data = load_apps_config()
        self.current_app_index = 0

    def initialize_ui(self):
        global xGL,yGL
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
    

        self.setWindowTitle('Сайти драйверiв')
        self.setGeometry(xGL, yGL, 600, 450)

        settings_button = QPushButton('', self)
        settings_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\menu.png'))
        settings_button.setIconSize(QSize(25, 25))
        settings_button.setFixedSize(30, 30)
        settings_button.setToolTip('Меню') 
        settings_button.clicked.connect(self.toggle_settings_menu)


        button_layout.addWidget(settings_button, alignment=Qt.AlignTop)

        self.instruction_label = QLabel('Оберіть сайт на який ви хочете перейти:', self)
        self.instruction_label.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(self.instruction_label)


        nvidia_button = QPushButton('NVIDIA', self)
        nvidia_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\nvidia.png'))
        nvidia_button.setToolTip('Сайт NVIDIA')
        amd_button = QPushButton('AMD', self)
        amd_button.setToolTip('Сайт AMD')
        amd_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\amd.png'))
        
        intel_button = QPushButton('INTEL', self)
        intel_button.setToolTip('Сайт INTEL')
        intel_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\intel.png'))

        amd_button.clicked.connect(self.open_amd_site)
        nvidia_button.clicked.connect(self.open_nvidia_site)

        self.nonn = QLabel('', self)
        self.nonn.setAlignment(Qt.AlignCenter)

        layout.addLayout(button_layout)
        layout.addWidget(amd_button)
        layout.addWidget(intel_button)
        layout.addWidget(nvidia_button)
        layout.addWidget(self.nonn)
        self.setLayout(layout)

        self.settings_menu = QWidget(self)
        self.settings_menu.setGeometry(0, 0, 150, self.height())

        self.settings_menu.setStyleSheet("""
            background-color: #3A4555;
        """)

        settings_layout = QVBoxLayout(self.settings_menu)
        back_button = QPushButton('', self.settings_menu)
        back_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\back.png'))
        back_button.setIconSize(QSize(16, 16))
        back_button.setFixedSize(30, 30)
        back_button.setToolTip('Назад')
        back_button.clicked.connect(self.toggle_settings_menu)
        settings_layout.addWidget(back_button,alignment=Qt.AlignLeft)

        settings_layout = self.settings_menu.layout()

        settings_button = QPushButton('Програми', self.settings_menu)
        settings_button.setToolTip('Вiкно з програмами')
        settings_button.clicked.connect(self.backbaton)


        line = QFrame(self.settings_menu)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: white;")
        line.setFixedHeight(5) 

        settings_layout.addWidget(settings_button)
        settings_layout.addWidget(line)


        none_label = QLabel('', self.settings_menu)
        none_label.setAlignment(Qt.AlignCenter)
        none_label.setStyleSheet("color: black;")
        settings_layout.addWidget(none_label)       

        info_button = QPushButton('', self.settings_menu)
        info_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\info1.png'))
        info_button.setIconSize(QSize(16, 16))
        info_button.setFixedSize(30, 30)
        info_button.setToolTip('Iнформацiя')
        info_button.clicked.connect(self.info_open_window)
        settings_layout.addWidget(info_button,alignment=Qt.AlignLeft)

        settings_button = QPushButton('', self.settings_menu)
        settings_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\settings.png')) 
        settings_button.setIconSize(QSize(16, 16))
        settings_button.setFixedSize(30, 30)
        settings_button.setToolTip('Налаштування')
        settings_button.clicked.connect(self.open_settings_window)
        settings_layout.addWidget(settings_button,alignment=Qt.AlignLeft)

        folder_button = QPushButton('', self.settings_menu)
        folder_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\folder.png'))
        folder_button.setIconSize(QSize(16, 16))
        folder_button.setFixedSize(30, 30)
        folder_button.setToolTip('Вибір папки для завантаження')
        folder_button.clicked.connect(self.open_folder_selection2)
        settings_layout.addWidget(folder_button,alignment=Qt.AlignLeft)

        exit_button = QPushButton('', self.settings_menu)
        exit_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\exit.png'))
        exit_button.setIconSize(QSize(16, 16))
        exit_button.setFixedSize(30, 30)
        exit_button.setToolTip('Вийти з програми') 
        exit_button.clicked.connect(self.close)
        settings_layout.addWidget(exit_button,alignment=Qt.AlignLeft)

        self.settings_menu.setLayout(settings_layout)
        self.settings_menu.setVisible(False)

    def open_folder_selection2(self):
        global GeometryWindow,xGL,yGL
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        self.folder_selection_window = FolderSelectionWindow()
        self.folder_selection_window.folder_selected.connect(self.folder_selected2)
        self.folder_selection_window.show()
        self.hide()

    def open_settings_window(self):
        import re
        global GeometryWindow,xGL,yGL,SitesORInstallWindow1
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        match = re.search(r'<__main__\.(\w+) object at', str(self))
        if match.group(1) == "InstallerWindow":
            SitesORInstallWindow1 = "InstallerWindow"
        else:
            SitesORInstallWindow1 = "SitesWindow"
        self.installer_window = SettingsWindow()
        self.installer_window.show()
        self.hide()


    def info_open_window(self):
        import re
        global GeometryWindow,xGL,yGL,SitesORInstallWindow
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        match = re.search(r'<__main__\.(\w+) object at', str(self))
        if match.group(1) == "InstallerWindow":
            SitesORInstallWindow = "InstallerWindow"
        else:
            SitesORInstallWindow = "SitesWindow"
        self.hide()
        self.info_window = InformationWindow()
        self.info_window.show()

    def open_amd_site(self):
        QDesktopServices.openUrl(QUrl('https://www.amd.com/en/support/download/drivers.html'))

    def open_nvidia_site(self):
        QDesktopServices.openUrl(QUrl('https://www.nvidia.com/ru-ru/drivers/'))
    def open_intel_site(self):
        QDesktopServices.openUrl(QUrl('https://www.intel.com/content/www/us/en/download-center/home.html'))

    def toggle_settings_menu(self):
        self.settings_menu.setVisible(not self.settings_menu.isVisible())

    def sites_open_window(self):
        self.hide()
        self.siteswindow = SitesWindow()
        self.siteswindow.show()

    def backbaton(self):
        global GeometryWindow,xGL,yGL
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        self.hide()
        self.installer_window = InstallerWindow()
        self.installer_window.show()

class InformationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\info1.png'))
        self.setup_ui()

    def setup_ui(self):
        global xGL,yGL,SitesORInstallWindow
        self.setWindowTitle('Iнформація')
        self.setGeometry(xGL, yGL, 400, 250)

        layout = QVBoxLayout()

        info_text = (
            'Це інсталятор програм! Завантажте та встановіть необхідні програми легко і швидко.\n\n'
            'Факти про програму:\n'
            '• Ця програма інсталятор зроблена одним розробником.\n'
            '• Простий і зрозумілий інтерфейс.'
        )

        info_label = QLabel(info_text, self)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        close_button = QPushButton('Закрити', self)
        close_button.clicked.connect(self.HideInfo)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def HideInfo(self):
        global GeometryWindow,xGL,yGL,SitesORInstallWindow
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        self.hide()
        if SitesORInstallWindow == "InstallerWindow":
            self.info_window = InstallerWindow()
            self.info_window.show()
        else:
            self.info_window = SitesWindow()
            self.info_window.show()

class InstallerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\main.png'))
        self.initialize_ui()
        self.app_data = load_apps_config()
        self.current_app_index = 0

    def initialize_ui(self):
        global GeometryWindow,xGL,yGL
        self.setWindowTitle('Встановщiк програм')
        try:
            self.setGeometry(xGL, yGL, 600, 450)
        except NameError:
            self.setGeometry(300, 100, 600, 450)

        layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        settings_button = QPushButton('', self)
        settings_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\menu.png'))
        settings_button.setIconSize(QSize(25, 25))
        settings_button.setFixedSize(30, 30)
        settings_button.setToolTip('Меню') 
        settings_button.clicked.connect(self.toggle_settings_menu)
        button_layout.addWidget(settings_button)

        select_all_button = QPushButton('Вибрати всі', self)
        select_all_button.setFixedSize(250, 30)
        select_all_button.setToolTip('Вибрати всі файли') 
        select_all_button.clicked.connect(self.select_all_apps)
        button_layout.addWidget(select_all_button)

        deselect_all_button = QPushButton('Прибрати всi', self)
        deselect_all_button.setFixedSize(250, 30)
        deselect_all_button.setToolTip('Прибрати всi файли') 
        deselect_all_button.clicked.connect(self.unselect_all_apps)
        button_layout.addWidget(deselect_all_button)

        layout.addLayout(button_layout)

        self.instruction_label = QLabel('Оберіть програми для встановки:', self)
        self.instruction_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.instruction_label)

        self.app_list_widget = QListWidget()
        self.app_list_widget.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.app_list_widget)

        self.populate_app_list()

        install_button = QPushButton('Встановити обрані програми')
        install_button.clicked.connect(self.open_folder_selection)
        layout.addWidget(install_button)

        self.setLayout(layout)

        self.settings_menu = QWidget(self)
        self.settings_menu.setGeometry(0, 0, 150, self.height())

        settings_layout = QVBoxLayout(self.settings_menu)
        
        back_button = QPushButton('', self.settings_menu)
        back_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\back.png'))
        back_button.setIconSize(QSize(16, 16))
        back_button.setFixedSize(30, 30)
        back_button.setToolTip('Назад')
        back_button.clicked.connect(self.toggle_settings_menu)
        settings_layout.addWidget(back_button,alignment=Qt.AlignLeft)

        settings_layout = self.settings_menu.layout()

        settings_button = QPushButton('Сайти', self.settings_menu)
        settings_button.setToolTip('Сайти з драйверами')
        settings_button.clicked.connect(self.sites_open_window)


        line = QFrame(self.settings_menu)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: white;")
        line.setFixedHeight(5) 

        settings_layout.addWidget(settings_button)
        settings_layout.addWidget(line)


        none_label = QLabel('', self.settings_menu)
        none_label.setAlignment(Qt.AlignCenter)
        none_label.setStyleSheet("color: black;")
        settings_layout.addWidget(none_label)       

        info_button = QPushButton('', self.settings_menu)
        info_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\info1.png'))
        info_button.setIconSize(QSize(16, 16))
        info_button.setFixedSize(30, 30)
        info_button.setToolTip('Iнформацiя')
        info_button.clicked.connect(self.info_open_window)
        settings_layout.addWidget(info_button,alignment=Qt.AlignLeft)

        settings_button = QPushButton('', self.settings_menu)
        settings_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\settings.png')) 
        settings_button.setIconSize(QSize(16, 16))
        settings_button.setFixedSize(30, 30)
        settings_button.setToolTip('Налаштування')
        settings_button.clicked.connect(self.open_settings_window)
        settings_layout.addWidget(settings_button,alignment=Qt.AlignLeft)

        folder_button = QPushButton('', self.settings_menu)
        folder_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\folder.png'))
        folder_button.setIconSize(QSize(16, 16))
        folder_button.setFixedSize(30, 30)
        folder_button.setToolTip('Вибір папки для завантаження')
        folder_button.clicked.connect(self.open_folder_selection2)
        settings_layout.addWidget(folder_button,alignment=Qt.AlignLeft)

        exit_button = QPushButton('', self.settings_menu)
        exit_button.setIcon(QIcon('C:\\Projects\\Python\\MassFileDownloader\\Photos\\exit.png'))
        exit_button.setIconSize(QSize(16, 16))
        exit_button.setFixedSize(30, 30)
        exit_button.setToolTip('Вийти з програми') 
        exit_button.clicked.connect(self.close)
        settings_layout.addWidget(exit_button,alignment=Qt.AlignLeft)

        self.settings_menu.setLayout(settings_layout)
        self.settings_menu.setVisible(False)


    def sites_open_window(self):
        global GeometryWindow,xGL,yGL
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        self.hide()
        self.siteswindow = SitesWindow()
        self.siteswindow.show()

    def info_open_window(self):
        import re
        global GeometryWindow,xGL,yGL,SitesORInstallWindow
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        match = re.search(r'<__main__\.(\w+) object at', str(self))
        if match.group(1) == "InstallerWindow":
            SitesORInstallWindow = "InstallerWindow"
        else:
            SitesORInstallWindow = "SitesWindow"
        self.hide()
        self.info_window = InformationWindow()
        self.info_window.show()


    def open_folder_selection2(self):
        global GeometryWindow,xGL,yGL
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        self.folder_selection_window = FolderSelectionWindow()
        self.folder_selection_window.folder_selected.connect(self.folder_selected2)
        self.folder_selection_window.show()
        self.hide()

    def folder_selected2(self,file_path):
        QMessageBox.information(self, 'Вибір папки', f"Папка успішно обрана!\nШлях папки:{file_path}")
        self.folder_selection_window.hide()
        self.show()
        return file_path

    def open_settings_window(self):
        import re
        global GeometryWindow,xGL,yGL,SitesORInstallWindow1
        GeometryWindow = self.geometry()
        geometry_str = str(self.geometry())
        rect_values = geometry_str.replace('PyQt5.QtCore.QRect(', '').replace(')', '').split(', ')
        xGL = int(rect_values[0])
        yGL = int(rect_values[1]) 
        match = re.search(r'<__main__\.(\w+) object at', str(self))
        if match.group(1) == "InstallerWindow":
            SitesORInstallWindow1 = "InstallerWindow"
        else:
            SitesORInstallWindow1 = "SitesWindow"
        self.installer_window = SettingsWindow()
        self.installer_window.show()
        self.hide()

    def toggle_settings_menu(self):
        self.settings_menu.setVisible(not self.settings_menu.isVisible())



    def populate_app_list(self):
        apps = load_apps_config()
        for app_name in apps.keys():
            icon_path = f"C:\\Projects\\Python\\MassFileDownloader\\Photos\\{app_name.lower()}.png"
            icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
            item = QListWidgetItem(icon, app_name)
            self.app_list_widget.addItem(item)

    def select_all_apps(self):
        for i in range(self.app_list_widget.count()):
            item = self.app_list_widget.item(i)
            item.setSelected(True)

    def unselect_all_apps(self):
        for i in range(self.app_list_widget.count()):
            item = self.app_list_widget.item(i)
            item.setSelected(False)

    def start_downloads(self,file_path):
        self.download_directory = file_path
        self.current_app_index = 0
        self.download_next_app()

    def download_next_app(self):
        if self.current_app_index >= len(self.selected_apps):
            QMessageBox.information(self, 'Встановка завершена', "Всі програми встановлено.")
            self.show()
            return

        app_name = self.selected_apps[self.current_app_index]
        app_info = self.app_data[app_name]

        self.downloading_window = DownloadingWindow(app_name, self)
        self.downloading_window.show()
        self.hide()

        if app_name in ["Epic Games Laucher", "SQLite"]:
            file_name = os.path.join(self.download_directory, f"{app_info['original_name']}")
        else:
            file_name = os.path.join(self.download_directory, f"{app_name}.exe")

        self.download_thread = DownloadThread(app_name, app_info['url'], file_name)
        self.download_thread.progress_update.connect(self.update_download_progress)
        self.download_thread.download_complete.connect(self.on_download_finished)
        self.download_thread.start()


    def open_folder_selection(self):
        selected_items = self.app_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Помилка!', 'Виберіть хоча б одну програму для встановки.')
            return

        self.selected_apps = [item.text() for item in selected_items]

        try:
            self.start_downloads(file_path)
            self.hide()
        except NameError:
            QMessageBox.warning(self, 'Помилка!', f"Для початку завантаження виберiть папку!\nЦе можна зробити в налаштуваннях.")
            self.show()
            self.unselect_all_apps()
            return

    def update_download_progress(self, app_name, progress, downloaded, total, file_path):
        self.downloading_window.update_progress(progress, downloaded, total, file_path)

    def on_download_finished(self, app_name, file_path):
        global SetupStart
        self.downloading_window.close()
        try:
            if SetupStart == True:
                run_installer(file_path, self.app_data[app_name])
        except NameError:
            SetupStart = False

        self.current_app_index += 1
        self.download_next_app()


if __name__ == "__main__":
    app = QApplication([])

    # Определяем базовый путь, чтобы корректно находить style.css в скомпилированном .exe
    if getattr(sys, 'frozen', False):
        # Если программа скомпилирована в .exe
        base_path = sys._MEIPASS
    else:
        # Если программа запускается как скрипт
        base_path = os.path.abspath(".")

    # Указываем путь к файлу style.css
    style_path = os.path.join(base_path, "style.css")
    
    # Читаем и применяем стиль, если файл найден
    if os.path.exists(style_path):
        with open(style_path, "r") as style:
            app.setStyleSheet(style.read())
    else:
        print(f"Файл стилей {style_path} не найден.")

    # Запускаем главное окно
    main_window = InfoWindow()
    main_window.show()
    app.exec_()
