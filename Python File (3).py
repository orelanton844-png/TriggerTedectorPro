import os
import sys
import time
import json
import shutil
import threading
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
import subprocess
import schedule  # Добавляем библиотеку для планирования задач

# Проверка и установка зависимостей
def check_and_install_dependencies():
    required_packages = {
        'Pillow': 'pillow',
        'pyautogui': 'pyautogui',
        'opencv-python': 'opencv-python',
        'numpy': 'numpy',
        'schedule': 'schedule'  # Добавляем schedule для планирования задач
    }
    
    missing_packages = []
    
    for package_name, pip_name in required_packages.items():
        try:
            __import__(package_name.lower().replace('-', '_'))
            print(f"✅ {package_name} уже установлен")
        except ImportError:
            missing_packages.append(pip_name)
            print(f"❌ {package_name} не найден")
    
    if missing_packages:
        print(f"\n⚠️ Установка недостающих пакетов: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("✅ Пакеты успешно установлены!")
        except Exception as e:
            print(f"❌ Ошибка установки: {e}")
            print("\nУстановите вручную:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

# Проверяем зависимости
if not check_and_install_dependencies():
    print("⚠️ Продолжаем с доступными пакетами...")

# Импортируем установленные библиотеки
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageGrab, ImageTk
    import pyautogui
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    import winsound
    import schedule  # Импортируем schedule
    print("✅ Все библиотеки загружены успешно!")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    input("Нажмите Enter для выхода...")
    sys.exit(1)

class TriggerDetectorPro:
    def __init__(self):
        # Инициализируем переменные ДО load_triggers_from_folder
        self.trigger_images = {}
        self.group1_triggers = []
        self.group2_trigger = None
        self.group3_trigger = None
        self.group4_triggers = []  # Теперь группа 4 имеет 20 триггеров
        self.group5_triggers = []  # Теперь группа 5 имеет только 1 триггер вместо 20
        self.group6_triggers = []  # Группа 6 - 8 триггеров (каждый загружается отдельно)
        
        # Инициализируем total_clicks_performed перед setup_gui
        self.total_clicks_performed = 0
        
        self.setup_directories()
        self.load_triggers_from_folder()
        self.load_config()
        self.init_variables()
        self.setup_gui()
        self.setup_password_settings_tab()
        
    def load_triggers_from_folder(self):
        """Загружает триггеры из папки при запуске"""
        triggers_dir = Path(__file__).parent / 'triggers'
        if triggers_dir.exists():
            try:
                print(f"🔍 Поиск триггеров в папке: {triggers_dir}")
                
                # Загружаем триггеры группы 1 (15 триггеров)
                for i in range(1, 16):
                    trigger_key = f'group1_trigger{i:02d}'
                    trigger_files = list(triggers_dir.glob(f"group1_{i:02d}.*"))
                    trigger_files.extend(list(triggers_dir.glob(f"group1_trigger{i:02d}.*")))
                    trigger_files.extend(list(triggers_dir.glob(f"g1_{i}.*")))
                    
                    if trigger_files:
                        file_path = trigger_files[0]
                        if self.process_trigger_file(trigger_key, file_path):
                            if trigger_key not in self.group1_triggers:
                                self.group1_triggers.append(trigger_key)
                            print(f"✅ Загружен триггер группы 1: {file_path.name}")
                
                # Загружаем триггеры группы 4 (20 триггеров)
                for i in range(1, 21):
                    trigger_key = f'group4_trigger{i:02d}'
                    trigger_files = list(triggers_dir.glob(f"group4_{i:02d}.*"))
                    trigger_files.extend(list(triggers_dir.glob(f"group4_trigger{i:02d}.*")))
                    trigger_files.extend(list(triggers_dir.glob(f"g4_{i}.*")))
                    
                    if trigger_files:
                        file_path = trigger_files[0]
                        if self.process_trigger_file(trigger_key, file_path):
                            if trigger_key not in self.group4_triggers:
                                self.group4_triggers.append(trigger_key)
                            print(f"✅ Загружен триггер группы 4: {file_path.name}")
                
                # Загружаем триггер группы 5 (ТОЛЬКО 1 триггер вместо 20)
                for i in range(1, 2):  # Изменено с range(1, 21) на range(1, 2)
                    trigger_key = f'group5_trigger{i:02d}'
                    trigger_files = list(triggers_dir.glob(f"group5_{i:02d}.*"))
                    trigger_files.extend(list(triggers_dir.glob(f"group5_trigger{i:02d}.*")))
                    trigger_files.extend(list(triggers_dir.glob(f"g5_{i}.*")))
                    
                    if trigger_files:
                        file_path = trigger_files[0]
                        if self.process_trigger_file(trigger_key, file_path):
                            if trigger_key not in self.group5_triggers:
                                self.group5_triggers.append(trigger_key)
                            print(f"✅ Загружен триггер группы 5: {file_path.name}")
                
                # Загружаем триггеры группы 6 (8 триггеров) - каждый загружается отдельно
                for i in range(1, 9):  # Изменено с range(1, 6) на range(1, 9)
                    trigger_key = f'group6_trigger{i:02d}'
                    trigger_files = list(triggers_dir.glob(f"group6_{i:02d}.*"))
                    trigger_files.extend(list(triggers_dir.glob(f"group6_trigger{i:02d}.*")))
                    trigger_files.extend(list(triggers_dir.glob(f"g6_{i}.*")))
                    
                    if trigger_files:
                        file_path = trigger_files[0]
                        if self.process_trigger_file(trigger_key, file_path):
                            if trigger_key not in self.group6_triggers:
                                self.group6_triggers.append(trigger_key)
                            print(f"✅ Загружен триггер группы 6: {file_path.name}")
                
                # Загружаем одиночные триггеры других групп
                single_triggers = [
                    ('group2_trigger.png', 'group2_trigger', 'group2'),
                    ('group3_trigger.png', 'group3_trigger', 'group3')
                ]
                
                for filename, trigger_key, group_name in single_triggers:
                    trigger_files = list(triggers_dir.glob(filename))
                    if trigger_files:
                        file_path = trigger_files[0]
                        if self.process_trigger_file(trigger_key, file_path):
                            if group_name == 'group2':
                                self.group2_trigger = trigger_key
                            elif group_name == 'group3':
                                self.group3_trigger = trigger_key
                            print(f"✅ Загружен триггер {group_name}: {file_path.name}")
                
                print(f"📁 Всего загружено триггеров: {len(self.trigger_images)}")
                
            except Exception as e:
                print(f"⚠️ Ошибка загрузки триггеров из папки: {e}")
        else:
            print("ℹ️ Папка триггеров не существует, будет создана позже")
        
    def safe_mkdir(self, path):
        """Безопасное создание папки"""
        try:
            path.mkdir(exist_ok=True, parents=True)
            return True
        except Exception as e:
            print(f"❌ Ошибка создания папки {path}: {e}")
            return False
        
    def setup_directories(self):
        """Создает все необходимые папки автоматически"""
        self.base_dir = Path(__file__).parent
        
        # Список всех необходимых папок
        all_dirs = {
            'triggers': self.base_dir / 'triggers',
            'screenshots': self.base_dir / 'screenshots',
            'logs': self.base_dir / 'logs',
            'config': self.base_dir / 'config',
            'backups': self.base_dir / 'backups',
            'recovery_images': self.base_dir / 'recovery_images',
            'internal_triggers': self.base_dir / 'internal_triggers',
            'action_logs': self.base_dir / 'action_logs',
            'schedule_configs': self.base_dir / 'schedule_configs',
            'data': self.base_dir / 'data',
            'temp': self.base_dir / 'temp',
            'cache': self.base_dir / 'cache'
        }
        
        self.dirs = {}
        
        for dir_name, dir_path in all_dirs.items():
            if self.safe_mkdir(dir_path):
                self.dirs[dir_name] = dir_path
                print(f"✅ Папка создана: {dir_path}")
        
        # Создаем папку на рабочем столе для скриншотов сетки
        desktop_paths = [
            Path.home() / 'Desktop',
            Path.home() / 'Рабочий стол',
            Path.home() / 'Desktop (Оrel2)',
            Path.home(),
            self.base_dir
        ]
        
        grid_screenshots_dir = None
        for desktop_path in desktop_paths:
            try:
                if desktop_path.exists():
                    grid_screenshots_dir = desktop_path / 'Grid_Screenshots'
                    if self.safe_mkdir(grid_screenshots_dir):
                        print(f"✅ Папка создана: {grid_screenshots_dir}")
                        break
            except Exception as e:
                print(f"⚠️ Не удалось использовать путь {desktop_path}: {e}")
                continue
        
        if grid_screenshots_dir and grid_screenshots_dir.exists():
            self.dirs['grid_screenshots'] = grid_screenshots_dir
        else:
            grid_screenshots_dir = self.base_dir / 'Grid_Screenshots'
            self.safe_mkdir(grid_screenshots_dir)
            self.dirs['grid_screenshots'] = grid_screenshots_dir
        
        print(f"📁 Всего создано {len(self.dirs)} папок")
    
    def load_config(self):
        """Загружает или создает конфигурационный файл"""
        self.config_file = self.dirs['config'] / 'config.json'
        
        # Координаты для автоматических кликов каждые 12 часов (4 клика в каждом окне)
        auto_clicks_config = [
            {'x': 100, 'y': 100},   # Клик 1
            {'x': 200, 'y': 200},   # Клик 2
            {'x': 300, 'y': 300},   # Клик 3
            {'x': 400, 'y': 400}    # Клик 4
        ]
        
        # Координаты для разнообразных действий - ИЗМЕНЕНО: теперь 5 действий вместо 7
        action_config = [
            {'type': 'action1_single_click', 'x': 200, 'y': 200, 'chance': 20},
            {'type': 'action2_four_single_clicks', 'clicks': [
                {'x': 300, 'y': 300},  # Клик 1
                {'x': 320, 'y': 320},  # Клик 2
                {'x': 340, 'y': 340},  # Клик 3
                {'x': 360, 'y': 360}   # Клик 4
            ], 'chance': 20},
            {'type': 'action3_nine_clicks', 'clicks': [  # ИЗМЕНЕНО: теперь 9 отдельных кликов
                {'x': 400, 'y': 400, 'type': 'click'},  # Клик 1
                {'x': 420, 'y': 420, 'type': 'click'},  # Клик 2
                {'x': 440, 'y': 440, 'type': 'click'},  # Клик 3
                {'x': 460, 'y': 460, 'type': 'click'},  # Клик 4
                {'x': 480, 'y': 480, 'type': 'click'},  # Клик 5
                {'x': 500, 'y': 500, 'type': 'click'},  # Клик 6
                {'x': 520, 'y': 520, 'type': 'click'},  # Клик 7
                {'x': 540, 'y': 540, 'type': 'click'},  # Клик 8
                {'x': 560, 'y': 560, 'type': 'click'}   # Клик 9
            ], 'chance': 15},
            {'type': 'action4_joystick_random_fixed', 'joystick_start_x': 350, 'joystick_start_y': 350, 
             'distance': 100, 'duration': 2.0, 'click_x': 450, 'click_y': 450, 'chance': 15},
            # НОВОЕ ДЕЙСТВИЕ 5: Джойстик 45-135 градусов + двойной клик
            {'type': 'action5_joystick_random_double_click', 'joystick_start_x': 350, 'joystick_start_y': 350,
             'distance': 100, 'duration_min': 1.0, 'duration_max': 3.0,
             'click_x': 450, 'click_y': 450, 'chance': 15}
        ]
        
        # Настройки временных интервалов
        schedule_config = {
            'action_periods': [
                {'start_minute': 0, 'end_minute': 15, 'mode': 'actions_only'},  # 0-15 мин: только действия
                {'start_minute': 15, 'end_minute': 25, 'mode': 'recovery_only'},  # 15-25 мин: только восстановление
                {'start_minute': 25, 'end_minute': 40, 'mode': 'actions_only'},  # 25-40 мин: только действия
                {'start_minute': 40, 'end_minute': 60, 'mode': 'recovery_only'}  # 40-60 мин: только восстановление
            ],
            'current_mode': 'actions_only',  # Текущий режим
            'last_mode_change': None,
            'mode_check_interval': 60  # Проверять каждую минуту
        }
        
        default_config = {
            # Пороги для групп триггеров
            'threshold_group1': 0.65,
            'threshold_group2': 0.65,
            'threshold_group3': 0.65,
            'threshold_group4': 0.65,
            'threshold_group5': 0.65,
            'threshold_group6': 0.65,
            
            # КУЛДАУН ДЛЯ ГРУППЫ 1 ПОСЛЕ СРАБАТЫВАНИЯ ГРУППЫ 4 - ИЗМЕНЕНО
            'group1_cooldown_after_group4': 180,  # 3 минуты после срабатывания группы 4
            
            'check_interval': 3,
            'sound_alerts': True,
            'auto_save_screenshots': True,
            'monitor_all_windows': True,
            'log_level': 'detailed',
            
            # НОВАЯ НАСТРОЙКА: скорость работы скрипта
            'script_speed': {
                'detection_speed': 1.0,  # Коэффициент скорости детекции (1.0 = нормальная)
                'action_speed': 1.0,     # Коэффициент скорости действий
                'recovery_speed': 1.0,   # Коэффициент скорости восстановления
                'min_delay': 0.05,       # Минимальная задержка
                'max_delay': 0.5         # Максимальная задержка
            },

            # Настройки скорости ввода пароля
            'password_input_settings': {
                'delay_before_password': 0.2,    # Задержка перед вводом пароля (сек)
                'delay_between_chars': 0.1,      # Задержка между символами пароля (сек)
                'min_delay_variation': 0.05,     # Минимальная вариация задержки
                'max_delay_variation': 0.15      # Максимальная вариация задержки
            },
            
            # НОВЫЕ НАСТРОЙКИ КООРДИНАТ ДЛЯ КАЖДОЙ ГРУППЫ
            'group1_clicks': [
                {'x': 100, 'y': 100},   # Первый клик
                {'x': 150, 'y': 150}    # Второй клик
            ],
            'group2_click': {'x': 100, 'y': 100},  # Один клик
            'group3_click': {'x': 100, 'y': 100},  # Один клик
            'group4_click': {'x': 100, 'y': 100},  # Один клик для всех 20 триггеров
            'group5_trigger': {  # КЛИК + ПАРОЛЬ + КЛИК
                'first_click': {'x': 100, 'y': 100},  # Первый клик
                'password': 'password01',  # Пароль
                'second_click': {'x': 150, 'y': 150}  # Второй клик
            },
            'group6_clicks': [  # 5 РАЗНЫХ КЛИКОВ
                {'x': 100, 'y': 100},   # Клик 1
                {'x': 120, 'y': 120},   # Клик 2
                {'x': 140, 'y': 140},   # Клик 3
                {'x': 160, 'y': 160},   # Клик 4
                {'x': 180, 'y': 180}    # Клик 5
            ],
            
            # Координаты для автоматических кликов каждые 12 часов
            'auto_clicks_config': auto_clicks_config,
            
            # Настройки автоматических кликов
            'auto_clicks_settings': {
                'enabled': True,
                'first_time': '12:00',      # Первое время выполнения
                'second_time': '00:00',     # Второе время выполнения (полночь)
                'check_before_clicks': True, # Проверять окна перед кликами
                'wait_for_no_triggers': 30   # Ждать до 30 секунд отсутствия триггеров
            },
            
            # Настройки разнообразных действий - ИЗМЕНЕНО: теперь 5 действий
            'action_settings': {
                'enabled': True,
                'actions': action_config,
                'action_interval': 2,  # Интервал между действиями в секундах
                'min_execution_time': 0.5,  # Минимальное время выполнения действия
                'max_execution_time': 1.5,  # Максимальное время выполнения действия
                'random_delay': True,  # Добавлять случайные задержки
                'enabled_actions': [True, True, True, True, True],  # Какие действия включены (5 действий)
                'random_order': True,  # Выполнять действия в случайном порядке
                'window_order': 'sequential'  # Порядок окон: sequential (последовательно), random (случайно)
            },
            
            # Настройки временного расписания
            'schedule_settings': schedule_config,
            
            'grid_settings': {
                'rows': 5,
                'columns': 6,
                'window_width': 800,
                'window_height': 600,
                'start_x': 50,
                'start_y': 50,
                'gap_x': 10,
                'gap_y': 10
            },
            
            # НОВЫЕ НАСТРОЙКИ ОТДЫХА ПОСЛЕ ВОССТАНОВЛЕНИЯ ОКОН - ИЗМЕНЕНО
            'rest_settings': {
                'enabled': True,
                'windows_before_rest': 10,  # Количество восстановленных окон перед отдыхом
                'rest_duration': 15,
                'pause_monitoring': True,  # Полная приостановка мониторинга во время отдыха
                'stop_actions': True,      # Остановка действий во время отдыха
                'stop_recovery': True      # Остановка восстановления во время отдыха
            },
            
            # Оптимизация для предотвращения зависаний
            'optimization': {
                'max_concurrent_recoveries': 3,
                'memory_cleanup_interval': 50,
                'skip_frames_on_busy': 2,
                'thread_timeout': 30
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                print("✅ Конфигурация загружена")
                
                self.config = self.update_config_structure(loaded_config, default_config)
                self.save_config()
            except Exception as e:
                print(f"❌ Ошибка загрузки конфигурации: {e}")
                self.config = default_config
                self.save_config()
        else:
            self.config = default_config
            self.save_config()
    
    def update_config_structure(self, loaded_config, default_config):
        """Обновляет структуру конфигурации"""
        for key in default_config:
            if key not in loaded_config:
                loaded_config[key] = default_config[key]
        
        # Гарантируем правильную структуру rest_settings
        if 'rest_settings' not in loaded_config or not isinstance(loaded_config['rest_settings'], dict):
            loaded_config['rest_settings'] = default_config['rest_settings'].copy()
        
        # Проверяем все поля в rest_settings
        for subkey in default_config['rest_settings']:
            if subkey not in loaded_config['rest_settings']:
                loaded_config['rest_settings'][subkey] = default_config['rest_settings'][subkey]
        
        # Гарантируем наличие настроек для группы 5
        if 'group5_trigger' not in loaded_config:
            loaded_config['group5_trigger'] = default_config['group5_trigger'].copy()
        
        # Гарантируем наличие настроек для группы 6 (5 кликов)
        if 'group6_clicks' not in loaded_config or len(loaded_config['group6_clicks']) != 5:
            loaded_config['group6_clicks'] = default_config['group6_clicks'].copy()
        
        # Гарантируем наличие настроек автоматических кликов
        if 'auto_clicks_settings' not in loaded_config:
            loaded_config['auto_clicks_settings'] = default_config['auto_clicks_settings'].copy()
        
        if 'auto_clicks_config' not in loaded_config:
            loaded_config['auto_clicks_config'] = default_config['auto_clicks_config'].copy()
        
        # Гарантируем наличие настроек разнообразных действий
        if 'action_settings' not in loaded_config:
            loaded_config['action_settings'] = default_config['action_settings'].copy()
        
        # Гарантируем наличие настроек расписания
        if 'schedule_settings' not in loaded_config:
            loaded_config['schedule_settings'] = default_config['schedule_settings'].copy()
        
        # Гарантируем наличие настроек оптимизации
        if 'optimization' not in loaded_config or not isinstance(loaded_config['optimization'], dict):
            loaded_config['optimization'] = default_config['optimization'].copy()
        
        # Гарантируем наличие настройки кулдауна для группы 1 после группы 4
        if 'group1_cooldown_after_group4' not in loaded_config:
            loaded_config['group1_cooldown_after_group4'] = default_config['group1_cooldown_after_group4']
        
        # Гарантируем наличие настроек скорости скрипта
        if 'script_speed' not in loaded_config:
            loaded_config['script_speed'] = default_config['script_speed'].copy()
        
        return loaded_config
    
    def save_config(self):
        """Сохраняет конфигурацию"""
        try:
            # Создаем временный файл
            temp_file = self.config_file.with_suffix('.tmp')
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            # Заменяем оригинальный файл
            if self.config_file.exists():
                os.remove(self.config_file)
            os.rename(temp_file, self.config_file)
            
            print("✅ Конфигурация сохранена")
        except Exception as e:
            print(f"❌ Ошибка сохранения конфигурации: {e}")
    
    def init_variables(self):
        """Инициализирует переменные"""
        self.is_monitoring = False
        self.is_paused = False
        self.detection_count = 0
        self.recovery_count = 0
        self.last_detection_time = None
        self.windows_data = []
        self.log_queue = deque(maxlen=100)
        self.last_triggered_windows = {}
        self.cooldown_period = 15
        
        # КУЛДАУН ДЛЯ ГРУППЫ 1 ПОСЛЕ СРАБАТЫВАНИЯ ГРУППЫ 4 - ИЗМЕНЕНО
        self.group1_cooldown_after_group4 = self.config.get('group1_cooldown_after_group4', 180)
        self.group1_cooldown_after_group4_active = False
        self.group1_cooldown_after_group4_start = 0
        self.group4_triggered_windows = {}  # Словарь для отслеживания окон, где сработала группа 4
        
        self.last_grid_screenshot_time = None
        self.grid_screenshot_thread = None
        self.grid_screenshot_running = False
        
        # СИСТЕМА ОЧЕРЕДИ ДЛЯ ОДНОВРЕМЕННОЙ ОБРАБОТКИ НЕСКОЛЬКИХ ТРИГГЕРОВ
        self.active_recoveries = {}
        self.recovery_queue = deque()
        
        # Трекер для усложненной логики действий
        self.windows_with_action1 = {}  # Окна, где сработало действие 1
        self.windows_allowed_action2 = set()  # Окна, где разрешено действие 2
        self.action2_chance_in_action1_windows = 20  # Шанс действия 2 в окнах с действием 1 (%)

        # Отслеживание окон, где сработали действия
        self.action_execution_history = {}  # window_idx: [список выполненных действий]

        # Счетчики для отдыха после восстановления окон - ИЗМЕНЕНО
        self.recovered_windows_count = 0
        self.is_resting = False
        self.rest_start_time = None
        self.was_monitoring_before_rest = False  # Состояние мониторинга перед отдыхом
        self.was_actions_before_rest = False     # Состояние действий перед отдыхом
        
        # Оптимизация для предотвращения зависаний
        self.consecutive_checks = 0
        self.last_memory_cleanup = time.time()
        self.recovery_lock = threading.Lock()
        self.monitoring_active = True
        self.skip_counter = 0
        
        # Переменные для автоматических кликов
        self.auto_clicks_running = False
        self.auto_clicks_thread = None
        self.last_auto_click_time = None
        self.auto_clicks_scheduled = False
        
        # Переменные для разнообразных действий
        self.actions_enabled = False
        self.actions_thread = None
        self.last_action_time = None
        self.action_counter = 0
        
        # Переменные для управления режимами
        self.current_mode = 'actions_only'  # 'actions_only', 'recovery_only', 'mixed'
        self.mode_change_time = time.time()
        self.schedule_check_counter = 0
        
        # Переменная для блокировки мониторинга во время ввода пароля
        self.password_input_active = False
        
        # Переменные для скорости работы скрипта
        self.detection_speed = self.config['script_speed']['detection_speed']
        self.action_speed = self.config['script_speed']['action_speed']
        self.recovery_speed = self.config['script_speed']['recovery_speed']
        
        # Инициализируем total_clicks_performed
        self.total_clicks_performed = 0
        
        # Инициализируем планировщик для автоматических кликов
        self.init_auto_clicks_scheduler()
        
        # Инициализируем планировщик для режимов работы
        self.init_schedule_mode()
    
    def init_auto_clicks_scheduler(self):
        """Инициализирует планировщик для автоматических кликов"""
        try:
            # Очищаем существующие задачи
            schedule.clear()
            
            # Получаем время из конфигурации
            first_time = self.config['auto_clicks_settings']['first_time']
            second_time = self.config['auto_clicks_settings']['second_time']
            
            # Планируем задачи
            if self.config['auto_clicks_settings']['enabled']:
                schedule.every().day.at(first_time).do(self.execute_auto_clicks)
                schedule.every().day.at(second_time).do(self.execute_auto_clicks)
                
                print(f"⏰ Автоматические клики запланированы на {first_time} и {second_time}")
                self.auto_clicks_scheduled = True
                
                # Запускаем поток для обработки расписания
                self.schedule_thread = threading.Thread(target=self.run_schedule, daemon=True)
                self.schedule_thread.start()
                
        except Exception as e:
            print(f"⚠️ Ошибка инициализации планировщика: {e}")
    
    def init_schedule_mode(self):
        """Инициализирует планировщик режимов работы"""
        try:
            # Запускаем проверку режима каждую минуту
            self.mode_scheduler_thread = threading.Thread(target=self.check_schedule_mode, daemon=True)
            self.mode_scheduler_thread.start()
            
            print("⏰ Планировщик режимов работы инициализирован")
            
        except Exception as e:
            print(f"⚠️ Ошибка инициализации планировщика режимов: {e}")
    
    def check_schedule_mode(self):
        """Проверяет и меняет режимы работы согласно расписанию"""
        while True:
            try:
                current_time = time.time()
                current_minute = datetime.now().minute
                
                # Получаем настройки расписания
                schedule_config = self.config.get('schedule_settings', {})
                action_periods = schedule_config.get('action_periods', [])
                
                # Определяем текущий режим
                new_mode = None
                for period in action_periods:
                    start = period.get('start_minute', 0)
                    end = period.get('end_minute', 60)
                    mode = period.get('mode', 'actions_only')
                    
                    if start <= current_minute < end:
                        new_mode = mode
                        break
                
                # Если режим изменился
                if new_mode and new_mode != self.current_mode:
                    self.current_mode = new_mode
                    self.mode_change_time = current_time
                    
                    # Логируем смену режима
                    if new_mode == 'actions_only':
                        self.log_message("🔄 Режим изменен: ТОЛЬКО ДЕЙСТВИЯ", 'SCHEDULE')
                        self.start_actions()
                        self.stop_recovery_mode()
                    elif new_mode == 'recovery_only':
                        self.log_message("🔄 Режим изменен: ТОЛЬКО ВОССТАНОВЛЕНИЕ", 'SCHEDULE')
                        self.stop_actions()
                        self.start_recovery_mode()
                    
                    # Сохраняем время изменения
                    schedule_config['last_mode_change'] = time.time()
                    schedule_config['current_mode'] = new_mode
                    self.save_config()
                
                # Ждем 1 минуту до следующей проверки
                time.sleep(60)
                
            except Exception as e:
                print(f"⚠️ Ошибка в планировщике режимов: {e}")
                time.sleep(60)
    
    def run_schedule(self):
        """Запускает цикл планировщика"""
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Проверяем каждую минуту
            except Exception as e:
                print(f"⚠️ Ошибка в планировщике: {e}")
                time.sleep(60)
    
    def execute_auto_clicks(self):
        """Выполняет автоматические клики в каждом окне"""
        if not self.config['auto_clicks_settings']['enabled']:
            return
        
        self.log_message("⏰ Запуск автоматических кликов по расписанию", 'AUTO_CLICKS')
        
        # Проверяем, что мониторинг активен
        if not self.is_monitoring or self.is_paused:
            self.log_message("⚠️ Автоматические клики пропущены: мониторинг неактивен", 'WARNING')
            return
        
        # Создаем отдельный поток для выполнения кликов
        self.auto_clicks_thread = threading.Thread(target=self._execute_auto_clicks_thread, daemon=True)
        self.auto_clicks_thread.start()
    
    def _execute_auto_clicks_thread(self):
        """Поток для выполнения автоматических кликов"""
        try:
            self.auto_clicks_running = True
            self.log_message("🔄 Начинаю проверку окон для автоматических кликов", 'AUTO_CLICKS')
            
            # Ждем, пока все окна будут без триггеров
            if self.config['auto_clicks_settings']['check_before_clicks']:
                if not self.wait_for_no_triggers():
                    self.log_message("⚠️ Не удалось дождаться отсутствия триггеров, пропускаем клики", 'WARNING')
                    self.auto_clicks_running = False
                    return
            
            # Получаем координаты для кликов
            click_coords = self.config['auto_clicks_config']
            
            # Выполняем клики в каждом окне
            for window_idx, window_info in enumerate(self.windows_data):
                if not self.auto_clicks_running:
                    break
                    
                try:
                    base_x = window_info.get('start_x', 0)
                    base_y = window_info.get('start_y', 0)
                    
                    self.log_message(f"🖱️ Выполняю 4 клика в окне {window_idx+1}", 'AUTO_CLICKS')
                    
                    # Выполняем 4 клика по разным координатам
                    for i, coord in enumerate(click_coords):
                        if not self.auto_clicks_running:
                            break
                            
                        # Вычисляем абсолютные координаты
                        abs_x = base_x + coord['x']
                        abs_y = base_y + coord['y']
                        
                        # Выполняем клик с человеческой задержкой
                        time.sleep(random.uniform(0.3, 0.5) * self.action_speed)
                        pyautogui.moveTo(abs_x, abs_y, duration=0.2 + random.uniform(0.05, 0.1))
                        time.sleep(random.uniform(0.05, 0.1) * self.action_speed)
                        pyautogui.click()
                        
                        self.log_message(f"   Клик {i+1}: ({coord['x']}, {coord['y']})", 'AUTO_CLICKS')
                        time.sleep(random.uniform(0.2, 0.3) * self.action_speed)
                    
                    # Пауза между окнами
                    if window_idx < len(self.windows_data) - 1:
                        time.sleep(random.uniform(0.5, 1.0) * self.action_speed)
                        
                except Exception as e:
                    self.log_message(f"❌ Ошибка при кликах в окне {window_idx+1}: {e}", 'ERROR')
                    continue
            
            self.last_auto_click_time = datetime.now()
            self.log_message("✅ Автоматические клики успешно выполнены во всех окнах", 'AUTO_CLICKS')
            
        except Exception as e:
            self.log_message(f"❌ Критическая ошибка при выполнении автоматических кликов: {e}", 'ERROR')
        finally:
            self.auto_clicks_running = False
    
    def wait_for_no_triggers(self):
        """Ожидает, пока во всех окнах не будет триггеров"""
        max_wait_time = self.config['auto_clicks_settings']['wait_for_no_triggers']
        check_interval = 2  # Проверяем каждые 2 секунды
        start_time = time.time()
        
        self.log_message(f"⏳ Ожидание отсутствия триггеров (макс. {max_wait_time} сек)", 'AUTO_CLICKS')
        
        while time.time() - start_time < max_wait_time:
            # Проверяем все окна на наличие триггеров
            all_windows_clear = True
            
            for window_idx in range(min(len(self.windows_data), 10)):  # Проверяем первые 10 окон для скорости
                try:
                    window_info = self.windows_data[window_idx]
                    x1 = window_info.get('start_x', 0)
                    y1 = window_info.get('start_y', 0)
                    x2 = window_info.get('end_x', x1 + 800)
                    y2 = window_info.get('end_y', y1 + 600)
                    
                    # Делаем скриншот окна
                    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
                    
                    # Быстрая проверка на триггеры
                    has_trigger = self.quick_check_for_triggers(screenshot_cv)
                    
                    if has_trigger:
                        all_windows_clear = False
                        self.log_message(f"   Окно {window_idx+1}: обнаружен триггер, продолжаем ожидание", 'AUTO_CLICKS')
                        break
                        
                except Exception as e:
                    self.log_message(f"⚠️ Ошибка проверки окна {window_idx+1}: {e}", 'WARNING')
                    continue
            
            if all_windows_clear:
                self.log_message("✅ Все окна без триггеров, продолжаем", 'AUTO_CLICKS')
                return True
            
            # Ждем перед следующей проверкой
            time.sleep(check_interval)
        
        self.log_message("⚠️ Таймаут ожидания отсутствия триггеров", 'WARNING')
        return False
    
    def quick_check_for_triggers(self, screenshot_cv):
        """Быстрая проверка на наличие триггеров в окне"""
        # Проверяем только наиболее важные триггеры
        check_groups = ['group1', 'group2', 'group3']
        
        for trigger_key in self.trigger_images:
            trigger_data = self.trigger_images[trigger_key]
            group = trigger_data.get('group', '')
            
            if group in check_groups:
                try:
                    result = cv2.matchTemplate(screenshot_cv, 
                                              trigger_data['image'], 
                                              cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    threshold = self.config.get(f'threshold_{group}', 0.65)
                    
                    if max_val >= threshold:
                        return True
                except Exception:
                    continue
        
        return False
    
    def start_actions(self):
        """Запускает выполнение разнообразных действий"""
        if self.actions_enabled:
            return
        
        self.actions_enabled = True
        self.log_message("🚀 Запуск разнообразных действий", 'ACTIONS')
        
        # Запускаем поток для выполнения действий
        self.actions_thread = threading.Thread(target=self.execute_actions_loop, daemon=True)
        self.actions_thread.start()
    
    def stop_actions(self):
        """Останавливает выполнение действий"""
        self.actions_enabled = False
        self.log_message("⏹ Остановка разнообразных действий", 'ACTIONS')
    
    def start_recovery_mode(self):
        """Запускает режим восстановления"""
        if not self.is_monitoring:
            self.start_monitoring()
        self.log_message("🔄 Режим восстановления активирован", 'RECOVERY')
    
    def stop_recovery_mode(self):
        """Останавливает режим восстановления"""
        if self.is_monitoring:
            self.stop_monitoring()
        self.log_message("⏹ Режим восстановления деактивирован", 'RECOVERY')
    
def execute_actions_loop(self):
    """Цикл выполнения разнообразных действий с усложненной логикой"""
    action_counter = 0
    
    while self.actions_enabled:
        try:
            # Проверяем, что режим все еще actions_only
            if self.current_mode != 'actions_only':
                time.sleep(1)
                continue
            
            # Получаем настройки действий
            action_settings = self.config.get('action_settings', {})
            if not action_settings.get('enabled', True):
                time.sleep(1)
                continue
            
            actions_list = action_settings.get('actions', [])
            if not actions_list:
                time.sleep(1)
                continue
            
            # Получаем информацию о включенных действиях
            enabled_actions = action_settings.get('enabled_actions', [True, True, True, True, True])
            
            # Проверяем порядок окон
            window_order = action_settings.get('window_order', 'sequential')
            
            # ИСПРАВЛЕНИЕ: Правильный порядок окон для сетки 6x5
            if window_order == 'sequential':
                # Последовательный порядок окон (6x5 = 30 окон)
                window_indices = list(range(len(self.windows_data)))
            else:
                # Случайный порядок окон
                window_indices = list(range(len(self.windows_data)))
                random.shuffle(window_indices)
            
            # Проходим по всем окнам в выбранном порядке
            for window_idx in window_indices:
                if not self.actions_enabled or self.current_mode != 'actions_only':
                    break
                
                # Проверяем, что индекс окна существует
                if window_idx >= len(self.windows_data):
                    continue
                
                # Проверяем усложненную логику действий
                can_execute_action = True
                action_to_execute = None
                
                # Если в окне уже было действие 1
                if window_idx in self.windows_with_action1:
                    # В этом окне другие действия (кроме 2) не срабатывают
                    # Проверяем, можем ли выполнить действие 2
                    if window_idx in self.windows_allowed_action2:
                        # Проверяем шанс 20%
                        if random.randint(1, 100) <= self.action2_chance_in_action1_windows:
                            action_to_execute = self.find_action_by_type(actions_list, 'action2_four_single_clicks')
                    # Если не попадаем в 20%, пропускаем это окно
                    can_execute_action = (action_to_execute is not None)
                else:
                    # Обычная логика выбора действия
                    available_actions = []
                    for idx, action_config in enumerate(actions_list):
                        if idx < len(enabled_actions) and enabled_actions[idx]:
                            # Проверяем вероятность выполнения этого действия
                            chance = action_config.get('chance', 0)
                            if chance > 0 and random.randint(1, 100) <= chance:
                                # Проверяем тип действия
                                action_type = action_config.get('type', '')
                                if action_type == 'action2_four_single_clicks':
                                    # Действие 2 не срабатывает в других окнах
                                    # (только если до этого в окне сработало действие 1)
                                    continue
                                available_actions.append(action_config)
                    
                    if available_actions:
                        # Выбираем случайное действие из доступных
                        action_to_execute = random.choice(available_actions)
                
                if not action_to_execute or not can_execute_action:
                    continue
                
                # Выполняем действие в текущем окне
                result = self.execute_specific_action_in_window(action_to_execute, window_idx)
                
                # Обновляем историю выполнения действий
                if result:
                    action_type = action_to_execute.get('type', '')
                    
                    # Инициализируем историю для окна
                    if window_idx not in self.action_execution_history:
                        self.action_execution_history[window_idx] = []
                    
                    # Добавляем действие в историю
                    self.action_execution_history[window_idx].append({
                        'type': action_type,
                        'time': time.time(),
                        'name': self.get_action_name(action_type)
                    })
                    
                    # Если это действие 1, отмечаем окно
                    if action_type == 'action1_single_click':
                        self.windows_with_action1[window_idx] = time.time()
                        # Даем разрешение на действие 2 в этом окне
                        self.windows_allowed_action2.add(window_idx)
                        self.log_message(f"🎯 Окно {window_idx+1}: действие 1 выполнено, действие 2 теперь доступно с шансом 20%", 'ACTION_LOGIC')
                    
                    action_counter += 1
                
                # Интервал между действиями с учетом скорости
                action_interval = action_settings.get('action_interval', 2)
                random_delay = action_settings.get('random_delay', True)
                
                if random_delay:
                    delay = action_interval + random.uniform(-0.5, 0.5)
                    delay = max(0.1, delay)
                else:
                    delay = action_interval
                
                # Применяем коэффициент скорости
                delay = delay / self.action_speed
                
                # Небольшая пауза перед следующим действием
                time.sleep(delay)
            
            # Очистка памяти каждые 50 действий
            if action_counter % 50 == 0:
                self.cleanup_memory()
            
            # Очищаем старые записи в истории (старше 1 часа)
            self.cleanup_action_history()
            
        except Exception as e:
            self.log_message(f"❌ Ошибка в цикле действий: {e}", 'ERROR')
            time.sleep(5)

def find_action_by_type(self, actions_list, action_type):
    """Находит действие по типу"""
    for action in actions_list:
        if action.get('type') == action_type:
            return action
    return None

def cleanup_action_history(self):
    """Очищает старую историю действий"""
    current_time = time.time()
    one_hour_ago = current_time - 3600
    
    # Очищаем окна с действием 1 старше 1 часа
    windows_to_remove = []
    for window_idx, action_time in self.windows_with_action1.items():
        if action_time < one_hour_ago:
            windows_to_remove.append(window_idx)
    
    for window_idx in windows_to_remove:
        del self.windows_with_action1[window_idx]
        if window_idx in self.windows_allowed_action2:
            self.windows_allowed_action2.remove(window_idx)
    
    # Очищаем историю действий старше 1 часа
    for window_idx in list(self.action_execution_history.keys()):
        if window_idx in self.action_execution_history:
            self.action_execution_history[window_idx] = [
                action for action in self.action_execution_history[window_idx]
                if action['time'] > one_hour_ago
            ]
            if not self.action_execution_history[window_idx]:
                del self.action_execution_history[window_idx]
                
    def execute_specific_action_in_window(self, action_config, window_idx):
        """Выполняет конкретное действие в указанном окне"""
        try:
            action_type = action_config.get('type', '')
            
            if not action_type:
                return
            
            if window_idx >= len(self.windows_data):
                return
            
            window_info = self.windows_data[window_idx]
            
            try:
                base_x = window_info.get('start_x', 0)
                base_y = window_info.get('start_y', 0)
                
                # Выполняем действие в зависимости от типа
                if action_type == 'action1_single_click':
                    self.execute_action1_single_click(action_config, base_x, base_y, window_idx)
                elif action_type == 'action2_four_single_clicks':
                    self.execute_action2_four_single_clicks(action_config, base_x, base_y, window_idx)
                elif action_type == 'action3_nine_clicks':
                    self.execute_action3_nine_clicks(action_config, base_x, base_y, window_idx)
                elif action_type == 'action4_joystick_random_fixed':
                    self.execute_action4_joystick_random_fixed(action_config, base_x, base_y, window_idx)
                elif action_type == 'action5_joystick_random_double_click':
                    self.execute_action5_joystick_random_double_click(action_config, base_x, base_y, window_idx)
                
                # Короткая пауза после выполнения действия
                time.sleep(0.1 / self.action_speed)
                
                # Логируем выполнение действия
                self.last_action_time = datetime.now()
                self.action_counter += 1
                self.log_message(f"⚡ Выполнено действие: {self.get_action_name(action_type)} в окне {window_idx+1}", 'ACTION')
                
            except Exception as e:
                self.log_message(f"❌ Ошибка выполнения действия в окне {window_idx+1}: {e}", 'ERROR')
                return
            
        except Exception as e:
            self.log_message(f"❌ Критическая ошибка выполнения действия: {e}", 'ERROR')
    
    def execute_specific_action(self, action_config):
        """Выполняет конкретное действие во всех окнах"""
        try:
            action_type = action_config.get('type', '')
            
            if not action_type:
                return
            
            # Проверяем порядок окон из настроек
            action_settings = self.config.get('action_settings', {})
            window_order = action_settings.get('window_order', 'sequential')
            
            if window_order == 'sequential':
                # Последовательный порядок окон
                window_indices = list(range(len(self.windows_data)))
            else:
                # Случайный порядок окон
                window_indices = list(range(len(self.windows_data)))
                random.shuffle(window_indices)
            
            for window_idx in window_indices:
                if not self.actions_enabled or self.current_mode != 'actions_only':
                    break
                
                self.execute_specific_action_in_window(action_config, window_idx)
                
                # Короткая пауза между окнами
                time.sleep(0.1 / self.action_speed)
            
            # Логируем выполнение действия
            self.last_action_time = datetime.now()
            self.action_counter += 1
            self.log_message(f"⚡ Выполнено действие: {self.get_action_name(action_type)}", 'ACTION')
            
        except Exception as e:
            self.log_message(f"❌ Критическая ошибка выполнения действия: {e}", 'ERROR')
    
    def get_action_name(self, action_type):
        """Возвращает читаемое имя действия"""
        action_names = {
            'action1_single_click': 'Клик по координатам',
            'action2_four_single_clicks': '4 обычных клика',
            'action3_nine_clicks': '9 отдельных кликов',
            'action4_joystick_random_fixed': 'Джойстик (45,135,225,315°) + клик',
            'action5_joystick_random_double_click': 'Джойстик 45-135° + двойной клик'
        }
        return action_names.get(action_type, action_type)
    
    def execute_action1_single_click(self, action_config, base_x, base_y, window_idx):
        """Действие 1: Простой клик по координатам"""
        try:
            x = action_config.get('x', 200)
            y = action_config.get('y', 200)
            
            abs_x = base_x + x
            abs_y = base_y + y
            
            # Выполняем клик с учетом скорости
            pyautogui.moveTo(abs_x, abs_y, duration=0.1 / self.action_speed)
            time.sleep(0.05 / self.action_speed)
            pyautogui.click()
            
            # Увеличиваем счетчик кликов
            self.total_clicks_performed += 1
            
            # Задержка для реалистичности
            time.sleep(0.05 / self.action_speed)
            
        except Exception as e:
            raise e
    
    def execute_action2_four_single_clicks(self, action_config, base_x, base_y, window_idx):
        """Действие 2: 4 обычных клика по разным координатам"""
        try:
            clicks = action_config.get('clicks', [
                {'x': 300, 'y': 300},
                {'x': 320, 'y': 320},
                {'x': 340, 'y': 340},
                {'x': 360, 'y': 360}
            ])
            
            for i, click_coords in enumerate(clicks):
                x = click_coords.get('x', 300 + i*20)
                y = click_coords.get('y', 300 + i*20)
                
                abs_x = base_x + x
                abs_y = base_y + y
                
                # Выполняем клик с учетом скорости
                pyautogui.moveTo(abs_x, abs_y, duration=0.1 + random.uniform(0.01, 0.05))
                time.sleep(0.05 / self.action_speed)
                pyautogui.click()
                
                # Увеличиваем счетчик кликов
                self.total_clicks_performed += 1
                
                # Небольшая задержка между кликами
                time.sleep(0.05 + random.uniform(0.01, 0.03) / self.action_speed)
            
        except Exception as e:
            raise e
    
    def execute_action3_nine_clicks(self, action_config, base_x, base_y, window_idx):
        """Действие 3: 9 отдельных кликов"""
        try:
            clicks = action_config.get('clicks', [
                {'x': 400, 'y': 400, 'type': 'click'},  # Клик 1
                {'x': 420, 'y': 420, 'type': 'click'},  # Клик 2
                {'x': 440, 'y': 440, 'type': 'click'},  # Клик 3
                {'x': 460, 'y': 460, 'type': 'click'},  # Клик 4
                {'x': 480, 'y': 480, 'type': 'click'},  # Клик 5
                {'x': 500, 'y': 500, 'type': 'click'},  # Клик 6
                {'x': 520, 'y': 520, 'type': 'click'},  # Клик 7
                {'x': 540, 'y': 540, 'type': 'click'},  # Клик 8
                {'x': 560, 'y': 560, 'type': 'click'}   # Клик 9
            ])
            
            for i, action in enumerate(clicks):
                action_type = action.get('type', 'click')
                
                if action_type == 'click':
                    x = action.get('x', 400 + i*20)
                    y = action.get('y', 400 + i*20)
                    
                    abs_x = base_x + x
                    abs_y = base_y + y
                    
                    # Выполняем клик с учетом скорости
                    pyautogui.moveTo(abs_x, abs_y, duration=0.1 + random.uniform(0.01, 0.05))
                    time.sleep(0.05 / self.action_speed)
                    pyautogui.click()
                    
                    # Увеличиваем счетчик кликов
                    self.total_clicks_performed += 1
                    
                    # Небольшая задержка между действиями
                    time.sleep(0.1 + random.uniform(0.01, 0.03) / self.action_speed)
            
        except Exception as e:
            raise e
        
    def execute_action4_joystick_random_fixed(self, action_config, base_x, base_y, window_idx):
        """Действие 4: Движение джойстиком в случайное из фиксированных направлений (обновленные диапазоны) + клик"""
        try:
            # Получаем координаты начала движения джойстика
            joystick_start_x = action_config.get('joystick_start_x', 350)
            joystick_start_y = action_config.get('joystick_start_y', 350)
            
            # Случайные направления из обновленных диапазонов:
            # 1. 33-55 градусов
            # 2. 115-150 градусов
            # 3. 200-250 градусов
            # 4. 300-330 градусов
            direction_ranges = [
                (33, 55),    # Диапазон 1
                (115, 150),  # Диапазон 2
                (200, 250),  # Диапазон 3
                (300, 330)   # Диапазон 4
            ]
            
            # Выбираем случайный диапазон
            selected_range = random.choice(direction_ranges)
            # Выбираем случайный градус в выбранном диапазоне
            direction = random.uniform(selected_range[0], selected_range[1])
            
            distance = action_config.get('distance', 100)
            duration = action_config.get('duration', 2.0)
            
            # Координаты клика после движения
            click_x = action_config.get('click_x', 450)
            click_y = action_config.get('click_y', 450)
            
            # Вычисляем абсолютные координаты
            abs_joystick_x = base_x + joystick_start_x
            abs_joystick_y = base_y + joystick_start_y
            abs_click_x = base_x + click_x
            abs_click_y = base_y + click_y
            
            # Конвертируем угол из градусов в радианы
            angle_rad = math.radians(direction)
            
            # Вычисляем конечные координаты движения
            end_x = abs_joystick_x + distance * math.cos(angle_rad)
            end_y = abs_joystick_y + distance * math.sin(angle_rad)
            
            # Логируем движение
            self.log_message(f"🎮 Джойстик обновленный диапазон: ({joystick_start_x},{joystick_start_y}) -> ({direction:.1f}°, {distance}px, {duration}сек)", 'JOYSTICK')
            
            # Нажимаем на начальную позицию (имитируем нажатие джойстика)
            pyautogui.moveTo(abs_joystick_x, abs_joystick_y, duration=0.1 / self.action_speed)
            pyautogui.mouseDown()
            time.sleep(0.1 / self.action_speed)
            
            # Перемещаем курсор (имитируем движение джойстика)
            pyautogui.moveTo(end_x, end_y, duration=duration / self.action_speed)
            time.sleep(0.1 / self.action_speed)
            
            # Отпускаем кнопку мыши
            pyautogui.mouseUp()
            time.sleep(0.1 / self.action_speed)
            
            # Выполняем клик по указанным координатам
            pyautogui.moveTo(abs_click_x, abs_click_y, duration=0.1 / self.action_speed)
            pyautogui.click()
            
            # Увеличиваем счетчик кликов
            self.total_clicks_performed += 1
            
        except Exception as e:
            raise e   
        
    def execute_action5_joystick_random_double_click(self, action_config, base_x, base_y, window_idx):
        """Действие 5: Джойстик со случайным движением 225-315 градусов и двойным кликом"""
        try:
            # Получаем координаты начала движения джойстика
            joystick_start_x = action_config.get('joystick_start_x', 350)
            joystick_start_y = action_config.get('joystick_start_y', 350)
            
            # Случайное направление от 225 до 315 градусов (вместо 45-135)
            direction = random.uniform(225, 315)
            distance = action_config.get('distance', 100)
            duration_min = action_config.get('duration_min', 1.0)
            duration_max = action_config.get('duration_max', 3.0)
            duration = random.uniform(duration_min, duration_max)
            
            # Координаты двойного клика после движения
            click_x = action_config.get('click_x', 450)
            click_y = action_config.get('click_y', 450)
            
            # Вычисляем абсолютные координаты
            abs_joystick_x = base_x + joystick_start_x
            abs_joystick_y = base_y + joystick_start_y
            abs_click_x = base_x + click_x
            abs_click_y = base_y + click_y
            
            # Конвертируем угол из градусов в радианы
            angle_rad = math.radians(direction)
            
            # Вычисляем конечные координаты движения
            end_x = abs_joystick_x + distance * math.cos(angle_rad)
            end_y = abs_joystick_y + distance * math.sin(angle_rad)
            
            # Логируем движение
            self.log_message(f"🎮 Джойстик 225-315° + двойной клик: ({joystick_start_x},{joystick_start_y}) -> ({direction:.1f}°, {distance}px, {duration:.1f}сек)", 'JOYSTICK')
            
            # Нажимаем на начальную позицию (имитируем нажатие джойстика)
            pyautogui.moveTo(abs_joystick_x, abs_joystick_y, duration=0.1 / self.action_speed)
            pyautogui.mouseDown()
            time.sleep(0.1 / self.action_speed)
            
            # Перемещаем курсор (имитируем движение джойстика)
            pyautogui.moveTo(end_x, end_y, duration=duration / self.action_speed)
            time.sleep(0.1 / self.action_speed)
            
            # Отпускаем кнопку мыши
            pyautogui.mouseUp()
            time.sleep(0.1 / self.action_speed)
            
            # Выполняем двойной клик по указанным координатам
            pyautogui.moveTo(abs_click_x, abs_click_y, duration=0.1 / self.action_speed)
            pyautogui.doubleClick()
            
            # Увеличиваем счетчик кликов (двойной клик считается как 2 клика)
            self.total_clicks_performed += 2
            
        except Exception as e:
            raise e
    
    def setup_gui(self):
        """Создает графический интерфейс"""
        self.root = tk.Tk()
        self.root.title("🎯 Trigger Detector Pro v3.0")  # Обновлена версия
        self.root.geometry("1200x800")
        self.root.minsize(1100, 750)
        
        self.setup_styles()
        
        try:
            self.root.iconbitmap(self.base_dir / 'icon.ico')
        except:
            pass
        
        self.setup_notebook()
        self.setup_statusbar()
        self.update_gui()
        
    def setup_styles(self):
        """Настраивает стили"""
        style = ttk.Style()
        style.theme_use('clam')
        
        self.colors = {
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'info': '#17a2b8',
            'primary': '#007bff',
            'dark': '#343a40',
            'light': '#f8f9fa'
        }
        
        style.configure('Accent.TButton', foreground='white', background=self.colors['success'])
        style.configure('Warning.TButton', foreground='white', background=self.colors['warning'])
        style.configure('Danger.TButton', foreground='white', background=self.colors['danger'])
        
    def setup_notebook(self):
        """Создает вкладки"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.tab_detection = ttk.Frame(self.notebook)
        self.tab_password_settings = ttk.Frame(self.notebook)  # Новая вкладка для настроек пароля
        self.notebook.add(self.tab_password_settings, text='🔐 Настройки пароля')
        self.tab_triggers = ttk.Frame(self.notebook)
        self.tab_windows = ttk.Frame(self.notebook)
        self.tab_recovery = ttk.Frame(self.notebook)
        self.tab_actions = ttk.Frame(self.notebook)  # Новая вкладка для действий
        self.tab_schedule = ttk.Frame(self.notebook)  # Новая вкладка для расписания
        self.tab_auto_clicks = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)  # Вкладка с настройками скорости
        self.tab_coordinates = ttk.Frame(self.notebook)  # НОВАЯ ВКЛАДКА: Настройки координат
        
        self.notebook.add(self.tab_detection, text='🎯 Детекция')
        self.notebook.add(self.tab_triggers, text='🖼️ Группы триггеров')
        self.notebook.add(self.tab_windows, text='🪟 Окна')
        self.notebook.add(self.tab_recovery, text='⚡ Восстановление')
        self.notebook.add(self.tab_actions, text='🎮 Действия')  # Добавляем вкладку действий
        self.notebook.add(self.tab_schedule, text='⏰ Расписание')  # Добавляем вкладку расписания
        self.notebook.add(self.tab_auto_clicks, text='🔄 Авто-клики')
        self.notebook.add(self.tab_settings, text='⚙️ Настройки скорости')
        self.notebook.add(self.tab_coordinates, text='📍 Настройки координат')  # Добавляем вкладку координат
        
        self.setup_detection_tab()
        self.setup_triggers_tab()
        self.setup_windows_tab()
        self.setup_recovery_tab()
        self.setup_actions_tab()  # Добавляем настройку вкладки действий
        self.setup_schedule_tab()  # Добавляем настройку вкладки расписания
        self.setup_auto_clicks_tab()
        self.setup_settings_tab()
        self.setup_coordinates_tab()  # Добавляем настройку вкладки координат
    
    def setup_coordinates_tab(self):
        """Вкладка настройки координат для всех групп триггеров"""
        title_frame = ttk.Frame(self.tab_coordinates)
        title_frame.pack(fill='x', pady=10)
        
        ttk.Label(title_frame, text="📍 Настройки координат для всех групп триггеров", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(title_frame, text="Настройка координат кликов для каждой группы триггеров").pack()
        
        # Создаем контейнер с прокруткой
        container = ttk.Frame(self.tab_coordinates)
        container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Создаем canvas и скроллбар
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ГРУППА 1: 2 клика
        group1_frame = ttk.LabelFrame(scrollable_frame, text="ГРУППА 1: 2 клика (15 триггеров)", padding=10)
        group1_frame.pack(fill='x', padx=10, pady=5)
        
        # Первый клик
        click1_frame = ttk.Frame(group1_frame)
        click1_frame.pack(fill='x', pady=5)
        
        ttk.Label(click1_frame, text="Первый клик - X:").pack(side='left', padx=5)
        self.var_group1_click1_x = tk.IntVar(value=self.config['group1_clicks'][0]['x'])
        ttk.Spinbox(click1_frame, from_=0, to=1000, textvariable=self.var_group1_click1_x, width=8).pack(side='left', padx=5)
        
        ttk.Label(click1_frame, text="Y:").pack(side='left', padx=5)
        self.var_group1_click1_y = tk.IntVar(value=self.config['group1_clicks'][0]['y'])
        ttk.Spinbox(click1_frame, from_=0, to=1000, textvariable=self.var_group1_click1_y, width=8).pack(side='left', padx=5)
        
        # Второй клик
        click2_frame = ttk.Frame(group1_frame)
        click2_frame.pack(fill='x', pady=5)
        
        ttk.Label(click2_frame, text="Второй клик - X:").pack(side='left', padx=5)
        self.var_group1_click2_x = tk.IntVar(value=self.config['group1_clicks'][1]['x'])
        ttk.Spinbox(click2_frame, from_=0, to=1000, textvariable=self.var_group1_click2_x, width=8).pack(side='left', padx=5)
        
        ttk.Label(click2_frame, text="Y:").pack(side='left', padx=5)
        self.var_group1_click2_y = tk.IntVar(value=self.config['group1_clicks'][1]['y'])
        ttk.Spinbox(click2_frame, from_=0, to=1000, textvariable=self.var_group1_click2_y, width=8).pack(side='left', padx=5)
        
        # Кнопка захвата координат
        capture_frame = ttk.Frame(group1_frame)
        capture_frame.pack(fill='x', pady=5)
        
        ttk.Button(capture_frame, text="📷 Захватить координаты первого клика", 
                  command=lambda: self.capture_coordinates(self.var_group1_click1_x, self.var_group1_click1_y)).pack(side='left', padx=5)
        ttk.Button(capture_frame, text="📷 Захватить координаты второго клика", 
                  command=lambda: self.capture_coordinates(self.var_group1_click2_x, self.var_group1_click2_y)).pack(side='left', padx=5)
        
        # Описание
        desc_frame = ttk.Frame(group1_frame)
        desc_frame.pack(fill='x', pady=5)
        
        ttk.Label(desc_frame, text="При обнаружении любого из 15 триггеров группы 1 выполняются 2 клика по указанным координатам", 
                 font=('Arial', 9)).pack(anchor='w')
        
        # ГРУППА 2: 1 клик
        group2_frame = ttk.LabelFrame(scrollable_frame, text="ГРУППА 2: 1 клик", padding=10)
        group2_frame.pack(fill='x', padx=10, pady=5)
        
        # Координаты клика
        click_frame = ttk.Frame(group2_frame)
        click_frame.pack(fill='x', pady=5)
        
        ttk.Label(click_frame, text="Координата X:").pack(side='left', padx=5)
        self.var_group2_click_x = tk.IntVar(value=self.config['group2_click']['x'])
        ttk.Spinbox(click_frame, from_=0, to=1000, textvariable=self.var_group2_click_x, width=8).pack(side='left', padx=5)
        
        ttk.Label(click_frame, text="Координата Y:").pack(side='left', padx=5)
        self.var_group2_click_y = tk.IntVar(value=self.config['group2_click']['y'])
        ttk.Spinbox(click_frame, from_=0, to=1000, textvariable=self.var_group2_click_y, width=8).pack(side='left', padx=5)
        
        # Кнопка захвата
        capture2_frame = ttk.Frame(group2_frame)
        capture2_frame.pack(fill='x', pady=5)
        
        ttk.Button(capture2_frame, text="📷 Захватить координаты", 
                  command=lambda: self.capture_coordinates(self.var_group2_click_x, self.var_group2_click_y)).pack(side='left', padx=5)
        
        # ГРУППА 3: 1 клик
        group3_frame = ttk.LabelFrame(scrollable_frame, text="ГРУППА 3: 1 клик", padding=10)
        group3_frame.pack(fill='x', padx=10, pady=5)
        
        # Координаты клика
        click3_frame = ttk.Frame(group3_frame)
        click3_frame.pack(fill='x', pady=5)
        
        ttk.Label(click3_frame, text="Координата X:").pack(side='left', padx=5)
        self.var_group3_click_x = tk.IntVar(value=self.config['group3_click']['x'])
        ttk.Spinbox(click3_frame, from_=0, to=1000, textvariable=self.var_group3_click_x, width=8).pack(side='left', padx=5)
        
        ttk.Label(click3_frame, text="Координата Y:").pack(side='left', padx=5)
        self.var_group3_click_y = tk.IntVar(value=self.config['group3_click']['y'])
        ttk.Spinbox(click3_frame, from_=0, to=1000, textvariable=self.var_group3_click_y, width=8).pack(side='left', padx=5)
        
        # Кнопка захвата
        capture3_frame = ttk.Frame(group3_frame)
        capture3_frame.pack(fill='x', pady=5)
        
        ttk.Button(capture3_frame, text="📷 Захватить координаты", 
                  command=lambda: self.capture_coordinates(self.var_group3_click_x, self.var_group3_click_y)).pack(side='left', padx=5)
        
        # ГРУППА 4: 1 клик (для всех 20 триггеров)
        group4_frame = ttk.LabelFrame(scrollable_frame, text="ГРУППА 4: 1 клик (20 триггеров - одинаковые координаты)", padding=10)
        group4_frame.pack(fill='x', padx=10, pady=5)
        
        # Координаты клика
        click4_frame = ttk.Frame(group4_frame)
        click4_frame.pack(fill='x', pady=5)
        
        ttk.Label(click4_frame, text="Координата X:").pack(side='left', padx=5)
        self.var_group4_click_x = tk.IntVar(value=self.config['group4_click']['x'])
        ttk.Spinbox(click4_frame, from_=0, to=1000, textvariable=self.var_group4_click_x, width=8).pack(side='left', padx=5)
        
        ttk.Label(click4_frame, text="Координата Y:").pack(side='left', padx=5)
        self.var_group4_click_y = tk.IntVar(value=self.config['group4_click']['y'])
        ttk.Spinbox(click4_frame, from_=0, to=1000, textvariable=self.var_group4_click_y, width=8).pack(side='left', padx=5)
        
        # Кнопка захвата
        capture4_frame = ttk.Frame(group4_frame)
        capture4_frame.pack(fill='x', pady=5)
        
        ttk.Button(capture4_frame, text="📷 Захватить координаты", 
                  command=lambda: self.capture_coordinates(self.var_group4_click_x, self.var_group4_click_y)).pack(side='left', padx=5)
        
        # Описание
        desc4_frame = ttk.Frame(group4_frame)
        desc4_frame.pack(fill='x', pady=5)
        
        ttk.Label(desc4_frame, text="Все 20 триггеров группы 4 используют одинаковые координаты для клика", 
                 font=('Arial', 9)).pack(anchor='w')
        
        # ГРУППА 5: КЛИК + ПАРОЛЬ + КЛИК
        group5_frame = ttk.LabelFrame(scrollable_frame, text="ГРУППА 5: КЛИК + ПАРОЛЬ + КЛИК (1 триггер)", padding=10)
        group5_frame.pack(fill='x', padx=10, pady=5)
        
        # Первый клик
        click5_1_frame = ttk.Frame(group5_frame)
        click5_1_frame.pack(fill='x', pady=5)
        
        ttk.Label(click5_1_frame, text="Первый клик - X:").pack(side='left', padx=5)
        self.var_group5_click1_x = tk.IntVar(value=self.config['group5_trigger']['first_click']['x'])
        ttk.Spinbox(click5_1_frame, from_=0, to=1000, textvariable=self.var_group5_click1_x, width=8).pack(side='left', padx=5)
        
        ttk.Label(click5_1_frame, text="Y:").pack(side='left', padx=5)
        self.var_group5_click1_y = tk.IntVar(value=self.config['group5_trigger']['first_click']['y'])
        ttk.Spinbox(click5_1_frame, from_=0, to=1000, textvariable=self.var_group5_click1_y, width=8).pack(side='left', padx=5)
        
        # Пароль
        password_frame = ttk.Frame(group5_frame)
        password_frame.pack(fill='x', pady=5)
        
        ttk.Label(password_frame, text="Пароль:").pack(side='left', padx=5)
        self.var_group5_password = tk.StringVar(value=self.config['group5_trigger']['password'])
        ttk.Entry(password_frame, textvariable=self.var_group5_password, width=20).pack(side='left', padx=5)
        
        # Второй клик
        click5_2_frame = ttk.Frame(group5_frame)
        click5_2_frame.pack(fill='x', pady=5)
        
        ttk.Label(click5_2_frame, text="Второй клик - X:").pack(side='left', padx=5)
        self.var_group5_click2_x = tk.IntVar(value=self.config['group5_trigger']['second_click']['x'])
        ttk.Spinbox(click5_2_frame, from_=0, to=1000, textvariable=self.var_group5_click2_x, width=8).pack(side='left', padx=5)
        
        ttk.Label(click5_2_frame, text="Y:").pack(side='left', padx=5)
        self.var_group5_click2_y = tk.IntVar(value=self.config['group5_trigger']['second_click']['y'])
        ttk.Spinbox(click5_2_frame, from_=0, to=1000, textvariable=self.var_group5_click2_y, width=8).pack(side='left', padx=5)
        
        # Кнопки захвата
        capture5_frame = ttk.Frame(group5_frame)
        capture5_frame.pack(fill='x', pady=5)
        
        ttk.Button(capture5_frame, text="📷 Захватить первый клик", 
                  command=lambda: self.capture_coordinates(self.var_group5_click1_x, self.var_group5_click1_y)).pack(side='left', padx=5)
        ttk.Button(capture5_frame, text="📷 Захватить второй клик", 
                  command=lambda: self.capture_coordinates(self.var_group5_click2_x, self.var_group5_click2_y)).pack(side='left', padx=5)
        
        # Описание
        desc5_frame = ttk.Frame(group5_frame)
        desc5_frame.pack(fill='x', pady=5)
        
        ttk.Label(desc5_frame, text="При обнаружении триггера группы 5: 1) Клик по первым координатам, 2) Ввод пароля, 3) Клик по вторым координатам", 
                 font=('Arial', 9)).pack(anchor='w')
        
        # ГРУППА 6: 5 РАЗНЫХ КЛИКОВ
        group6_frame = ttk.LabelFrame(scrollable_frame, text="ГРУППА 6: 5 РАЗНЫХ КЛИКОВ (5 триггеров)", padding=10)
        group6_frame.pack(fill='x', padx=10, pady=5)
        
        # Создаем переменные для 5 кликов
        self.var_group6_clicks = []
        for i in range(5):
            click_frame = ttk.Frame(group6_frame)
            click_frame.pack(fill='x', pady=2)
            
            ttk.Label(click_frame, text=f"Клик {i+1} - X:").pack(side='left', padx=5)
            var_x = tk.IntVar(value=self.config['group6_clicks'][i]['x'])
            ttk.Spinbox(click_frame, from_=0, to=1000, textvariable=var_x, width=8).pack(side='left', padx=5)
            
            ttk.Label(click_frame, text="Y:").pack(side='left', padx=5)
            var_y = tk.IntVar(value=self.config['group6_clicks'][i]['y'])
            ttk.Spinbox(click_frame, from_=0, to=1000, textvariable=var_y, width=8).pack(side='left', padx=5)
            
            # Кнопка захвата для каждого клика
            ttk.Button(click_frame, text="📷 Захватить", 
                      command=lambda x=var_x, y=var_y: self.capture_coordinates(x, y),
                      width=10).pack(side='left', padx=5)
            
            self.var_group6_clicks.append((var_x, var_y))
        
        # Описание
        desc6_frame = ttk.Frame(group6_frame)
        desc6_frame.pack(fill='x', pady=5)
        
        ttk.Label(desc6_frame, text="Каждый из 5 триггеров группы 6 использует свои уникальные координаты для клика", 
                 font=('Arial', 9)).pack(anchor='w')
        
        # Кнопки управления
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="💾 Сохранить все координаты", 
                  command=self.save_all_coordinates,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🔄 Сбросить к значениям по умолчанию", 
                  command=self.reset_coordinates).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="📋 Копировать координаты в буфер", 
                  command=self.copy_coordinates_to_clipboard).pack(side='left', padx=5)
        
        # Статус
        status_frame = ttk.LabelFrame(scrollable_frame, text="Статус", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.label_coordinates_status = ttk.Label(status_frame, text="Координаты не сохранены", foreground='red')
        self.label_coordinates_status.pack(anchor='w', pady=2)
        
        ttk.Label(status_frame, text="Все координаты указываются относительно верхнего левого угла каждого окна", 
                 font=('Arial', 9)).pack(anchor='w', pady=2)
        
        # Упаковываем canvas и scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def capture_coordinates(self, var_x, var_y):
        """Захватывает текущие координаты курсора"""
        try:
            # Даем время пользователю переместить курсор
            self.log_message("📷 Переместите курсор в нужную позицию и нажмите Enter...", 'INFO')
            messagebox.showinfo("Захват координат", "Переместите курсор в нужную позицию и нажмите OK")
            
            # Получаем текущие координаты курсора
            x, y = pyautogui.position()
            
            # Устанавливаем значения в переменные
            var_x.set(x)
            var_y.set(y)
            
            self.log_message(f"📷 Координаты захвачены: ({x}, {y})", 'SUCCESS')
            messagebox.showinfo("Успех", f"Координаты захвачены: X={x}, Y={y}")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка захвата координат: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка захвата координат: {e}")
    
    def save_all_coordinates(self):
        """Сохраняет все координаты в конфигурацию"""
        try:
            # Группа 1: 2 клика
            self.config['group1_clicks'] = [
                {'x': self.var_group1_click1_x.get(), 'y': self.var_group1_click1_y.get()},
                {'x': self.var_group1_click2_x.get(), 'y': self.var_group1_click2_y.get()}
            ]
            
            # Группа 2: 1 клик
            self.config['group2_click'] = {
                'x': self.var_group2_click_x.get(), 
                'y': self.var_group2_click_y.get()
            }
            
            # Группа 3: 1 клик
            self.config['group3_click'] = {
                'x': self.var_group3_click_x.get(), 
                'y': self.var_group3_click_y.get()
            }
            
            # Группа 4: 1 клик (для всех 20 триггеров)
            self.config['group4_click'] = {
                'x': self.var_group4_click_x.get(), 
                'y': self.var_group4_click_y.get()
            }
            
            # Группа 5: КЛИК + ПАРОЛЬ + КЛИК
            self.config['group5_trigger'] = {
                'first_click': {'x': self.var_group5_click1_x.get(), 'y': self.var_group5_click1_y.get()},
                'password': self.var_group5_password.get(),
                'second_click': {'x': self.var_group5_click2_x.get(), 'y': self.var_group5_click2_y.get()}
            }
            
            # Группа 6: 5 разных кликов
            self.config['group6_clicks'] = []
            for i in range(5):
                if i < len(self.var_group6_clicks):
                    var_x, var_y = self.var_group6_clicks[i]
                    self.config['group6_clicks'].append({
                        'x': var_x.get(),
                        'y': var_y.get()
                    })
            
            self.save_config()
            
            self.label_coordinates_status.config(text="✅ Все координаты сохранены", foreground='green')
            self.log_message("💾 Все координаты сохранены в конфигурацию", 'SUCCESS')
            messagebox.showinfo("Успех", "Координаты для всех групп сохранены!")
            
        except Exception as e:
            self.label_coordinates_status.config(text="❌ Ошибка сохранения", foreground='red')
            self.log_message(f"❌ Ошибка сохранения координат: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def reset_coordinates(self):
        """Сбрасывает координаты к значениям по умолчанию"""
        try:
            # Группа 1
            self.var_group1_click1_x.set(100)
            self.var_group1_click1_y.set(100)
            self.var_group1_click2_x.set(150)
            self.var_group1_click2_y.set(150)
            
            # Группа 2
            self.var_group2_click_x.set(100)
            self.var_group2_click_y.set(100)
            
            # Группа 3
            self.var_group3_click_x.set(100)
            self.var_group3_click_y.set(100)
            
            # Группа 4
            self.var_group4_click_x.set(100)
            self.var_group4_click_y.set(100)
            
            # Группа 5
            self.var_group5_click1_x.set(100)
            self.var_group5_click1_y.set(100)
            self.var_group5_password.set('password01')
            self.var_group5_click2_x.set(150)
            self.var_group5_click2_y.set(150)
            
            # Группа 6
            for i in range(5):
                if i < len(self.var_group6_clicks):
                    var_x, var_y = self.var_group6_clicks[i]
                    var_x.set(100 + i*20)
                    var_y.set(100 + i*20)
            
            self.label_coordinates_status.config(text="Координаты сброшены к значениям по умолчанию", foreground='orange')
            self.log_message("↩️ Координаты сброшены к значениям по умолчанию", 'INFO')
            messagebox.showinfo("Сброс", "Координаты сброшены к значениям по умолчанию!")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка сброса координат: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка сброса: {e}")
    
    def copy_coordinates_to_clipboard(self):
        """Копирует все координаты в буфер обмена"""
        try:
            coordinates_text = "КООРДИНАТЫ ВСЕХ ГРУПП:\n\n"
            
            # Группа 1
            coordinates_text += "ГРУППА 1 (2 клика):\n"
            coordinates_text += f"  Клик 1: X={self.var_group1_click1_x.get()}, Y={self.var_group1_click1_y.get()}\n"
            coordinates_text += f"  Клик 2: X={self.var_group1_click2_x.get()}, Y={self.var_group1_click2_y.get()}\n\n"
            
            # Группа 2
            coordinates_text += "ГРУППА 2 (1 клик):\n"
            coordinates_text += f"  Клик: X={self.var_group2_click_x.get()}, Y={self.var_group2_click_y.get()}\n\n"
            
            # Группа 3
            coordinates_text += "ГРУППА 3 (1 клик):\n"
            coordinates_text += f"  Клик: X={self.var_group3_click_x.get()}, Y={self.var_group3_click_y.get()}\n\n"
            
            # Группа 4
            coordinates_text += "ГРУППА 4 (1 клик для 20 триггеров):\n"
            coordinates_text += f"  Клик: X={self.var_group4_click_x.get()}, Y={self.var_group4_click_y.get()}\n\n"
            
            # Группа 5
            coordinates_text += "ГРУППА 5 (клик + пароль + клик):\n"
            coordinates_text += f"  Клик 1: X={self.var_group5_click1_x.get()}, Y={self.var_group5_click1_y.get()}\n"
            coordinates_text += f"  Пароль: {self.var_group5_password.get()}\n"
            coordinates_text += f"  Клик 2: X={self.var_group5_click2_x.get()}, Y={self.var_group5_click2_y.get()}\n\n"
            
            # Группа 6
            coordinates_text += "ГРУППА 6 (5 разных кликов):\n"
            for i in range(5):
                if i < len(self.var_group6_clicks):
                    var_x, var_y = self.var_group6_clicks[i]
                    coordinates_text += f"  Клик {i+1}: X={var_x.get()}, Y={var_y.get()}\n"
            
            # Копируем в буфер обмена
            self.root.clipboard_clear()
            self.root.clipboard_append(coordinates_text)
            
            self.log_message("📋 Координаты скопированы в буфер обмена", 'SUCCESS')
            messagebox.showinfo("Скопировано", "Координаты всех групп скопированы в буфер обмена!")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка копирования в буфер обмена: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка копирования: {e}")
    
    def setup_settings_tab(self):
        """Вкладка настройки скорости работы скрипта"""
        title_frame = ttk.Frame(self.tab_settings)
        title_frame.pack(fill='x', pady=10)
        
        ttk.Label(title_frame, text="⚙️ Настройки скорости работы скрипта", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(title_frame, text="Регулировка скорости выполнения различных операций").pack()
        
        # Создаем контейнер с прокруткой
        container = ttk.Frame(self.tab_settings)
        container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Создаем canvas и скроллбар
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Основные настройки скорости
        speed_frame = ttk.LabelFrame(scrollable_frame, text="Настройки скорости", padding=10)
        speed_frame.pack(fill='x', padx=10, pady=5)
        
        # Скорость детекции
        detection_frame = ttk.Frame(speed_frame)
        detection_frame.pack(fill='x', pady=5)
        
        ttk.Label(detection_frame, text="Скорость детекции (коэффициент):").pack(side='left', padx=5)
        self.var_detection_speed = tk.DoubleVar(value=self.config['script_speed']['detection_speed'])
        detection_scale = ttk.Scale(detection_frame, from_=0.1, to=5.0, variable=self.var_detection_speed, 
                                   orient='horizontal', length=200)
        detection_scale.pack(side='left', padx=5)
        self.label_detection_speed = ttk.Label(detection_frame, text=f"{self.var_detection_speed.get():.1f}x")
        self.label_detection_speed.pack(side='left', padx=5)
        self.var_detection_speed.trace_add('write', lambda *args: self.update_detection_speed_label())
        
        ttk.Label(detection_frame, text="(1.0 = нормальная скорость)").pack(side='left', padx=5)
        
        # Скорость действий
        action_frame = ttk.Frame(speed_frame)
        action_frame.pack(fill='x', pady=5)
        
        ttk.Label(action_frame, text="Скорость действий (коэффициент):").pack(side='left', padx=5)
        self.var_action_speed = tk.DoubleVar(value=self.config['script_speed']['action_speed'])
        action_scale = ttk.Scale(action_frame, from_=0.1, to=5.0, variable=self.var_action_speed, 
                                orient='horizontal', length=200)
        action_scale.pack(side='left', padx=5)
        self.label_action_speed = ttk.Label(action_frame, text=f"{self.var_action_speed.get():.1f}x")
        self.label_action_speed.pack(side='left', padx=5)
        self.var_action_speed.trace_add('write', lambda *args: self.update_action_speed_label())
        
        ttk.Label(action_frame, text="(1.0 = нормальная скорость)").pack(side='left', padx=5)
        
        # Скорость восстановления
        recovery_frame = ttk.Frame(speed_frame)
        recovery_frame.pack(fill='x', pady=5)
        
        ttk.Label(recovery_frame, text="Скорость восстановления (коэффициент):").pack(side='left', padx=5)
        self.var_recovery_speed = tk.DoubleVar(value=self.config['script_speed']['recovery_speed'])
        recovery_scale = ttk.Scale(recovery_frame, from_=0.1, to=5.0, variable=self.var_recovery_speed, 
                                  orient='horizontal', length=200)
        recovery_scale.pack(side='left', padx=5)
        self.label_recovery_speed = ttk.Label(recovery_frame, text=f"{self.var_recovery_speed.get():.1f}x")
        self.label_recovery_speed.pack(side='left', padx=5)
        self.var_recovery_speed.trace_add('write', lambda *args: self.update_recovery_speed_label())
        
        ttk.Label(recovery_frame, text="(1.0 = нормальная скорость)").pack(side='left', padx=5)
        
        # Минимальная и максимальная задержка
        delays_frame = ttk.LabelFrame(scrollable_frame, text="Настройки задержек", padding=10)
        delays_frame.pack(fill='x', padx=10, pady=5)
        
        # Минимальная задержка
        min_delay_frame = ttk.Frame(delays_frame)
        min_delay_frame.pack(fill='x', pady=5)
        
        ttk.Label(min_delay_frame, text="Минимальная задержка (сек):").pack(side='left', padx=5)
        self.var_min_delay = tk.DoubleVar(value=self.config['script_speed']['min_delay'])
        ttk.Spinbox(min_delay_frame, from_=0.01, to=1.0, increment=0.01, textvariable=self.var_min_delay, width=8).pack(side='left', padx=5)
        
        # Максимальная задержка
        max_delay_frame = ttk.Frame(delays_frame)
        max_delay_frame.pack(fill='x', pady=5)
        
        ttk.Label(max_delay_frame, text="Максимальная задержка (сек):").pack(side='left', padx=5)
        self.var_max_delay = tk.DoubleVar(value=self.config['script_speed']['max_delay'])
        ttk.Spinbox(max_delay_frame, from_=0.1, to=5.0, increment=0.1, textvariable=self.var_max_delay, width=8).pack(side='left', padx=5)
        
        # Описание
        desc_frame = ttk.LabelFrame(scrollable_frame, text="Описание", padding=10)
        desc_frame.pack(fill='x', padx=10, pady=5)
        
        description = """
        Настройки скорости работы скрипта:
        
        1. Скорость детекции - влияет на частоту проверки окон на наличие триггеров.
           • Высокие значения (>1.0) ускоряют проверку, но увеличивают нагрузку на систему.
           • Низкие значения (<1.0) замедляют проверку, снижая нагрузку.
        
        2. Скорость действий - влияет на скорость выполнения действий (клики, движения джойстика и т.д.).
           • Высокие значения (>1.0) ускоряют выполнение действий.
           • Низкие значения (<1.0) замедляют выполнение, делая его более естественным.
        
        3. Скорость восстановления - влияет на скорость обработки триггеров.
           • Высокие значения (>1.0) ускоряют восстановление окон.
           • Низкие значения (<1.0) замедляют восстановление.
        
        4. Минимальная и максимальная задержка - ограничивают случайные задержки между действиями.
        
        Рекомендации:
        • Для максимальной производительности: 2.0-3.0
        • Для баланса производительности и естественности: 1.0-1.5
        • Для максимальной естественности: 0.5-0.8
        """
        
        ttk.Label(desc_frame, text=description, justify='left').pack(anchor='w')
        
        # Кнопки управления
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="💾 Сохранить настройки скорости", 
                  command=self.save_speed_settings,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🔄 Применить сейчас", 
                  command=self.apply_speed_settings).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="↩️ Сбросить к значениям по умолчанию", 
                  command=self.reset_speed_settings).pack(side='left', padx=5)
        
        # Отображение текущих настроек скорости
        status_frame = ttk.LabelFrame(scrollable_frame, text="Текущие настройки скорости", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.label_current_speed = ttk.Label(status_frame, 
            text=f"Детекция: {self.detection_speed:.1f}x | Действия: {self.action_speed:.1f}x | Восстановление: {self.recovery_speed:.1f}x")
        self.label_current_speed.pack(anchor='w', pady=2)
        
        self.label_current_delays = ttk.Label(status_frame, 
            text=f"Задержки: {self.config['script_speed']['min_delay']} - {self.config['script_speed']['max_delay']} сек")
        self.label_current_delays.pack(anchor='w', pady=2)
        
        # Упаковываем canvas и scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def update_detection_speed_label(self):
        """Обновляет метку скорости детекции"""
        self.label_detection_speed.config(text=f"{self.var_detection_speed.get():.1f}x")
    
    def update_action_speed_label(self):
        """Обновляет метку скорости действий"""
        self.label_action_speed.config(text=f"{self.var_action_speed.get():.1f}x")
    
    def update_recovery_speed_label(self):
        """Обновляет метку скорости восстановления"""
        self.label_recovery_speed.config(text=f"{self.var_recovery_speed.get():.1f}x")
    
    def save_speed_settings(self):
        """Сохраняет настройки скорости"""
        try:
            self.config['script_speed']['detection_speed'] = self.var_detection_speed.get()
            self.config['script_speed']['action_speed'] = self.var_action_speed.get()
            self.config['script_speed']['recovery_speed'] = self.var_recovery_speed.get()
            self.config['script_speed']['min_delay'] = self.var_min_delay.get()
            self.config['script_speed']['max_delay'] = self.var_max_delay.get()
            
            self.save_config()
            
            # Применяем настройки
            self.apply_speed_settings()
            
            # Обновляем отображение текущих настроек
            self.update_speed_display()
            
            self.log_message("💾 Настройки скорости сохранены", 'SUCCESS')
            messagebox.showinfo("Успех", "Настройки скорости сохранены!")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения настроек скорости: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def apply_speed_settings(self):
        """Применяет настройки скорости"""
        try:
            self.detection_speed = self.var_detection_speed.get()
            self.action_speed = self.var_action_speed.get()
            self.recovery_speed = self.var_recovery_speed.get()
            
            # Обновляем отображение текущих настроек
            self.update_speed_display()
            
            self.log_message(f"⚡ Скорость применена: детекция={self.detection_speed:.1f}x, действия={self.action_speed:.1f}x, восстановление={self.recovery_speed:.1f}x", 'INFO')
            
        except Exception as e:
            self.log_message(f"❌ Ошибка применения настроек скорости: {e}", 'ERROR')
    
    def update_speed_display(self):
        """Обновляет отображение текущих настроек скорости"""
        try:
            self.label_current_speed.config(
                text=f"Детекция: {self.detection_speed:.1f}x | Действия: {self.action_speed:.1f}x | Восстановление: {self.recovery_speed:.1f}x")
            self.label_current_delays.config(
                text=f"Задержки: {self.config['script_speed']['min_delay']} - {self.config['script_speed']['max_delay']} сек")
        except Exception as e:
            print(f"Ошибка обновления отображения скорости: {e}")
    
    def reset_speed_settings(self):
        """Сбрасывает настройки скорости к значениям по умолчанию"""
        try:
            self.var_detection_speed.set(1.0)
            self.var_action_speed.set(1.0)
            self.var_recovery_speed.set(1.0)
            self.var_min_delay.set(0.05)
            self.var_max_delay.set(0.5)
            
            self.update_detection_speed_label()
            self.update_action_speed_label()
            self.update_recovery_speed_label()
            
            self.log_message("↩️ Настройки скорости сброшены к значениям по умолчанию", 'INFO')
            
        except Exception as e:
            self.log_message(f"❌ Ошибка сброса настроек скорости: {e}", 'ERROR')
    
    def setup_actions_tab(self):
        """Вкладка настройки 5 отдельных действий"""
        title_frame = ttk.Frame(self.tab_actions)
        title_frame.pack(fill='x', pady=10)
        
        ttk.Label(title_frame, text="🎮 Настройки 5 отдельных действий", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(title_frame, text="Настройка 5 отдельных действий, выполняемых в каждом окне").pack()
        
        # Создаем контейнер с прокруткой
        container = ttk.Frame(self.tab_actions)
        container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Создаем canvas и скроллбар
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Основные настройки
        main_frame = ttk.LabelFrame(scrollable_frame, text="Основные настройки", padding=10)
        main_frame.pack(fill='x', padx=10, pady=5)
        
        # Включение/отключение действий
        enable_frame = ttk.Frame(main_frame)
        enable_frame.pack(fill='x', pady=5)
        
        action_settings = self.config.get('action_settings', {})
        self.var_actions_enabled = tk.BooleanVar(value=action_settings.get('enabled', True))
        ttk.Checkbutton(enable_frame, text="Включить разнообразные действия", 
                       variable=self.var_actions_enabled).pack(side='left', padx=5)
        
        # Включение/отключение отдельных действий
        enabled_actions = action_settings.get('enabled_actions', [True, True, True, True, True])
        self.var_enabled_actions = []
        for i in range(5):
            var = tk.BooleanVar(value=enabled_actions[i] if i < len(enabled_actions) else True)
            self.var_enabled_actions.append(var)
            ttk.Checkbutton(enable_frame, text=f"Действие {i+1}", 
                           variable=var).pack(side='left', padx=2)
        
        # Порядок выполнения
        order_frame = ttk.Frame(main_frame)
        order_frame.pack(fill='x', pady=5)
        
        ttk.Label(order_frame, text="Порядок окон:").pack(side='left', padx=5)
        self.var_window_order = tk.StringVar(value=action_settings.get('window_order', 'sequential'))
        order_combo = ttk.Combobox(order_frame, textvariable=self.var_window_order, 
                                  values=['sequential', 'random'], state='readonly', width=10)
        order_combo.pack(side='left', padx=5)
        ttk.Label(order_frame, text="(sequential = по порядку, random = случайно)").pack(side='left', padx=5)
        
        # Случайный порядок действий
        self.var_random_order = tk.BooleanVar(value=action_settings.get('random_order', True))
        ttk.Checkbutton(main_frame, text="Случайный выбор действий для каждого окна", 
                       variable=self.var_random_order).pack(anchor='w', pady=2)
        
        # Интервал между действиями
        interval_frame = ttk.Frame(main_frame)
        interval_frame.pack(fill='x', pady=5)
        
        ttk.Label(interval_frame, text="Интервал между действиями (сек):").pack(side='left', padx=5)
        self.var_action_interval = tk.IntVar(value=action_settings.get('action_interval', 2))
        ttk.Spinbox(interval_frame, from_=1, to=60, textvariable=self.var_action_interval, width=8).pack(side='left', padx=5)
        
        # Случайные задержки
        self.var_random_delay = tk.BooleanVar(value=action_settings.get('random_delay', True))
        ttk.Checkbutton(main_frame, text="Добавлять случайные задержки", 
                       variable=self.var_random_delay).pack(anchor='w', pady=2)
        
        # Настройки каждого отдельного действия
        actions_list = action_settings.get('actions', [])
        
        # Действие 1: Простой клик по координатам
        action1_frame = ttk.LabelFrame(scrollable_frame, text="Действие 1: Простой клик по координатам", padding=10)
        action1_frame.pack(fill='x', padx=10, pady=5)
        
        # Вероятность выполнения
        chance1_frame = ttk.Frame(action1_frame)
        chance1_frame.pack(fill='x', pady=5)
        
        ttk.Label(chance1_frame, text="Вероятность выполнения (%):").pack(side='left', padx=5)
        self.var_action1_chance = tk.IntVar(value=self.get_action_chance(actions_list, 'action1_single_click', 20))
        chance1_scale = ttk.Scale(chance1_frame, from_=0, to=100, variable=self.var_action1_chance, orient='horizontal', length=150)
        chance1_scale.pack(side='left', padx=5)
        self.label_action1_chance = ttk.Label(chance1_frame, text=f"{self.var_action1_chance.get()}%")
        self.label_action1_chance.pack(side='left', padx=5)
        self.var_action1_chance.trace_add('write', lambda *args: self.update_action1_chance())
        
        # Координаты клика
        coords1_frame = ttk.Frame(action1_frame)
        coords1_frame.pack(fill='x', pady=5)
        
        ttk.Label(coords1_frame, text="Координата X:").pack(side='left', padx=5)
        self.var_action1_x = tk.IntVar(value=self.get_action_param(actions_list, 'action1_single_click', 'x', 200))
        ttk.Spinbox(coords1_frame, from_=0, to=1000, textvariable=self.var_action1_x, width=8).pack(side='left', padx=5)
        
        ttk.Label(coords1_frame, text="Координата Y:").pack(side='left', padx=5)
        self.var_action1_y = tk.IntVar(value=self.get_action_param(actions_list, 'action1_single_click', 'y', 200))
        ttk.Spinbox(coords1_frame, from_=0, to=1000, textvariable=self.var_action1_y, width=8).pack(side='left', padx=5)
        
        # Действие 2: 4 обычных клика по разным координатам
        action2_frame = ttk.LabelFrame(scrollable_frame, text="Действие 2: 4 обычных клика по разным координатам", padding=10)
        action2_frame.pack(fill='x', padx=10, pady=5)
        
        # Вероятность выполнения
        chance2_frame = ttk.Frame(action2_frame)
        chance2_frame.pack(fill='x', pady=5)
        
        ttk.Label(chance2_frame, text="Вероятность выполнения (%):").pack(side='left', padx=5)
        self.var_action2_chance = tk.IntVar(value=self.get_action_chance(actions_list, 'action2_four_single_clicks', 20))
        chance2_scale = ttk.Scale(chance2_frame, from_=0, to=100, variable=self.var_action2_chance, orient='horizontal', length=150)
        chance2_scale.pack(side='left', padx=5)
        self.label_action2_chance = ttk.Label(chance2_frame, text=f"{self.var_action2_chance.get()}%")
        self.label_action2_chance.pack(side='left', padx=5)
        self.var_action2_chance.trace_add('write', lambda *args: self.update_action2_chance())
        
        # Координаты 4-х кликов
        clicks_config = self.get_action_param(actions_list, 'action2_four_single_clicks', 'clicks', [
            {'x': 300, 'y': 300},
            {'x': 320, 'y': 320},
            {'x': 340, 'y': 340},
            {'x': 360, 'y': 360}
        ])
        
        self.var_action2_clicks = []
        for i in range(4):
            click_frame = ttk.Frame(action2_frame)
            click_frame.pack(fill='x', pady=2)
            
            ttk.Label(click_frame, text=f"Клик {i+1} - X:").pack(side='left', padx=5)
            var_x = tk.IntVar(value=clicks_config[i]['x'] if i < len(clicks_config) else 300 + i*20)
            ttk.Spinbox(click_frame, from_=0, to=1000, textvariable=var_x, width=8).pack(side='left', padx=5)
            
            ttk.Label(click_frame, text="Y:").pack(side='left', padx=5)
            var_y = tk.IntVar(value=clicks_config[i]['y'] if i < len(clicks_config) else 300 + i*20)
            ttk.Spinbox(click_frame, from_=0, to=1000, textvariable=var_y, width=8).pack(side='left', padx=5)
            
            self.var_action2_clicks.append((var_x, var_y))
        
        # Действие 3: 9 отдельных кликов
        action3_frame = ttk.LabelFrame(scrollable_frame, text="Действие 3: 9 отдельных кликов", padding=10)
        action3_frame.pack(fill='x', padx=10, pady=5)
        
        # Вероятность выполнения
        chance3_frame = ttk.Frame(action3_frame)
        chance3_frame.pack(fill='x', pady=5)
        
        ttk.Label(chance3_frame, text="Вероятность выполнения (%):").pack(side='left', padx=5)
        self.var_action3_chance = tk.IntVar(value=self.get_action_chance(actions_list, 'action3_nine_clicks', 15))
        chance3_scale = ttk.Scale(chance3_frame, from_=0, to=100, variable=self.var_action3_chance, orient='horizontal', length=150)
        chance3_scale.pack(side='left', padx=5)
        self.label_action3_chance = ttk.Label(chance3_frame, text=f"{self.var_action3_chance.get()}%")
        self.label_action3_chance.pack(side='left', padx=5)
        self.var_action3_chance.trace_add('write', lambda *args: self.update_action3_chance())
        
        # Координаты 9 кликов
        clicks_config = self.get_action_param(actions_list, 'action3_nine_clicks', 'clicks', [
            {'x': 400, 'y': 400, 'type': 'click'},
            {'x': 420, 'y': 420, 'type': 'click'},
            {'x': 440, 'y': 440, 'type': 'click'},
            {'x': 460, 'y': 460, 'type': 'click'},
            {'x': 480, 'y': 480, 'type': 'click'},
            {'x': 500, 'y': 500, 'type': 'click'},
            {'x': 520, 'y': 520, 'type': 'click'},
            {'x': 540, 'y': 540, 'type': 'click'},
            {'x': 560, 'y': 560, 'type': 'click'}
        ])
        
        self.var_action3_clicks = []
        for i in range(9):
            click_frame = ttk.Frame(action3_frame)
            click_frame.pack(fill='x', pady=2)
            
            ttk.Label(click_frame, text=f"Клик {i+1} - X:").pack(side='left', padx=5)
            var_x = tk.IntVar(value=clicks_config[i]['x'] if i < len(clicks_config) else 400 + i*20)
            ttk.Spinbox(click_frame, from_=0, to=1000, textvariable=var_x, width=8).pack(side='left', padx=5)
            
            ttk.Label(click_frame, text="Y:").pack(side='left', padx=5)
            var_y = tk.IntVar(value=clicks_config[i]['y'] if i < len(clicks_config) else 400 + i*20)
            ttk.Spinbox(click_frame, from_=0, to=1000, textvariable=var_y, width=8).pack(side='left', padx=5)
            
            self.var_action3_clicks.append((var_x, var_y))
        
        # Действие 4: Джойстик фикс (45,135,225,315°) + клик
        action4_frame = ttk.LabelFrame(scrollable_frame, text="Действие 4: Джойстик фикс (случайное из 45,135,225,315°) + клик", padding=10)
        action4_frame.pack(fill='x', padx=10, pady=5)
        
        # Вероятность выполнения
        chance4_frame = ttk.Frame(action4_frame)
        chance4_frame.pack(fill='x', pady=5)
        
        ttk.Label(chance4_frame, text="Вероятность выполнения (%):").pack(side='left', padx=5)
        self.var_action4_chance = tk.IntVar(value=self.get_action_chance(actions_list, 'action4_joystick_random_fixed', 15))
        chance4_scale = ttk.Scale(chance4_frame, from_=0, to=100, variable=self.var_action4_chance, orient='horizontal', length=150)
        chance4_scale.pack(side='left', padx=5)
        self.label_action4_chance = ttk.Label(chance4_frame, text=f"{self.var_action4_chance.get()}%")
        self.label_action4_chance.pack(side='left', padx=5)
        self.var_action4_chance.trace_add('write', lambda *args: self.update_action4_chance())
        
        # Координаты начала движения джойстика
        joystick_start_frame = ttk.LabelFrame(action4_frame, text="Начало движения джойстика", padding=5)
        joystick_start_frame.pack(fill='x', pady=5)
        
        start_x_frame = ttk.Frame(joystick_start_frame)
        start_x_frame.pack(fill='x', pady=2)
        
        ttk.Label(start_x_frame, text="Координата X:").pack(side='left', padx=5)
        self.var_action4_joystick_x = tk.IntVar(value=self.get_action_param(actions_list, 'action4_joystick_random_fixed', 'joystick_start_x', 350))
        ttk.Spinbox(start_x_frame, from_=0, to=1000, textvariable=self.var_action4_joystick_x, width=8).pack(side='left', padx=5)
        
        start_y_frame = ttk.Frame(joystick_start_frame)
        start_y_frame.pack(fill='x', pady=2)
        
        ttk.Label(start_y_frame, text="Координата Y:").pack(side='left', padx=5)
        self.var_action4_joystick_y = tk.IntVar(value=self.get_action_param(actions_list, 'action4_joystick_random_fixed', 'joystick_start_y', 350))
        ttk.Spinbox(start_y_frame, from_=0, to=1000, textvariable=self.var_action4_joystick_y, width=8).pack(side='left', padx=5)
        
        # Параметры движения
        move_params_frame = ttk.LabelFrame(action4_frame, text="Параметры движения", padding=5)
        move_params_frame.pack(fill='x', pady=5)
        
        # Дистанция
        distance_frame = ttk.Frame(move_params_frame)
        distance_frame.pack(fill='x', pady=2)
        
        ttk.Label(distance_frame, text="Дистанция (пиксели):").pack(side='left', padx=5)
        self.var_action4_distance = tk.IntVar(value=self.get_action_param(actions_list, 'action4_joystick_random_fixed', 'distance', 100))
        ttk.Spinbox(distance_frame, from_=10, to=500, textvariable=self.var_action4_distance, width=8).pack(side='left', padx=5)
        
        # Длительность
        duration_frame = ttk.Frame(move_params_frame)
        duration_frame.pack(fill='x', pady=2)
        
        ttk.Label(duration_frame, text="Длительность (сек):").pack(side='left', padx=5)
        self.var_action4_duration = tk.DoubleVar(value=self.get_action_param(actions_list, 'action4_joystick_random_fixed', 'duration', 2.0))
        ttk.Spinbox(duration_frame, from_=0.5, to=10.0, increment=0.5, textvariable=self.var_action4_duration, width=8).pack(side='left', padx=5)
        
        # Координаты клика после движения
        click_coords_frame = ttk.LabelFrame(action4_frame, text="Координаты клика после движения", padding=5)
        click_coords_frame.pack(fill='x', pady=5)
        
        click_x_frame = ttk.Frame(click_coords_frame)
        click_x_frame.pack(fill='x', pady=2)
        
        ttk.Label(click_x_frame, text="Координата X:").pack(side='left', padx=5)
        self.var_action4_click_x = tk.IntVar(value=self.get_action_param(actions_list, 'action4_joystick_random_fixed', 'click_x', 450))
        ttk.Spinbox(click_x_frame, from_=0, to=1000, textvariable=self.var_action4_click_x, width=8).pack(side='left', padx=5)
        
        click_y_frame = ttk.Frame(click_coords_frame)
        click_y_frame.pack(fill='x', pady=2)
        
        ttk.Label(click_y_frame, text="Координата Y:").pack(side='left', padx=5)
        self.var_action4_click_y = tk.IntVar(value=self.get_action_param(actions_list, 'action4_joystick_random_fixed', 'click_y', 450))
        ttk.Spinbox(click_y_frame, from_=0, to=1000, textvariable=self.var_action4_click_y, width=8).pack(side='left', padx=5)
        
        # Информация о направлении
        info_frame = ttk.Frame(action4_frame)
        info_frame.pack(fill='x', pady=5)

        ttk.Label(info_frame, text="Направление: случайное из [33-55°, 115-150°, 200-250°, 300-330°]").pack(anchor='w')

        # Действие 5: Джойстик 45-135 градусов + двойной клик
        action5_frame = ttk.LabelFrame(scrollable_frame, text="Действие 5: Джойстик 45-135° + двойной клик", padding=10)
        action5_frame.pack(fill='x', padx=10, pady=5)
        
        # Вероятность выполнения
        chance5_frame = ttk.Frame(action5_frame)
        chance5_frame.pack(fill='x', pady=5)
        
        ttk.Label(chance5_frame, text="Вероятность выполнения (%):").pack(side='left', padx=5)
        self.var_action5_chance = tk.IntVar(value=self.get_action_chance(actions_list, 'action5_joystick_random_double_click', 15))
        chance5_scale = ttk.Scale(chance5_frame, from_=0, to=100, variable=self.var_action5_chance, orient='horizontal', length=150)
        chance5_scale.pack(side='left', padx=5)
        self.label_action5_chance = ttk.Label(chance5_frame, text=f"{self.var_action5_chance.get()}%")
        self.label_action5_chance.pack(side='left', padx=5)
        self.var_action5_chance.trace_add('write', lambda *args: self.update_action5_chance())
        
        # Координаты начала движения джойстика
        joystick5_start_frame = ttk.LabelFrame(action5_frame, text="Начало движения джойстика", padding=5)
        joystick5_start_frame.pack(fill='x', pady=5)
        
        start5_x_frame = ttk.Frame(joystick5_start_frame)
        start5_x_frame.pack(fill='x', pady=2)
        
        ttk.Label(start5_x_frame, text="Координата X:").pack(side='left', padx=5)
        self.var_action5_joystick_x = tk.IntVar(value=self.get_action_param(actions_list, 'action5_joystick_random_double_click', 'joystick_start_x', 350))
        ttk.Spinbox(start5_x_frame, from_=0, to=1000, textvariable=self.var_action5_joystick_x, width=8).pack(side='left', padx=5)
        
        start5_y_frame = ttk.Frame(joystick5_start_frame)
        start5_y_frame.pack(fill='x', pady=2)
        
        ttk.Label(start5_y_frame, text="Координата Y:").pack(side='left', padx=5)
        self.var_action5_joystick_y = tk.IntVar(value=self.get_action_param(actions_list, 'action5_joystick_random_double_click', 'joystick_start_y', 350))
        ttk.Spinbox(start5_y_frame, from_=0, to=1000, textvariable=self.var_action5_joystick_y, width=8).pack(side='left', padx=5)
        
        # Параметры движения
        move5_params_frame = ttk.LabelFrame(action5_frame, text="Параметры движения", padding=5)
        move5_params_frame.pack(fill='x', pady=5)
        
        # Дистанция
        distance5_frame = ttk.Frame(move5_params_frame)
        distance5_frame.pack(fill='x', pady=2)
        
        ttk.Label(distance5_frame, text="Дистанция (пиксели):").pack(side='left', padx=5)
        self.var_action5_distance = tk.IntVar(value=self.get_action_param(actions_list, 'action5_joystick_random_double_click', 'distance', 100))
        ttk.Spinbox(distance5_frame, from_=10, to=500, textvariable=self.var_action5_distance, width=8).pack(side='left', padx=5)
        
        # Длительность
        duration5_min_frame = ttk.Frame(move5_params_frame)
        duration5_min_frame.pack(fill='x', pady=2)
        
        ttk.Label(duration5_min_frame, text="Мин. длительность (сек):").pack(side='left', padx=5)
        self.var_action5_duration_min = tk.DoubleVar(value=self.get_action_param(actions_list, 'action5_joystick_random_double_click', 'duration_min', 1.0))
        ttk.Spinbox(duration5_min_frame, from_=0.5, to=10.0, increment=0.5, textvariable=self.var_action5_duration_min, width=8).pack(side='left', padx=5)
        
        duration5_max_frame = ttk.Frame(move5_params_frame)
        duration5_max_frame.pack(fill='x', pady=2)
        
        ttk.Label(duration5_max_frame, text="Макс. длительность (сек):").pack(side='left', padx=5)
        self.var_action5_duration_max = tk.DoubleVar(value=self.get_action_param(actions_list, 'action5_joystick_random_double_click', 'duration_max', 3.0))
        ttk.Spinbox(duration5_max_frame, from_=0.5, to=10.0, increment=0.5, textvariable=self.var_action5_duration_max, width=8).pack(side='left', padx=5)
        
        # Координаты двойного клика после движения
        click5_coords_frame = ttk.LabelFrame(action5_frame, text="Координаты двойного клика после движения", padding=5)
        click5_coords_frame.pack(fill='x', pady=5)
        
        click5_x_frame = ttk.Frame(click5_coords_frame)
        click5_x_frame.pack(fill='x', pady=2)
        
        ttk.Label(click5_x_frame, text="Координата X:").pack(side='left', padx=5)
        self.var_action5_click_x = tk.IntVar(value=self.get_action_param(actions_list, 'action5_joystick_random_double_click', 'click_x', 450))
        ttk.Spinbox(click5_x_frame, from_=0, to=1000, textvariable=self.var_action5_click_x, width=8).pack(side='left', padx=5)
        
        click5_y_frame = ttk.Frame(click5_coords_frame)
        click5_y_frame.pack(fill='x', pady=2)
        
        ttk.Label(click5_y_frame, text="Координата Y:").pack(side='left', padx=5)
        self.var_action5_click_y = tk.IntVar(value=self.get_action_param(actions_list, 'action5_joystick_random_double_click', 'click_y', 450))
        ttk.Spinbox(click5_y_frame, from_=0, to=1000, textvariable=self.var_action5_click_y, width=8).pack(side='left', padx=5)
        
        # Описание действия 5
        desc5_frame = ttk.Frame(action5_frame)
        desc5_frame.pack(fill='x', pady=5)

        ttk.Label(desc5_frame, text="Случайное направление 225-315°, случайная длительность в указанных пределах + двойной клик").pack(anchor='w')          
           
        # Кнопки управления
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="🚀 Тестовый запуск всех действий", 
                  command=self.test_all_actions,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="💾 Сохранить настройки действий", 
                  command=self.save_actions_settings).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🔄 Тест действия 3", 
                  command=lambda: self.test_single_action(3)).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🔄 Тест действия 5", 
                  command=lambda: self.test_single_action(5)).pack(side='left', padx=5)
            
        # Статус
        status_frame = ttk.LabelFrame(scrollable_frame, text="Статус", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.label_actions_status = ttk.Label(status_frame, text="Действия отключены", foreground='red')
        self.label_actions_status.pack(anchor='w', pady=2)
        
        ttk.Label(status_frame, text="Всего 5 отдельных действий").pack(anchor='w', pady=2)
        
        if self.last_action_time:
            last_time_str = self.last_action_time.strftime("%H:%M:%S %d.%m.%Y")
            ttk.Label(status_frame, text=f"Последнее выполнение: {last_time_str}").pack(anchor='w', pady=2)
        
        # ДОБАВЬТЕ ЭТОТ БЛОК - НАСТРОЙКИ ПАРОЛЯ:
        password_settings = self.config.get('password_input_settings', {
            'delay_before_password': 0.2,
            'delay_between_chars': 0.1,
            'min_delay_variation': 0.05,
            'max_delay_variation': 0.15
        })
        
        password_info = f"Настройки пароля: перед={password_settings['delay_before_password']}с, между={password_settings['delay_between_chars']}с"
        ttk.Label(status_frame, text=password_info, font=('Arial', 9)).pack(anchor='w', pady=2)
        
        # Упаковываем canvas и scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def update_action1_chance(self):
        """Обновляет метку шанса выполнения действия 1"""
        self.label_action1_chance.config(text=f"{self.var_action1_chance.get()}%")
    
    def update_action2_chance(self):
        """Обновляет метку шанса выполнения действия 2"""
        self.label_action2_chance.config(text=f"{self.var_action2_chance.get()}%")
    
    def update_action3_chance(self):
        """Обновляет метку шанса выполнения действия 3"""
        self.label_action3_chance.config(text=f"{self.var_action3_chance.get()}%")
    
    def update_action4_chance(self):
        """Обновляет метку шанса выполнения действия 4"""
        self.label_action4_chance.config(text=f"{self.var_action4_chance.get()}%")
    
    def update_action5_chance(self):
        """Обновляет метку шанса выполнения действия 5"""
        self.label_action5_chance.config(text=f"{self.var_action5_chance.get()}%")
    
    def test_single_action(self, action_num):
        """Тестирует одно действие"""
        if not self.windows_data:
            messagebox.showwarning("Предупреждение", "Сначала создайте сетку окон!")
            return
        
        if messagebox.askyesno("Тестовый запуск", f"Выполнить тестовое действие {action_num} сейчас?"):
            # Создаем конфиг для тестового действия
            if action_num == 1:
                action_config = {
                    'type': 'action1_single_click',
                    'x': self.var_action1_x.get(),
                    'y': self.var_action1_y.get(),
                    'chance': 100
                }
            elif action_num == 2:
                action_config = {
                    'type': 'action2_four_single_clicks',
                    'clicks': [
                        {'x': self.var_action2_clicks[0][0].get(), 'y': self.var_action2_clicks[0][1].get()},
                        {'x': self.var_action2_clicks[1][0].get(), 'y': self.var_action2_clicks[1][1].get()},
                        {'x': self.var_action2_clicks[2][0].get(), 'y': self.var_action2_clicks[2][1].get()},
                        {'x': self.var_action2_clicks[3][0].get(), 'y': self.var_action2_clicks[3][1].get()}
                    ],
                    'chance': 100
                }
            elif action_num == 3:
                action_config = {
                    'type': 'action3_nine_clicks',
                    'clicks': [
                        {'x': self.var_action3_clicks[0][0].get(), 'y': self.var_action3_clicks[0][1].get(), 'type': 'click'},
                        {'x': self.var_action3_clicks[1][0].get(), 'y': self.var_action3_clicks[1][1].get(), 'type': 'click'},
                        {'x': self.var_action3_clicks[2][0].get(), 'y': self.var_action3_clicks[2][1].get(), 'type': 'click'},
                        {'x': self.var_action3_clicks[3][0].get(), 'y': self.var_action3_clicks[3][1].get(), 'type': 'click'},
                        {'x': self.var_action3_clicks[4][0].get(), 'y': self.var_action3_clicks[4][1].get(), 'type': 'click'},
                        {'x': self.var_action3_clicks[5][0].get(), 'y': self.var_action3_clicks[5][1].get(), 'type': 'click'},
                        {'x': self.var_action3_clicks[6][0].get(), 'y': self.var_action3_clicks[6][1].get(), 'type': 'click'},
                        {'x': self.var_action3_clicks[7][0].get(), 'y': self.var_action3_clicks[7][1].get(), 'type': 'click'},
                        {'x': self.var_action3_clicks[8][0].get(), 'y': self.var_action3_clicks[8][1].get(), 'type': 'click'}
                    ],
                    'chance': 100
                }
            elif action_num == 4:
                action_config = {
                    'type': 'action4_joystick_random_fixed',
                    'joystick_start_x': self.var_action4_joystick_x.get(),
                    'joystick_start_y': self.var_action4_joystick_y.get(),
                    'distance': self.var_action4_distance.get(),
                    'duration': self.var_action4_duration.get(),
                    'click_x': self.var_action4_click_x.get(),
                    'click_y': self.var_action4_click_y.get(),
                    'chance': 100
                }
            elif action_num == 5:
                action_config = {
                    'type': 'action5_joystick_random_double_click',
                    'joystick_start_x': self.var_action5_joystick_x.get(),
                    'joystick_start_y': self.var_action5_joystick_y.get(),
                    'distance': self.var_action5_distance.get(),
                    'duration_min': self.var_action5_duration_min.get(),
                    'duration_max': self.var_action5_duration_max.get(),
                    'click_x': self.var_action5_click_x.get(),
                    'click_y': self.var_action5_click_y.get(),
                    'chance': 100
                }
            else:
                messagebox.showerror("Ошибка", f"Неизвестное действие {action_num}")
                return
            
            # Выполняем действие во всех окнах
            self.execute_specific_action(action_config)
            messagebox.showinfo("Успех", f"Тестовое действие {action_num} выполнено!")
    
    def test_all_actions(self):
        """Тестовый запуск всех действий"""
        if not self.windows_data:
            messagebox.showwarning("Предупреждение", "Сначала создайте сетку окон!")
            return
        
        if messagebox.askyesno("Тестовый запуск", "Выполнить тестовые действия сейчас? (по одному разу каждое)"):
            # Выполняем все 5 действий по порядку
            for action_num in range(1, 6):
                self.test_single_action(action_num)
                time.sleep(1)  # Пауза между действиями
    
    def save_actions_settings(self):
        """Сохраняет настройки действий"""
        try:
            # Основные настройки
            action_settings = self.config.get('action_settings', {})
            action_settings['enabled'] = self.var_actions_enabled.get()
            action_settings['action_interval'] = self.var_action_interval.get()
            action_settings['random_delay'] = self.var_random_delay.get()
            action_settings['random_order'] = self.var_random_order.get()
            action_settings['window_order'] = self.var_window_order.get()
            
            # Сохраняем информацию о включенных действиях
            enabled_actions = [var.get() for var in self.var_enabled_actions]
            action_settings['enabled_actions'] = enabled_actions
            
            # Создаем список действий
            actions_list = []
            
            # Действие 1
            actions_list.append({
                'type': 'action1_single_click',
                'x': self.var_action1_x.get(),
                'y': self.var_action1_y.get(),
                'chance': self.var_action1_chance.get()
            })
            
            # Действие 2 - 4 обычных клика
            actions_list.append({
                'type': 'action2_four_single_clicks',
                'clicks': [
                    {'x': self.var_action2_clicks[0][0].get(), 'y': self.var_action2_clicks[0][1].get()},
                    {'x': self.var_action2_clicks[1][0].get(), 'y': self.var_action2_clicks[1][1].get()},
                    {'x': self.var_action2_clicks[2][0].get(), 'y': self.var_action2_clicks[2][1].get()},
                    {'x': self.var_action2_clicks[3][0].get(), 'y': self.var_action2_clicks[3][1].get()}
                ],
                'chance': self.var_action2_chance.get()
            })
            
            # Действие 3 - 9 отдельных кликов
            actions_list.append({
                'type': 'action3_nine_clicks',
                'clicks': [
                    {'x': self.var_action3_clicks[0][0].get(), 'y': self.var_action3_clicks[0][1].get(), 'type': 'click'},
                    {'x': self.var_action3_clicks[1][0].get(), 'y': self.var_action3_clicks[1][1].get(), 'type': 'click'},
                    {'x': self.var_action3_clicks[2][0].get(), 'y': self.var_action3_clicks[2][1].get(), 'type': 'click'},
                    {'x': self.var_action3_clicks[3][0].get(), 'y': self.var_action3_clicks[3][1].get(), 'type': 'click'},
                    {'x': self.var_action3_clicks[4][0].get(), 'y': self.var_action3_clicks[4][1].get(), 'type': 'click'},
                    {'x': self.var_action3_clicks[5][0].get(), 'y': self.var_action3_clicks[5][1].get(), 'type': 'click'},
                    {'x': self.var_action3_clicks[6][0].get(), 'y': self.var_action3_clicks[6][1].get(), 'type': 'click'},
                    {'x': self.var_action3_clicks[7][0].get(), 'y': self.var_action3_clicks[7][1].get(), 'type': 'click'},
                    {'x': self.var_action3_clicks[8][0].get(), 'y': self.var_action3_clicks[8][1].get(), 'type': 'click'}
                ],
                'chance': self.var_action3_chance.get()
            })
            
            # Действие 4
            actions_list.append({
                'type': 'action4_joystick_random_fixed',
                'joystick_start_x': self.var_action4_joystick_x.get(),
                'joystick_start_y': self.var_action4_joystick_y.get(),
                'distance': self.var_action4_distance.get(),
                'duration': self.var_action4_duration.get(),
                'click_x': self.var_action4_click_x.get(),
                'click_y': self.var_action4_click_y.get(),
                'chance': self.var_action4_chance.get()
            })
            
            # Действие 5
            actions_list.append({
                'type': 'action5_joystick_random_double_click',
                'joystick_start_x': self.var_action5_joystick_x.get(),
                'joystick_start_y': self.var_action5_joystick_y.get(),
                'distance': self.var_action5_distance.get(),
                'duration_min': self.var_action5_duration_min.get(),
                'duration_max': self.var_action5_duration_max.get(),
                'click_x': self.var_action5_click_x.get(),
                'click_y': self.var_action5_click_y.get(),
                'chance': self.var_action5_chance.get()
            })
            
            action_settings['actions'] = actions_list
            self.config['action_settings'] = action_settings
            
            self.save_config()
            
            # Запускаем действия если они включены
            if self.var_actions_enabled.get():
                self.start_actions()
            else:
                self.stop_actions()
            
            self.log_message("💾 Настройки 5 действий сохранены", 'SUCCESS')
            messagebox.showinfo("Успех", "Настройки 5 отдельных действий сохранены!")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения настроек действий: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def get_action_chance(self, actions_list, action_type, default_chance):
        """Возвращает шанс выполнения для указанного типа действия"""
        for action in actions_list:
            if action.get('type') == action_type:
                return action.get('chance', default_chance)
        return default_chance
    
    def get_action_param(self, actions_list, action_type, param_name, default_value):
        """Возвращает параметр для указанного типа действия"""
        for action in actions_list:
            if action.get('type') == action_type:
                return action.get(param_name, default_value)
        return default_value
    
    def setup_schedule_tab(self):
        """Вкладка настройки расписания"""
        title_frame = ttk.Frame(self.tab_schedule)
        title_frame.pack(fill='x', pady=10)
        
        ttk.Label(title_frame, text="⏰ Настройки расписания работы", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(title_frame, text="Расписание смены режимов работы каждый час").pack()
        
        # Создаем контейнер с прокруткой
        container = ttk.Frame(self.tab_schedule)
        container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Создаем canvas и скроллбар
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Настройки периодов
        schedule_settings = self.config.get('schedule_settings', {})
        action_periods = schedule_settings.get('action_periods', [])
        
        for i, period in enumerate(action_periods):
            period_frame = ttk.LabelFrame(scrollable_frame, text=f"Период {i+1}", padding=10)
            period_frame.pack(fill='x', padx=10, pady=5)
            
            # Время начала
            start_frame = ttk.Frame(period_frame)
            start_frame.pack(fill='x', pady=5)
            
            ttk.Label(start_frame, text="Начало (минуты):").pack(side='left', padx=5)
            start_var = tk.IntVar(value=period.get('start_minute', 0))
            ttk.Spinbox(start_frame, from_=0, to=59, textvariable=start_var, width=8).pack(side='left', padx=5)
            setattr(self, f'var_period{i}_start', start_var)
            
            # Время окончания
            end_frame = ttk.Frame(period_frame)
            end_frame.pack(fill='x', pady=5)
            
            ttk.Label(end_frame, text="Окончание (минуты):").pack(side='left', padx=5)
            end_var = tk.IntVar(value=period.get('end_minute', 15))
            ttk.Spinbox(end_frame, from_=0, to=59, textvariable=end_var, width=8).pack(side='left', padx=5)
            setattr(self, f'var_period{i}_end', end_var)
            
            # Режим работы
            mode_frame = ttk.Frame(period_frame)
            mode_frame.pack(fill='x', pady=5)
            
            ttk.Label(mode_frame, text="Режим:").pack(side='left', padx=5)
            mode_var = tk.StringVar(value=period.get('mode', 'actions_only'))
            mode_combo = ttk.Combobox(mode_frame, textvariable=mode_var, 
                                     values=['actions_only', 'recovery_only'],
                                     state='readonly', width=15)
            mode_combo.pack(side='left', padx=5)
            setattr(self, f'var_period{i}_mode', mode_var)
            
            # Описание периода
            desc_frame = ttk.Frame(period_frame)
            desc_frame.pack(fill='x', pady=5)
            
            start_min = start_var.get()
            end_min = end_var.get()
            duration = end_min - start_min if end_min > start_min else 60 - start_min + end_min
            mode_text = "ТОЛЬКО ДЕЙСТВИЯ" if mode_var.get() == 'actions_only' else "ТОЛЬКО ВОССТАНОВЛЕНИЕ"
            
            desc_label = ttk.Label(desc_frame, text=f"{start_min:02d}:00 - {end_min:02d}:00 ({duration} мин) - {mode_text}")
            desc_label.pack(anchor='w')
            setattr(self, f'label_period{i}_desc', desc_label)
            
            # Исправление: использование trace_add вместо trace_variable
            start_var.trace_add('write', lambda *args, idx=i: self.update_period_description(idx))
            end_var.trace_add('write', lambda *args, idx=i: self.update_period_description(idx))
            mode_var.trace_add('write', lambda *args, idx=i: self.update_period_description(idx))
        
        # Кнопки управления
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="🔄 Проверить сейчас", 
                  command=self.check_schedule_now).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="💾 Сохранить расписание", 
                  command=self.save_schedule_settings,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🔄 Перезапустить планировщик", 
                  command=self.restart_schedule_scheduler).pack(side='left', padx=5)
        
        # Статус
        status_frame = ttk.LabelFrame(scrollable_frame, text="Статус", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.label_schedule_status = ttk.Label(status_frame, text="Планировщик активен", foreground='green')
        self.label_schedule_status.pack(anchor='w', pady=2)
        
        current_minute = datetime.now().minute
        current_mode = "не определен"
        
        for period in action_periods:
            start = period.get('start_minute', 0)
            end = period.get('end_minute', 60)
            
            if start <= current_minute < end:
                mode = period.get('mode', 'actions_only')
                current_mode = "ТОЛЬКО ДЕЙСТВИЯ" if mode == 'actions_only' else "ТОЛЬКО ВОССТАНОВЛЕНИЕ"
                break
        
        ttk.Label(status_frame, text=f"Текущий режим: {current_mode}").pack(anchor='w', pady=2)
        ttk.Label(status_frame, text=f"Текущая минута часа: {current_minute}").pack(anchor='w', pady=2)
        
        if schedule_settings.get('last_mode_change'):
            last_change = datetime.fromtimestamp(schedule_settings['last_mode_change'])
            last_time_str = last_change.strftime("%H:%M:%S")
            ttk.Label(status_frame, text=f"Последняя смена режима: {last_time_str}").pack(anchor='w', pady=2)
        
        # Описание расписания
        desc_frame = ttk.LabelFrame(scrollable_frame, text="Описание расписания", padding=10)
        desc_frame.pack(fill='x', padx=10, pady=5)
        
        description = """
        Расписание работы каждый час:
        
        1. 0-15 минут: ТОЛЬКО ДЕЙСТВИЯ
           • Выполняются разнообразные действия во всех окнах
           • Восстановление окон отключено
        
        2. 15-25 минут: ТОЛЬКО ВОССТАНОВЛЕНИЕ
           • Действия отключены
           • Активно восстанавливаются окна при обнаружении триггеров
        
        3. 25-40 минут: ТОЛЬКО ДЕЙСТВИЯ
           • Снова выполняются действия
           • Восстановление отключено
        
        4. 40-60 минут: ТОЛЬКО ВОССТАНОВЛЕНИЕ
           • Финальный этап восстановления окон
           • Действия отключены
        
        Цикл повторяется каждый час.
        """
        
        ttk.Label(desc_frame, text=description, justify='left').pack(anchor='w')
        
        # Упаковываем canvas и scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def update_period_description(self, idx):
        """Обновляет описание периода"""
        try:
            start_var = getattr(self, f'var_period{idx}_start')
            end_var = getattr(self, f'var_period{idx}_end')
            mode_var = getattr(self, f'var_period{idx}_mode')
            desc_label = getattr(self, f'label_period{idx}_desc')
            
            start_min = start_var.get()
            end_min = end_var.get()
            duration = end_min - start_min if end_min > start_min else 60 - start_min + end_min
            mode_text = "ТОЛЬКО ДЕЙСТВИЯ" if mode_var.get() == 'actions_only' else "ТОЛЬКО ВОССТАНОВЛЕНИЕ"
            
            desc_label.config(text=f"{start_min:02d}:00 - {end_min:02d}:00 ({duration} мин) - {mode_text}")
            
        except Exception as e:
            print(f"Ошибка обновления описания периода: {e}")
    
    def check_schedule_now(self):
        """Проверяет расписание сейчас"""
        try:
            current_minute = datetime.now().minute
            schedule_settings = self.config.get('schedule_settings', {})
            action_periods = schedule_settings.get('action_periods', [])
            
            for period in action_periods:
                start = period.get('start_minute', 0)
                end = period.get('end_minute', 60)
                
                if start <= current_minute < end:
                    mode = period.get('mode', 'actions_only')
                    mode_text = "ТОЛЬКО ДЕЙСТВИЯ" if mode == 'actions_only' else "ТОЛЬКО ВОССТАНОВЛЕНИЕ"
                    
                    messagebox.showinfo("Текущий режим", 
                                      f"Текущая минута: {current_minute}\n"
                                      f"Режим: {mode_text}\n"
                                      f"Период: {start:02d}:00 - {end:02d}:00")
                    return
            
            messagebox.showinfo("Текущий режим", f"Текущая минута: {current_minute}\nРежим: не определен")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка проверки расписания: {e}")
    
    def save_schedule_settings(self):
        """Сохраняет настройки расписания"""
        try:
            schedule_settings = self.config.get('schedule_settings', {})
            action_periods = []
            
            # Собираем все периоды
            for i in range(4):  # У нас всегда 4 периода
                try:
                    start_var = getattr(self, f'var_period{i}_start')
                    end_var = getattr(self, f'var_period{i}_end')
                    mode_var = getattr(self, f'var_period{i}_mode')
                    
                    period = {
                        'start_minute': start_var.get(),
                        'end_minute': end_var.get(),
                        'mode': mode_var.get()
                    }
                    
                    action_periods.append(period)
                    
                except AttributeError:
                    # Если переменные не существуют, используем значения по умолчанию
                    default_periods = [
                        {'start_minute': 0, 'end_minute': 15, 'mode': 'actions_only'},
                        {'start_minute': 15, 'end_minute': 25, 'mode': 'recovery_only'},
                        {'start_minute': 25, 'end_minute': 40, 'mode': 'actions_only'},
                        {'start_minute': 40, 'end_minute': 60, 'mode': 'recovery_only'}
                    ]
                    
                    if i < len(default_periods):
                        action_periods.append(default_periods[i])
            
            schedule_settings['action_periods'] = action_periods
            self.config['schedule_settings'] = schedule_settings
            
            self.save_config()
            
            # Перезапускаем планировщик
            self.restart_schedule_scheduler()
            
            self.log_message("💾 Настройки расписания сохранены", 'SUCCESS')
            messagebox.showinfo("Успех", "Настройки расписания сохранены!")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения настроек расписания: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def restart_schedule_scheduler(self):
        """Перезапускает планировщик расписания"""
        try:
            # Останавливаем текущий планировщик
            if hasattr(self, 'mode_scheduler_thread') and self.mode_scheduler_thread.is_alive():
                # Создаем новый поток
                self.mode_scheduler_thread = threading.Thread(target=self.check_schedule_mode, daemon=True)
                self.mode_scheduler_thread.start()
            
            self.log_message("🔄 Планировщик расписания перезапущен", 'INFO')
            self.label_schedule_status.config(text="Планировщик активен", foreground='green')
            
        except Exception as e:
            self.log_message(f"❌ Ошибка перезапуска планировщика: {e}", 'ERROR')
            self.label_schedule_status.config(text="Ошибка планировщика", foreground='red')
    
    def setup_auto_clicks_tab(self):
        """Вкладка настройки автоматических кликов"""
        title_frame = ttk.Frame(self.tab_auto_clicks)
        title_frame.pack(fill='x', pady=10)
        
        ttk.Label(title_frame, text="⏰ Настройки автоматических кликов", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(title_frame, text="Автоматическое выполнение 4 кликов в каждом окне каждые 12 часов").pack()
        
        # Основные настройки
        main_frame = ttk.LabelFrame(self.tab_auto_clicks, text="Основные настройки", padding=10)
        main_frame.pack(fill='x', padx=10, pady=5)
        
        # Включение/отключение
        enable_frame = ttk.Frame(main_frame)
        enable_frame.pack(fill='x', pady=5)
        
        self.var_auto_clicks_enabled = tk.BooleanVar(value=self.config['auto_clicks_settings']['enabled'])
        ttk.Checkbutton(enable_frame, text="Включить автоматические клики", 
                       variable=self.var_auto_clicks_enabled).pack(side='left', padx=5)
        
        # Время выполнения
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill='x', pady=5)
        
        ttk.Label(time_frame, text="Первое время:").pack(side='left', padx=5)
        self.var_first_time = tk.StringVar(value=self.config['auto_clicks_settings']['first_time'])
        ttk.Entry(time_frame, textvariable=self.var_first_time, width=8).pack(side='left', padx=5)
        
        ttk.Label(time_frame, text="Второе время:").pack(side='left', padx=5)
        self.var_second_time = tk.StringVar(value=self.config['auto_clicks_settings']['second_time'])
        ttk.Entry(time_frame, textvariable=self.var_second_time, width=8).pack(side='left', padx=5)
        
        # Проверка перед кликами
        check_frame = ttk.Frame(main_frame)
        check_frame.pack(fill='x', pady=5)
        
        self.var_check_before_clicks = tk.BooleanVar(value=self.config['auto_clicks_settings']['check_before_clicks'])
        ttk.Checkbutton(check_frame, text="Проверять отсутствие триггеров перед кликами", 
                       variable=self.var_check_before_clicks).pack(side='left', padx=5)
        
        # Время ожидания
        wait_frame = ttk.Frame(main_frame)
        wait_frame.pack(fill='x', pady=5)
        
        ttk.Label(wait_frame, text="Макс. время ожидания (сек):").pack(side='left', padx=5)
        self.var_wait_for_no_triggers = tk.IntVar(value=self.config['auto_clicks_settings']['wait_for_no_triggers'])
        ttk.Spinbox(wait_frame, from_=10, to=300, textvariable=self.var_wait_for_no_triggers, width=10).pack(side='left', padx=5)
        
        # Координаты кликов
        coords_frame = ttk.LabelFrame(self.tab_auto_clicks, text="Координаты 4-х кликов", padding=10)
        coords_frame.pack(fill='x', padx=10, pady=5)
        
        # Создаем переменные для координат
        self.auto_click_vars = []
        for i in range(4):
            click_frame = ttk.Frame(coords_frame)
            click_frame.pack(fill='x', pady=5)
            
            ttk.Label(click_frame, text=f"Клик {i+1} - X:").pack(side='left', padx=5)
            var_x = tk.IntVar(value=self.config['auto_clicks_config'][i]['x'])
            ttk.Spinbox(click_frame, from_=0, to=1000, textvariable=var_x, width=8).pack(side='left', padx=5)
            
            ttk.Label(click_frame, text="Y:").pack(side='left', padx=5)
            var_y = tk.IntVar(value=self.config['auto_clicks_config'][i]['y'])
            ttk.Spinbox(click_frame, from_=0, to=1000, textvariable=var_y, width=8).pack(side='left', padx=5)
            
            self.auto_click_vars.append((var_x, var_y))
        
        # Кнопки управления
        btn_frame = ttk.Frame(self.tab_auto_clicks)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="🚀 Тестовый запуск", 
                  command=self.test_auto_clicks,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="💾 Сохранить настройки", 
                  command=self.save_auto_clicks_settings).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🔄 Перезапустить планировщик", 
                  command=self.restart_auto_clicks_scheduler).pack(side='left', padx=5)
        
        # Статус
        status_frame = ttk.LabelFrame(self.tab_auto_clicks, text="Статус", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.label_auto_clicks_status = ttk.Label(status_frame, text="Планировщик активен", foreground='green')
        self.label_auto_clicks_status.pack(anchor='w', pady=2)
        
        if self.last_auto_click_time:
            last_time_str = self.last_auto_click_time.strftime("%H:%M:%S %d.%m.%Y")
            ttk.Label(status_frame, text=f"Последнее выполнение: {last_time_str}").pack(anchor='w', pady=2)
        
        # Описание
        desc_frame = ttk.LabelFrame(self.tab_auto_clicks, text="Описание", padding=10)
        desc_frame.pack(fill='x', padx=10, pady=5)
        
        description = """
        Автоматические клики выполняются каждые 12 часов (в 12:00 и 00:00):
        
        1. Проверяются все окна на отсутствие триггеров
        2. В КАЖДОМ окне выполняются 4 клика по заданным координатам
        3. Клики выполняются последовательно с человеческими задержками
        
        Координаты указываются относительно верхнего левого угла каждого окна.
        """
        
        ttk.Label(desc_frame, text=description, justify='left').pack(anchor='w')
    
    def test_auto_clicks(self):
        """Тестовый запуск автоматических кликов"""
        if not self.windows_data:
            messagebox.showwarning("Предупреждение", "Сначала создайте сетку окон!")
            return
        
        if messagebox.askyesno("Тестовый запуск", "Выполнить тестовые автоматические клики сейчас?"):
            self.execute_auto_clicks()
    
    def save_auto_clicks_settings(self):
        """Сохраняет настройки автоматических кликов"""
        try:
            # Основные настройки
            self.config['auto_clicks_settings']['enabled'] = self.var_auto_clicks_enabled.get()
            self.config['auto_clicks_settings']['first_time'] = self.var_first_time.get()
            self.config['auto_clicks_settings']['second_time'] = self.var_second_time.get()
            self.config['auto_clicks_settings']['check_before_clicks'] = self.var_check_before_clicks.get()
            self.config['auto_clicks_settings']['wait_for_no_triggers'] = self.var_wait_for_no_triggers.get()
            
            # Координаты кликов
            for i in range(4):
                self.config['auto_clicks_config'][i]['x'] = self.auto_click_vars[i][0].get()
                self.config['auto_clicks_config'][i]['y'] = self.auto_click_vars[i][1].get()
            
            self.save_config()
            
            # Перезапускаем планировщик
            self.restart_auto_clicks_scheduler()
            
            self.log_message("💾 Настройки автоматических кликов сохранены", 'SUCCESS')
            messagebox.showinfo("Успех", "Настройки автоматических кликов сохранены!")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения настроек: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def restart_auto_clicks_scheduler(self):
        """Перезапускает планировщик автоматических кликов"""
        try:
            self.init_auto_clicks_scheduler()
            self.log_message("🔄 Планировщик автоматических кликов перезапущен", 'INFO')
            self.label_auto_clicks_status.config(text="Планировщик активен", foreground='green')
        except Exception as e:
            self.log_message(f"❌ Ошибка перезапуска планировщика: {e}", 'ERROR')
            self.label_auto_clicks_status.config(text="Ошибка планировщика", foreground='red')
    
    def setup_detection_tab(self):
        """Вкладка детекции"""
        control_frame = ttk.LabelFrame(self.tab_detection, text="Управление", padding=15)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill='x', pady=5)
        
        self.btn_start = ttk.Button(btn_frame, text="🚀 НАЧАТЬ МОНИТОРИНГ", 
                                   command=self.start_monitoring,
                                   style='Accent.TButton')
        self.btn_start.pack(side='left', padx=5)
        
        self.btn_stop = ttk.Button(btn_frame, text="⏹ ОСТАНОВИТЬ", 
                                  command=self.stop_monitoring,
                                  state='disabled')
        self.btn_stop.pack(side='left', padx=5)
        
        self.btn_pause = ttk.Button(btn_frame, text="⏸ ПАУЗА", 
                                   command=self.toggle_pause,
                                   state='disabled')
        self.btn_pause.pack(side='left', padx=5)
        
        self.btn_clear_history = ttk.Button(btn_frame, text="🗑️ Очистить историю", 
                                          command=self.clear_trigger_history)
        self.btn_clear_history.pack(side='left', padx=5)
        
        # Добавляем кнопку для ручного запуска автокликов
        self.btn_auto_clicks = ttk.Button(btn_frame, text="⏰ Запустить автоклики", 
                                         command=self.execute_auto_clicks)
        self.btn_auto_clicks.pack(side='left', padx=5)
        
        # Добавляем кнопку для запуска действий
        self.btn_actions = ttk.Button(btn_frame, text="🎮 Запустить действия", 
                                     command=self.start_actions)
        self.btn_actions.pack(side='left', padx=5)
        
        stats_frame = ttk.LabelFrame(self.tab_detection, text="Статистика", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x')
        
        self.labels_stats = {}
        stats_data = [
            ('Всего обнаружений:', 'total_detections', '0'),
            ('Обработано действий:', 'action_count', '0'),
            ('Загружено триггеров:', 'loaded_triggers', '0'),
            ('Окон в сетке:', 'windows_count', '0'),
            ('Статус:', 'status', 'Неактивно'),
            ('Последнее действие:', 'last_action', 'Нет'),
            ('Окна в коудауне:', 'windows_cooldown', '0'),
            ('Выполнено кликов:', 'total_clicks', '0'),
            ('Статус отдыха:', 'rest_status', 'Активен'),
            ('Текущий режим:', 'current_mode', 'Действия'),
            ('Выполнено действий:', 'actions_count', '0'),
            ('Автоклики:', 'auto_clicks_status', 'Ожидание'),
            ('Кулдаун группы 1 после группы 4:', 'group1_cooldown_status', 'Неактивен'),  # ИЗМЕНЕНО
            ('Ввод пароля:', 'password_input_status', 'Неактивно'),
            ('Скорость детекции:', 'detection_speed', '1.0x'),
            ('Скорость действий:', 'action_speed', '1.0x'),
            ('Скорость восст.:', 'recovery_speed', '1.0x'),
            ('Восстановлено окон:', 'recovered_windows', '0'),  # Новая статистика
        ]
        
        for i, (label, key, value) in enumerate(stats_data):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(stats_grid, text=label).grid(row=row, column=col, padx=5, pady=2, sticky='w')
            self.labels_stats[key] = ttk.Label(stats_grid, text=value, font=('Arial', 9, 'bold'))
            self.labels_stats[key].grid(row=row, column=col+1, padx=5, pady=2, sticky='w')
        
        preview_frame = ttk.LabelFrame(self.tab_detection, text="Предпросмотр", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(preview_frame, bg='#2b2b2b')
        self.canvas.pack(fill='both', expand=True)
        
        self.label_preview = ttk.Label(self.canvas, text="Предпросмотр будет здесь...", 
                                      background='#2b2b2b', foreground='white')
        self.canvas.create_window(200, 150, window=self.label_preview)
    
    def clear_trigger_history(self):
        """Очищает историю срабатываний триггеров"""
        self.last_triggered_windows.clear()
        self.group4_triggered_windows.clear()  # Очищаем окна с сработавшей группой 4
        self.group1_cooldown_after_group4_active = False
        self.group1_cooldown_after_group4_start = 0
        self.labels_stats['windows_cooldown'].config(text='0')
        self.labels_stats['group1_cooldown_status'].config(text='Неактивен')
        self.log_message("История срабатываний очищена", 'INFO')
        messagebox.showinfo("Успех", "История срабатываний триггеров очищена!")
    
    def setup_triggers_tab(self):
        """Вкладка управления группами триггеров"""
        title_frame = ttk.Frame(self.tab_triggers)
        title_frame.pack(fill='x', pady=10)
        
        ttk.Label(title_frame, text="Управление группами триггеров", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(title_frame, text="Загрузите изображения для каждой группы").pack()
        
        # Создаем контейнер с прокруткой для всех групп
        container = ttk.Frame(self.tab_triggers)
        container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Создаем canvas и скроллбар
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ГРУППА 1: 15 триггеров (2 клика) - ИЗМЕНЕНО: УБРАН ОТДЕЛЬНЫЙ КУЛДАУН
        group1_frame = ttk.LabelFrame(scrollable_frame, text="ГРУППА 1: 15 триггеров (2 клика)", padding=10)
        group1_frame.pack(fill='x', pady=10, padx=5)
        
        # Порог для группы 1
        threshold_frame = ttk.Frame(group1_frame)
        threshold_frame.pack(fill='x', pady=5)
        
        ttk.Label(threshold_frame, text="Порог обнаружения:").pack(side='left', padx=5)
        self.var_threshold_group1 = tk.IntVar(value=int(self.config['threshold_group1'] * 100))
        self.scale_group1 = ttk.Scale(threshold_frame, from_=0, to=100, variable=self.var_threshold_group1,
                                     orient='horizontal', length=150)
        self.scale_group1.pack(side='left', padx=5)
        self.label_threshold_group1 = ttk.Label(threshold_frame, text=f"{self.config['threshold_group1']*100:.0f}%")
        self.label_threshold_group1.pack(side='left', padx=5)
        # Исправление: использование trace_add вместо trace_variable
        self.var_threshold_group1.trace_add('write', lambda *args: self.update_group1_threshold())
        
        # НАСТРОЙКА КУЛДАУНА ДЛЯ ГРУППЫ 1 ПОСЛЕ СРАБАТЫВАНИЯ ГРУППЫ 4 - ИЗМЕНЕНО
        cooldown_frame = ttk.Frame(group1_frame)
        cooldown_frame.pack(fill='x', pady=5)
        
        ttk.Label(cooldown_frame, text="Кулдаун для группы 1 после группы 4 (сек):").pack(side='left', padx=5)
        self.var_group1_cooldown_after_group4 = tk.IntVar(value=self.config.get('group1_cooldown_after_group4', 180))
        ttk.Spinbox(cooldown_frame, from_=10, to=600, textvariable=self.var_group1_cooldown_after_group4, width=10).pack(side='left', padx=5)
        ttk.Label(cooldown_frame, text="(После срабатывания группы 4, группа 1 блокируется на указанное время)").pack(side='left', padx=5)
        
        # Кнопки загрузки для 15 триггеров
        load_frame = ttk.Frame(group1_frame)
        load_frame.pack(fill='x', pady=5)
        
        ttk.Button(load_frame, text="📁 Загрузить все 15 триггеров", 
                  command=self.load_group1_triggers).pack(side='left', padx=5)
        ttk.Button(load_frame, text="📁 Загрузить по одному", 
                  command=self.load_single_group1_trigger).pack(side='left', padx=5)
        ttk.Button(load_frame, text="🗑️ Очистить группу 1", 
                  command=self.clear_group1).pack(side='left', padx=5)
        
        # Статус загрузки
        self.label_group1_status = ttk.Label(group1_frame, text="Загружено: 0/15", foreground='red')
        self.label_group1_status.pack(anchor='w', pady=2)
        
        # Информация о кулдауне - ИЗМЕНЕНО
        info_frame = ttk.Frame(group1_frame)
        info_frame.pack(fill='x', pady=5)
        
        ttk.Label(info_frame, text="После срабатывания триггера группы 4 в окне, группа 1 блокируется в этом окне", 
                 font=('Arial', 9)).pack(anchor='w')
        ttk.Label(info_frame, text="на указанное время (по умолчанию 3 минуты). Группа 1 не имеет отдельного кулдауна.", 
                 font=('Arial', 9)).pack(anchor='w')
        
        # ГРУППА 2: 1 триггер (1 клик)
        group2_frame = ttk.LabelFrame(scrollable_frame, text="ГРУППА 2: 1 триггер (1 клик)", padding=10)
        group2_frame.pack(fill='x', pady=10, padx=5)
        
        threshold_frame2 = ttk.Frame(group2_frame)
        threshold_frame2.pack(fill='x', pady=5)
        
        ttk.Label(threshold_frame2, text="Порог обнаружения:").pack(side='left', padx=5)
        self.var_threshold_group2 = tk.IntVar(value=int(self.config['threshold_group2'] * 100))
        self.scale_group2 = ttk.Scale(threshold_frame2, from_=0, to=100, variable=self.var_threshold_group2,
                                     orient='horizontal', length=150)
        self.scale_group2.pack(side='left', padx=5)
        self.label_threshold_group2 = ttk.Label(threshold_frame2, text=f"{self.config['threshold_group2']*100:.0f}%")
        self.label_threshold_group2.pack(side='left', padx=5)
        # Исправление: использование trace_add вместо trace_variable
        self.var_threshold_group2.trace_add('write', lambda *args: self.update_group2_threshold())
        
        load_frame2 = ttk.Frame(group2_frame)
        load_frame2.pack(fill='x', pady=5)
        
        ttk.Button(load_frame2, text="📁 Загрузить триггер группы 2", 
                  command=self.load_group2_trigger).pack(side='left', padx=5)
        self.btn_clear_group2 = ttk.Button(load_frame2, text="🗑️ Очистить", 
                                         command=self.clear_group2, state='disabled')
        self.btn_clear_group2.pack(side='left', padx=5)
        
        self.label_group2_status = ttk.Label(group2_frame, text="Не загружен", foreground='red')
        self.label_group2_status.pack(anchor='w', pady=2)
        
        # ГРУППА 3: 1 триггер (1 клик)
        group3_frame = ttk.LabelFrame(scrollable_frame, text="ГРУППА 3: 1 триггер (1 клик)", padding=10)
        group3_frame.pack(fill='x', pady=10, padx=5)
        
        threshold_frame3 = ttk.Frame(group3_frame)
        threshold_frame3.pack(fill='x', pady=5)
        
        ttk.Label(threshold_frame3, text="Порог обнаружения:").pack(side='left', padx=5)
        self.var_threshold_group3 = tk.IntVar(value=int(self.config['threshold_group3'] * 100))
        self.scale_group3 = ttk.Scale(threshold_frame3, from_=0, to=100, variable=self.var_threshold_group3,
                                     orient='horizontal', length=150)
        self.scale_group3.pack(side='left', padx=5)
        self.label_threshold_group3 = ttk.Label(threshold_frame3, text=f"{self.config['threshold_group3']*100:.0f}%")
        self.label_threshold_group3.pack(side='left', padx=5)
        # Исправление: использование trace_add вместо trace_variable
        self.var_threshold_group3.trace_add('write', lambda *args: self.update_group3_threshold())
        
        load_frame3 = ttk.Frame(group3_frame)
        load_frame3.pack(fill='x', pady=5)
        
        ttk.Button(load_frame3, text="📁 Загрузить триггер группы 3", 
                  command=self.load_group3_trigger).pack(side='left', padx=5)
        self.btn_clear_group3 = ttk.Button(load_frame3, text="🗑️ Очистить", 
                                         command=self.clear_group3, state='disabled')
        self.btn_clear_group3.pack(side='left', padx=5)
        
        self.label_group3_status = ttk.Label(group3_frame, text="Не загружен", foreground='red')
        self.label_group3_status.pack(anchor='w', pady=2)
        
        # ГРУППА 4: 20 триггеров (одинаковые координаты для всех)
        group4_frame = ttk.LabelFrame(scrollable_frame, text="ГРУППА 4: 20 триггеров (одинаковые координаты)", padding=10)
        group4_frame.pack(fill='x', pady=10, padx=5)
        
        threshold_frame4 = ttk.Frame(group4_frame)
        threshold_frame4.pack(fill='x', pady=5)
        
        ttk.Label(threshold_frame4, text="Порог обнаружения:").pack(side='left', padx=5)
        self.var_threshold_group4 = tk.IntVar(value=int(self.config['threshold_group4'] * 100))
        self.scale_group4 = ttk.Scale(threshold_frame4, from_=0, to=100, variable=self.var_threshold_group4,
                                     orient='horizontal', length=150)
        self.scale_group4.pack(side='left', padx=5)
        self.label_threshold_group4 = ttk.Label(threshold_frame4, text=f"{self.config['threshold_group4']*100:.0f}%")
        self.label_threshold_group4.pack(side='left', padx=5)
        # Исправление: использование trace_add вместо trace_variable
        self.var_threshold_group4.trace_add('write', lambda *args: self.update_group4_threshold())
        
        load_frame4 = ttk.Frame(group4_frame)
        load_frame4.pack(fill='x', pady=5)
        
        ttk.Button(load_frame4, text="📁 Загрузить все 20 триггеров", 
                  command=self.load_group4_triggers).pack(side='left', padx=5)
        ttk.Button(load_frame4, text="📁 Загрузить по одному", 
                  command=self.load_single_group4_trigger).pack(side='left', padx=5)
        ttk.Button(load_frame4, text="🗑️ Очистить группу 4", 
                  command=self.clear_group4).pack(side='left', padx=5)
        
        # Статус загрузки
        self.label_group4_status = ttk.Label(group4_frame, text="Загружено: 0/20", foreground='red')
        self.label_group4_status.pack(anchor='w', pady=2)
        
        # ГРУППА 5: 1 триггер (клик + пароль + клик) - ИЗМЕНЕНО
        group5_frame = ttk.LabelFrame(scrollable_frame, text="Группа 5: 1 триггер (клик + пароль + клик)", padding=10)
        group5_frame.pack(fill='x', pady=10, padx=5)
        
        threshold_frame5 = ttk.Frame(group5_frame)
        threshold_frame5.pack(fill='x', pady=5)
        
        ttk.Label(threshold_frame5, text="Порог обнаружения:").pack(side='left', padx=5)
        self.var_threshold_group5 = tk.IntVar(value=int(self.config['threshold_group5'] * 100))
        self.scale_group5 = ttk.Scale(threshold_frame5, from_=0, to=100, variable=self.var_threshold_group5,
                                     orient='horizontal', length=150)
        self.scale_group5.pack(side='left', padx=5)
        self.label_threshold_group5 = ttk.Label(threshold_frame5, text=f"{self.config['threshold_group5']*100:.0f}%")
        self.label_threshold_group5.pack(side='left', padx=5)
        # Исправление: использование trace_add вместо trace_variable
        self.var_threshold_group5.trace_add('write', lambda *args: self.update_group5_threshold())
        
        load_frame5 = ttk.Frame(group5_frame)
        load_frame5.pack(fill='x', pady=5)
        
        ttk.Button(load_frame5, text="📁 Загрузить триггер группы 5", 
                  command=self.load_single_group5_trigger).pack(side='left', padx=5)
        ttk.Button(load_frame5, text="🗑️ Очистить группу 5", 
                  command=self.clear_group5).pack(side='left', padx=5)
        
        # Статус загрузки (1 вместо 20)
        self.label_group5_status = ttk.Label(group5_frame, text="Загружено: 0/1", foreground='red')
        self.label_group5_status.pack(anchor='w', pady=2)
        
        # ГРУППА 6: 8 триггеров (каждый свой клик) - КАЖДЫЙ ЗАГРУЖАЕТСЯ ОТДЕЛЬНО (ИЗМЕНЕНО с 5 на 8)
        group6_frame = ttk.LabelFrame(scrollable_frame, text="ГРУППА 6: 8 триггеров (8 разных кликов)", padding=10)
        group6_frame.pack(fill='x', pady=10, padx=5)
        
        threshold_frame6 = ttk.Frame(group6_frame)
        threshold_frame6.pack(fill='x', pady=5)
        
        ttk.Label(threshold_frame6, text="Порог обнаружения:").pack(side='left', padx=5)
        self.var_threshold_group6 = tk.IntVar(value=int(self.config['threshold_group6'] * 100))
        self.scale_group6 = ttk.Scale(threshold_frame6, from_=0, to=100, variable=self.var_threshold_group6,
                                     orient='horizontal', length=150)
        self.scale_group6.pack(side='left', padx=5)
        self.label_threshold_group6 = ttk.Label(threshold_frame6, text=f"{self.config['threshold_group6']*100:.0f}%")
        self.label_threshold_group6.pack(side='left', padx=5)
        # Исправление: использование trace_add вместо trace_variable
        self.var_threshold_group6.trace_add('write', lambda *args: self.update_group6_threshold())
        
        # Создаем отдельные кнопки для каждого триггера группы 6
        triggers_grid = ttk.Frame(group6_frame)
        triggers_grid.pack(fill='x', pady=5)
        
        for i in range(1, 9):  # Изменено с range(1, 6) на range(1, 9)
            trigger_btn_frame = ttk.Frame(triggers_grid)
            trigger_btn_frame.pack(fill='x', pady=2)
            
            ttk.Label(trigger_btn_frame, text=f"Триггер {i}:").pack(side='left', padx=5)
            
            # Кнопка загрузки для конкретного триггера
            ttk.Button(trigger_btn_frame, text="📁 Загрузить", 
                      command=lambda idx=i: self.load_specific_group6_trigger(idx),
                      width=10).pack(side='left', padx=5)
            
            # Статус для каждого триггера
            status_label = ttk.Label(trigger_btn_frame, text="Не загружен", foreground='red')
            status_label.pack(side='left', padx=5)
            # Сохраняем ссылку на статус
            setattr(self, f'label_group6_trigger{i}_status', status_label)
            
            # Кнопка очистки для каждого триггера
            ttk.Button(trigger_btn_frame, text="🗑️", 
                      command=lambda idx=i: self.clear_specific_group6_trigger(idx),
                      width=3).pack(side='left', padx=2)
        
        # Общая кнопка загрузки всех триггеров
        load_frame6 = ttk.Frame(group6_frame)
        load_frame6.pack(fill='x', pady=5)
        
        ttk.Button(load_frame6, text="📁 Загрузить все 8 триггеров", 
                  command=self.load_group6_triggers).pack(side='left', padx=5)
        ttk.Button(load_frame6, text="🗑️ Очистить группу 6", 
                  command=self.clear_group6).pack(side='left', padx=5)
        
        # Статус загрузки
        self.label_group6_status = ttk.Label(group6_frame, text="Загружено: 0/8", foreground='red')
        self.label_group6_status.pack(anchor='w', pady=2)
        
        # Упаковываем canvas и scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки сохранения
        save_frame = ttk.Frame(self.tab_triggers)
        save_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(save_frame, text="💾 Сохранить все триггеры", 
                  command=self.save_all_triggers,
                  style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(save_frame, text="💾 Сохранить параметры", 
                  command=self.save_trigger_params).pack(side='left', padx=5)
    
    def update_group1_threshold(self):
        """Обновляет метку порога для группы 1"""
        self.label_threshold_group1.config(text=f"{self.var_threshold_group1.get()}%")
    
    def update_group2_threshold(self):
        """Обновляет метку порога для группы 2"""
        self.label_threshold_group2.config(text=f"{self.var_threshold_group2.get()}%")
    
    def update_group3_threshold(self):
        """Обновляет метку порога для группы 3"""
        self.label_threshold_group3.config(text=f"{self.var_threshold_group3.get()}%")
    
    def update_group4_threshold(self):
        """Обновляет метку порога для группы 4"""
        self.label_threshold_group4.config(text=f"{self.var_threshold_group4.get()}%")
    
    def update_group5_threshold(self):
        """Обновляет метку порога для группы 5"""
        self.label_threshold_group5.config(text=f"{self.var_threshold_group5.get()}%")
    
    def update_group6_threshold(self):
        """Обновляет метку порога для группы 6"""
        self.label_threshold_group6.config(text=f"{self.var_threshold_group6.get()}%")
    
    def load_group1_triggers(self):
        """Загружает 15 триггеров для группы 1"""
        try:
            filetypes = [("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*")]
            filepaths = filedialog.askopenfilenames(
                title="Выберите до 15 изображений для группы 1",
                filetypes=filetypes
            )
            
            if filepaths:
                loaded_count = 0
                max_triggers = min(15, len(filepaths))
                
                for i in range(max_triggers):
                    trigger_key = f'group1_trigger{i+1:02d}'
                    filepath = Path(filepaths[i])
                    
                    if self.process_trigger_file(trigger_key, filepath):
                        # Добавляем в список группы, если еще нет
                        if trigger_key not in self.group1_triggers:
                            self.group1_triggers.append(trigger_key)
                        loaded_count += 1
                
                self.label_group1_status.config(text=f"Загружено: {loaded_count}/15", 
                                              foreground='green' if loaded_count == 15 else 'orange')
                self.update_loaded_triggers_count()
                self.log_message(f"✅ Загружено {loaded_count} триггеров группы 1", 'SUCCESS')
                
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки триггеров группы 1: {e}", 'ERROR')
    
    def load_single_group1_trigger(self):
        """Загружает один триггер для группы 1"""
        try:
            filetypes = [("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*")]
            filepath = filedialog.askopenfilename(
                title="Выберите изображение для группы 1",
                filetypes=filetypes
            )
            
            if filepath:
                # Находим свободный номер для триггера
                for i in range(1, 16):
                    trigger_key = f'group1_trigger{i:02d}'
                    if trigger_key not in self.group1_triggers:
                        file_path = Path(filepath)
                        
                        if self.process_trigger_file(trigger_key, file_path):
                            self.group1_triggers.append(trigger_key)
                            loaded_count = len(self.group1_triggers)
                            self.label_group1_status.config(text=f"Загружено: {loaded_count}/15", 
                                                          foreground='orange' if loaded_count < 15 else 'green')
                            self.update_loaded_triggers_count()
                            self.log_message(f"✅ Загружен триггер группы 1: {file_path.name} (№{i})", 'SUCCESS')
                        break
                
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки триггера группы 1: {e}", 'ERROR')
    
    def load_group2_trigger(self):
        """Загружает триггер для группы 2"""
        self.load_single_trigger('group2', 'group2_trigger')
    
    def load_group3_trigger(self):
        """Загружает триггер для группы 3"""
        self.load_single_trigger('group3', 'group3_trigger')
    
    def load_group4_triggers(self):
        """Загружает 20 триггеров для группы 4"""
        try:
            filetypes = [("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*")]
            filepaths = filedialog.askopenfilenames(
                title="Выберите до 20 изображений для группы 4",
                filetypes=filetypes
            )
            
            if filepaths:
                loaded_count = 0
                max_triggers = min(20, len(filepaths))
                
                for i in range(max_triggers):
                    trigger_key = f'group4_trigger{i+1:02d}'
                    filepath = Path(filepaths[i])
                    
                    if self.process_trigger_file(trigger_key, filepath):
                        # Добавляем в список группы, если еще нет
                        if trigger_key not in self.group4_triggers:
                            self.group4_triggers.append(trigger_key)
                        loaded_count += 1
                
                self.label_group4_status.config(text=f"Загружено: {loaded_count}/20", 
                                              foreground='green' if loaded_count == 20 else 'orange')
                self.update_loaded_triggers_count()
                self.log_message(f"✅ Загружено {loaded_count} триггеров группы 4", 'SUCCESS')
                
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки триггеров группы 4: {e}", 'ERROR')
    
    def load_single_group4_trigger(self):
        """Загружает один триггер для группы 4"""
        try:
            filetypes = [("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*")]
            filepath = filedialog.askopenfilename(
                title="Выберите изображение для группы 4",
                filetypes=filetypes
            )
            
            if filepath:
                # Находим свободный номер для триггера
                for i in range(1, 21):
                    trigger_key = f'group4_trigger{i:02d}'
                    if trigger_key not in self.group4_triggers:
                        file_path = Path(filepath)
                        
                        if self.process_trigger_file(trigger_key, file_path):
                            self.group4_triggers.append(trigger_key)
                            loaded_count = len(self.group4_triggers)
                            self.label_group4_status.config(text=f"Загружено: {loaded_count}/20", 
                                                          foreground='orange' if loaded_count < 20 else 'green')
                            self.update_loaded_triggers_count()
                            self.log_message(f"✅ Загружен триггер группы 4: {file_path.name} (№{i})", 'SUCCESS')
                        break
                
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки триггера группы 4: {e}", 'ERROR')
    
    def load_group5_triggers(self):
        """Загружает 1 триггер для группы 5 (вместо 20)"""
        try:
            filetypes = [("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*")]
            filepaths = filedialog.askopenfilenames(
                title="Выберите 1 изображение для группы 5",
                filetypes=filetypes
            )
            
            if filepaths:
                loaded_count = 0
                max_triggers = min(1, len(filepaths))  # Только 1 триггер
                
                for i in range(max_triggers):
                    trigger_key = f'group5_trigger{1:02d}'  # Всегда trigger01
                    filepath = Path(filepaths[i])
                    
                    if self.process_trigger_file(trigger_key, filepath):
                        # Добавляем в список группы, если еще нет
                        if trigger_key not in self.group5_triggers:
                            self.group5_triggers.append(trigger_key)
                        loaded_count += 1
                
                self.label_group5_status.config(text=f"Загружено: {loaded_count}/1", 
                                              foreground='green' if loaded_count == 1 else 'orange')
                self.update_loaded_triggers_count()
                self.log_message(f"✅ Загружен триггер группы 5", 'SUCCESS')
                
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки триггера группы 5: {e}", 'ERROR')
    
    def load_single_group5_trigger(self):
        """Загружает один триггер для группы 5"""
        try:
            filetypes = [("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*")]
            filepath = filedialog.askopenfilename(
                title="Выберите изображение для группы 5",
                filetypes=filetypes
            )
            
            if filepath:
                # Для группы 5 всегда используем trigger01
                trigger_key = 'group5_trigger01'
                file_path = Path(filepath)
                
                if self.process_trigger_file(trigger_key, file_path):
                    # Удаляем старый триггер если был
                    if trigger_key in self.group5_triggers:
                        self.group5_triggers.remove(trigger_key)
                    
                    self.group5_triggers.append(trigger_key)
                    loaded_count = len(self.group5_triggers)
                    self.label_group5_status.config(text=f"Загружено: {loaded_count}/1", 
                                                  foreground='green' if loaded_count == 1 else 'orange')
                    self.update_loaded_triggers_count()
                    self.log_message(f"✅ Загружен триггер группы 5: {file_path.name}", 'SUCCESS')
                
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки триггера группы 5: {e}", 'ERROR')
    
    def load_group6_triggers(self):
        """Загружает 8 триггеров для группы 6"""
        try:
            filetypes = [("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*")]
            filepaths = filedialog.askopenfilenames(
                title="Выберите до 8 изображений для группы 6",
                filetypes=filetypes
            )
            
            if filepaths:
                loaded_count = 0
                max_triggers = min(8, len(filepaths))
                
                for i in range(max_triggers):
                    trigger_key = f'group6_trigger{i+1:02d}'
                    filepath = Path(filepaths[i])
                    
                    if self.process_trigger_file(trigger_key, filepath):
                        # Добавляем в список группы, если еще нет
                        if trigger_key not in self.group6_triggers:
                            self.group6_triggers.append(trigger_key)
                        loaded_count += 1
                        # Обновляем статус для конкретного триггера
                        status_label = getattr(self, f'label_group6_trigger{i+1}_status', None)
                        if status_label:
                            status_label.config(text="✅ Загружен", foreground='green')
                
                self.label_group6_status.config(text=f"Загружено: {loaded_count}/8", 
                                              foreground='green' if loaded_count == 8 else 'orange')
                self.update_loaded_triggers_count()
                self.log_message(f"✅ Загружено {loaded_count} триггеров группы 6", 'SUCCESS')
                
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки триггеров группы 6: {e}", 'ERROR')
    
    def load_specific_group6_trigger(self, trigger_num):
        """Загружает конкретный триггер для группы 6"""
        try:
            filetypes = [("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*")]
            filepath = filedialog.askopenfilename(
                title=f"Выберите изображение для триггера {trigger_num} группы 6",
                filetypes=filetypes
            )
            
            if filepath:
                trigger_key = f'group6_trigger{trigger_num:02d}'
                file_path = Path(filepath)
                
                if self.process_trigger_file(trigger_key, file_path):
                    # Удаляем старый триггер если был
                    if trigger_key in self.group6_triggers:
                        self.group6_triggers.remove(trigger_key)
                    
                    self.group6_triggers.append(trigger_key)
                    
                    # Обновляем статус для конкретного триггера
                    status_label = getattr(self, f'label_group6_trigger{trigger_num}_status', None)
                    if status_label:
                        status_label.config(text="✅ Загружен", foreground='green')
                    
                    # Обновляем общий статус
                    loaded_count = len(self.group6_triggers)
                    self.label_group6_status.config(text=f"Загружено: {loaded_count}/8", 
                                                  foreground='green' if loaded_count == 8 else 'orange')
                    self.update_loaded_triggers_count()
                    self.log_message(f"✅ Загружен триггер {trigger_num} группы 6: {file_path.name}", 'SUCCESS')
                
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки триггера группы 6: {e}", 'ERROR')
    
    def load_single_group6_trigger(self):
        """Загружает один триггер для группы 6 (старая версия для совместимости)"""
        try:
            filetypes = [("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*")]
            filepath = filedialog.askopenfilename(
                title="Выберите изображение для группы 6",
                filetypes=filetypes
            )
            
            if filepath:
                # Находим свободный номер для триггера
                for i in range(1, 9):  # Изменено с range(1, 6) на range(1, 9)
                    trigger_key = f'group6_trigger{i:02d}'
                    if trigger_key not in self.group6_triggers:
                        file_path = Path(filepath)
                        
                        if self.process_trigger_file(trigger_key, file_path):
                            self.group6_triggers.append(trigger_key)
                            loaded_count = len(self.group6_triggers)
                            self.label_group6_status.config(text=f"Загружено: {loaded_count}/8", 
                                                          foreground='orange' if loaded_count < 8 else 'green')
                            self.update_loaded_triggers_count()
                            self.log_message(f"✅ Загружен триггер группы 6: {file_path.name} (№{i})", 'SUCCESS')
                        break
                
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки триггера группы 6: {e}", 'ERROR')
    
    def load_single_trigger(self, group_name, trigger_key):
        """Загружает одиночный триггер"""
        try:
            filetypes = [("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*")]
            filepath = filedialog.askopenfilename(
                title=f"Выберите изображение для {group_name}",
                filetypes=filetypes
            )
            
            if filepath:
                file_path = Path(filepath)
                
                if self.process_trigger_file(trigger_key, file_path):
                    # Сохраняем ссылку на триггер
                    if group_name == 'group2':
                        self.group2_trigger = trigger_key
                        self.btn_clear_group2.config(state='normal')
                        self.label_group2_status.config(text="✅ Загружен", foreground='green')
                    elif group_name == 'group3':
                        self.group3_trigger = trigger_key
                        self.btn_clear_group3.config(state='normal')
                        self.label_group3_status.config(text="✅ Загружен", foreground='green')
                    
                    self.update_loaded_triggers_count()
                    self.log_message(f"✅ Загружен триггер {group_name}: {file_path.name}", 'SUCCESS')
                
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки триггера {group_name}: {e}", 'ERROR')
    
    def process_trigger_file(self, trigger_key, file_path):
        """Обрабатывает файл триггера"""
        try:
            pil_img = Image.open(file_path)
            if pil_img.mode != 'L':
                pil_img_gray = pil_img.convert('L')
            else:
                pil_img_gray = pil_img
            
            img_array = np.array(pil_img_gray)
            
            # Определяем группу по ключу
            if 'group1' in trigger_key:
                group = 'group1'
            elif 'group2' in trigger_key:
                group = 'group2'
            elif 'group3' in trigger_key:
                group = 'group3'
            elif 'group4' in trigger_key:
                group = 'group4'
            elif 'group5' in trigger_key:
                group = 'group5'
            elif 'group6' in trigger_key:
                group = 'group6'
            else:
                group = 'unknown'
            
            self.trigger_images[trigger_key] = {
                'image': img_array,
                'pil_image': pil_img_gray,
                'size': pil_img_gray.size,
                'filepath': file_path,
                'group': group
            }
            return True
        except Exception as e:
            print(f"❌ Ошибка обработки триггера {trigger_key}: {e}")
            return False
    
    def clear_group1(self):
        """Очищает группу 1"""
        # Удаляем триггеры из словаря
        for trigger_key in self.group1_triggers:
            if trigger_key in self.trigger_images:
                del self.trigger_images[trigger_key]
        
        # Очищаем список группы
        self.group1_triggers.clear()
        
        # Обновляем интерфейс
        self.label_group1_status.config(text="Загружено: 0/15", foreground='red')
        self.update_loaded_triggers_count()
        self.log_message("🗑️ Группа 1 очищена", 'INFO')
    
    def clear_group2(self):
        """Очищает группу 2"""
        if self.group2_trigger and self.group2_trigger in self.trigger_images:
            del self.trigger_images[self.group2_trigger]
        
        self.group2_trigger = None
        self.btn_clear_group2.config(state='disabled')
        self.label_group2_status.config(text="Не загружен", foreground='red')
        self.update_loaded_triggers_count()
        self.log_message("🗑️ Группа 2 очищена", 'INFO')
    
    def clear_group3(self):
        """Очищает группу 3"""
        if self.group3_trigger and self.group3_trigger in self.trigger_images:
            del self.trigger_images[self.group3_trigger]
        
        self.group3_trigger = None
        self.btn_clear_group3.config(state='disabled')
        self.label_group3_status.config(text="Не загружен", foreground='red')
        self.update_loaded_triggers_count()
        self.log_message("🗑️ Группа 3 очищена", 'INFO')
    
    def clear_group4(self):
        """Очищает группу 4"""
        # Удаляем триггеры из словаря
        for trigger_key in self.group4_triggers:
            if trigger_key in self.trigger_images:
                del self.trigger_images[trigger_key]
        
        # Очищаем список группы
        self.group4_triggers.clear()
        
        # Очищаем окна с сработавшей группой 4
        self.group4_triggered_windows.clear()
        
        # Обновляем интерфейс
        self.label_group4_status.config(text="Загружено: 0/20", foreground='red')
        self.update_loaded_triggers_count()
        self.log_message("🗑️ Группа 4 очищена", 'INFO')
    
    def clear_group5(self):
        """Очищает группу 5"""
        # Удаляем триггеры из словаря
        for trigger_key in self.group5_triggers:
            if trigger_key in self.trigger_images:
                del self.trigger_images[trigger_key]
        
        # Очищаем список группы
        self.group5_triggers.clear()
        
        # Обновляем интерфейс
        self.label_group5_status.config(text="Загружено: 0/1", foreground='red')
        self.update_loaded_triggers_count()
        self.log_message("🗑️ Группа 5 очищена", 'INFO')
    
    def clear_group6(self):
        """Очищает группу 6"""
        # Удаляем триггеры из словаря
        for trigger_key in self.group6_triggers:
            if trigger_key in self.trigger_images:
                del self.trigger_images[trigger_key]
        
        # Очищаем список группы
        self.group6_triggers.clear()
        
        # Обновляем интерфейс
        self.label_group6_status.config(text="Загружено: 0/8", foreground='red')
        
        # Обновляем статусы для каждого триггера
        for i in range(1, 9):  # Изменено с range(1, 6) на range(1, 9)
            status_label = getattr(self, f'label_group6_trigger{i}_status', None)
            if status_label:
                status_label.config(text="Не загружен", foreground='red')
        
        self.update_loaded_triggers_count()
        self.log_message("🗑️ Группа 6 очищена", 'INFO')
    
    def clear_specific_group6_trigger(self, trigger_num):
        """Очищает конкретный триггер группы 6"""
        trigger_key = f'group6_trigger{trigger_num:02d}'
        
        # Удаляем триггер из словаря
        if trigger_key in self.trigger_images:
            del self.trigger_images[trigger_key]
        
        # Удаляем из списка группы
        if trigger_key in self.group6_triggers:
            self.group6_triggers.remove(trigger_key)
        
        # Обновляем интерфейс
        status_label = getattr(self, f'label_group6_trigger{trigger_num}_status', None)
        if status_label:
            status_label.config(text="Не загружен", foreground='red')
        
        loaded_count = len(self.group6_triggers)
        self.label_group6_status.config(text=f"Загружено: {loaded_count}/8", 
                                      foreground='red' if loaded_count == 0 else 'orange')
        self.update_loaded_triggers_count()
        self.log_message(f"🗑️ Триггер {trigger_num} группы 6 очищен", 'INFO')
    
    def save_all_triggers(self):
        """Сохраняет все триггеры с исправлением ошибки занятого файла"""
        try:
            # Создаем временную папку для сохранения
            temp_triggers_dir = self.dirs['triggers'] / 'temp_save'
            temp_triggers_dir.mkdir(exist_ok=True, parents=True)
            
            saved_count = 0
            
            # Сохраняем триггеры группы 1
            for i, trigger_key in enumerate(self.group1_triggers):
                if trigger_key in self.trigger_images:
                    trigger_data = self.trigger_images[trigger_key]
                    dest_path = temp_triggers_dir / f"group1_{i+1:02d}.png"
                    
                    try:
                        # Сохраняем оригинальный файл если есть
                        if 'filepath' in trigger_data and trigger_data['filepath'].exists():
                            # Копируем с новым именем
                            shutil.copy2(trigger_data['filepath'], dest_path)
                            saved_count += 1
                        elif 'pil_image' in trigger_data:
                            # Или сохраняем из памяти
                            trigger_data['pil_image'].save(dest_path)
                            saved_count += 1
                    except Exception as copy_error:
                        self.log_message(f"⚠️ Ошибка сохранения триггера {trigger_key}: {copy_error}", 'WARNING')
                        continue
            
            # Сохраняем триггеры группы 4
            for i, trigger_key in enumerate(self.group4_triggers):
                if trigger_key in self.trigger_images:
                    trigger_data = self.trigger_images[trigger_key]
                    dest_path = temp_triggers_dir / f"group4_{i+1:02d}.png"
                    
                    try:
                        if 'filepath' in trigger_data and trigger_data['filepath'].exists():
                            shutil.copy2(trigger_data['filepath'], dest_path)
                            saved_count += 1
                        elif 'pil_image' in trigger_data:
                            trigger_data['pil_image'].save(dest_path)
                            saved_count += 1
                    except Exception as copy_error:
                        self.log_message(f"⚠️ Ошибка сохранения триггера {trigger_key}: {copy_error}", 'WARNING')
                        continue
            
            # Сохраняем триггеры группы 5 (только 1 триггер)
            for i, trigger_key in enumerate(self.group5_triggers):
                if trigger_key in self.trigger_images:
                    trigger_data = self.trigger_images[trigger_key]
                    dest_path = temp_triggers_dir / f"group5_{i+1:02d}.png"
                    
                    try:
                        if 'filepath' in trigger_data and trigger_data['filepath'].exists():
                            shutil.copy2(trigger_data['filepath'], dest_path)
                            saved_count += 1
                        elif 'pil_image' in trigger_data:
                            trigger_data['pil_image'].save(dest_path)
                            saved_count += 1
                    except Exception as copy_error:
                        self.log_message(f"⚠️ Ошибка сохранения триггера {trigger_key}: {copy_error}", 'WARNING')
                        continue
            
            # Сохраняем триггеры группы 6 (каждый отдельно)
            for i, trigger_key in enumerate(self.group6_triggers):
                if trigger_key in self.trigger_images:
                    trigger_data = self.trigger_images[trigger_key]
                    # Извлекаем номер триггера
                    trig_num = int(trigger_key.replace('group6_trigger', ''))
                    dest_path = temp_triggers_dir / f"group6_{trig_num:02d}.png"
                    
                    try:
                        if 'filepath' in trigger_data and trigger_data['filepath'].exists():
                            shutil.copy2(trigger_data['filepath'], dest_path)
                            saved_count += 1
                        elif 'pil_image' in trigger_data:
                            trigger_data['pil_image'].save(dest_path)
                            saved_count += 1
                    except Exception as copy_error:
                        self.log_message(f"⚠️ Ошибка сохранения триггера {trigger_key}: {copy_error}", 'WARNING')
                        continue
            
            # Сохраняем одиночные триггеры
            single_triggers = [
                (self.group2_trigger, 'group2_trigger.png'),
                (self.group3_trigger, 'group3_trigger.png')
            ]
            
            for trigger_key, filename in single_triggers:
                if trigger_key and trigger_key in self.trigger_images:
                    trigger_data = self.trigger_images[trigger_key]
                    dest_path = temp_triggers_dir / filename
                    
                    try:
                        if 'filepath' in trigger_data and trigger_data['filepath'].exists():
                            shutil.copy2(trigger_data['filepath'], dest_path)
                            saved_count += 1
                        elif 'pil_image' in trigger_data:
                            trigger_data['pil_image'].save(dest_path)
                            saved_count += 1
                    except Exception as copy_error:
                        self.log_message(f"⚠️ Ошибка сохранения триггера {trigger_key}: {copy_error}", 'WARNING')
                        continue
            
            # Теперь копируем из временной папки в основную
            final_triggers_dir = self.dirs['triggers']
            
            # Удаляем старые файлы в основной папке
            for file in final_triggers_dir.glob("*.*"):
                try:
                    if file.is_file():
                        os.remove(file)
                except Exception as e:
                    self.log_message(f"⚠️ Не удалось удалить старый файл {file.name}: {e}", 'WARNING')
            
            # Копируем новые файлы
            for file in temp_triggers_dir.glob("*.*"):
                if file.is_file():
                    try:
                        shutil.copy2(file, final_triggers_dir / file.name)
                    except Exception as e:
                        self.log_message(f"⚠️ Не удалось скопировать файл {file.name}: {e}", 'WARNING')
            
            # Удаляем временную папку
            try:
                shutil.rmtree(temp_triggers_dir)
            except:
                pass
            
            self.log_message(f"💾 Сохранено {saved_count} триггеров", 'SUCCESS')
            messagebox.showinfo("Успех", f"Сохранено {saved_count} триггеров в папку triggers!")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения триггеров: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def save_trigger_params(self):
        """Сохраняет параметры триггеров"""
        try:
            self.config['threshold_group1'] = self.var_threshold_group1.get() / 100.0
            self.config['threshold_group2'] = self.var_threshold_group2.get() / 100.0
            self.config['threshold_group3'] = self.var_threshold_group3.get() / 100.0
            self.config['threshold_group4'] = self.var_threshold_group4.get() / 100.0
            self.config['threshold_group5'] = self.var_threshold_group5.get() / 100.0
            self.config['threshold_group6'] = self.var_threshold_group6.get() / 100.0
            
            # Сохраняем настройку кулдауна для группы 1 после группы 4
            self.config['group1_cooldown_after_group4'] = self.var_group1_cooldown_after_group4.get()
            
            self.save_config()
            
            self.log_message("💾 Параметры триггеров сохранены", 'SUCCESS')
            messagebox.showinfo("Успех", "Параметры триггеров сохранены!")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения параметров: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def update_loaded_triggers_count(self):
        """Обновляет счетчик загруженных триггеров"""
        total = len(self.trigger_images)
        self.labels_stats['loaded_triggers'].config(text=str(total))
    
    def setup_windows_tab(self):
        """Вкладка управления окнами"""
        title_frame = ttk.Frame(self.tab_windows)
        title_frame.pack(fill='x', pady=10)
        
        ttk.Label(title_frame, text="Управление координатами окон", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(title_frame, text="Настройка сетки окон и загрузка координат").pack()
        
        grid_settings_frame = ttk.LabelFrame(self.tab_windows, text="Настройки сетки", padding=10)
        grid_settings_frame.pack(fill='x', padx=10, pady=5)
        
        rows_frame = ttk.Frame(grid_settings_frame)
        rows_frame.pack(fill='x', pady=5)
        
        ttk.Label(rows_frame, text="Количество рядов:").pack(side='left', padx=5)
        self.var_grid_rows = tk.IntVar(value=self.config['grid_settings']['rows'])
        ttk.Spinbox(rows_frame, from_=1, to=20, textvariable=self.var_grid_rows, width=10).pack(side='left', padx=5)
        
        cols_frame = ttk.Frame(grid_settings_frame)
        cols_frame.pack(fill='x', pady=5)
        
        ttk.Label(cols_frame, text="Количество колонок:").pack(side='left', padx=5)
        self.var_grid_cols = tk.IntVar(value=self.config['grid_settings']['columns'])
        ttk.Spinbox(cols_frame, from_=1, to=20, textvariable=self.var_grid_cols, width=10).pack(side='left', padx=5)
        
        width_frame = ttk.Frame(grid_settings_frame)
        width_frame.pack(fill='x', pady=5)
        
        ttk.Label(width_frame, text="Ширина окна:").pack(side='left', padx=5)
        self.var_window_width = tk.IntVar(value=self.config['grid_settings']['window_width'])
        ttk.Spinbox(width_frame, from_=100, to=2000, textvariable=self.var_window_width, width=10).pack(side='left', padx=5)
        
        height_frame = ttk.Frame(grid_settings_frame)
        height_frame.pack(fill='x', pady=5)
        
        ttk.Label(height_frame, text="Высота окна:").pack(side='left', padx=5)
        self.var_window_height = tk.IntVar(value=self.config['grid_settings']['window_height'])
        ttk.Spinbox(height_frame, from_=100, to=2000, textvariable=self.var_window_height, width=10).pack(side='left', padx=5)
        
        start_frame = ttk.Frame(grid_settings_frame)
        start_frame.pack(fill='x', pady=5)
        
        ttk.Label(start_frame, text="Начало сетки (X):").pack(side='left', padx=5)
        self.var_start_x = tk.IntVar(value=self.config['grid_settings']['start_x'])
        ttk.Spinbox(start_frame, from_=0, to=2000, textvariable=self.var_start_x, width=10).pack(side='left', padx=5)
        
        ttk.Label(start_frame, text="Начало сетки (Y):").pack(side='left', padx=5)
        self.var_start_y = tk.IntVar(value=self.config['grid_settings']['start_y'])
        ttk.Spinbox(start_frame, from_=0, to=2000, textvariable=self.var_start_y, width=10).pack(side='left', padx=5)
        
        gap_frame = ttk.Frame(grid_settings_frame)
        gap_frame.pack(fill='x', pady=5)
        
        ttk.Label(gap_frame, text="Отступ по X:").pack(side='left', padx=5)
        self.var_gap_x = tk.IntVar(value=self.config['grid_settings']['gap_x'])
        ttk.Spinbox(gap_frame, from_=0, to=100, textvariable=self.var_gap_x, width=10).pack(side='left', padx=5)
        
        ttk.Label(gap_frame, text="Отступ по Y:").pack(side='left', padx=5)
        self.var_gap_y = tk.IntVar(value=self.config['grid_settings']['gap_y'])
        ttk.Spinbox(gap_frame, from_=0, to=100, textvariable=self.var_gap_y, width=10).pack(side='left', padx=5)
        
        grid_buttons_frame = ttk.Frame(grid_settings_frame)
        grid_buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(grid_buttons_frame, text="📐 Создать сетку", 
                  command=self.generate_grid,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(grid_buttons_frame, text="📊 Просчитать координаты", 
                  command=self.calculate_grid).pack(side='left', padx=5)
        
        ttk.Button(grid_buttons_frame, text="🗑️ Очистить сетку", 
                  command=self.clear_grid).pack(side='left', padx=5)
        
        file_frame = ttk.LabelFrame(self.tab_windows, text="Загрузка из файла", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)
        
        load_buttons = ttk.Frame(file_frame)
        load_buttons.pack(fill='x', pady=5)
        
        ttk.Button(load_buttons, text="📁 Загрузить координаты", 
                  command=self.load_windows_from_file).pack(side='left', padx=5)
        ttk.Button(load_buttons, text="💾 Сохранить координаты", 
                  command=self.save_windows_to_file).pack(side='left', padx=5)
        
        # Просмотр окон
        preview_frame = ttk.LabelFrame(self.tab_windows, text="Просмотр окон", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Создаем Treeview для отображения окон
        columns = ("Номер", "X1", "Y1", "X2", "Y2", "Ширина", "Высота")
        self.tree_windows = ttk.Treeview(preview_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.tree_windows.heading(col, text=col)
            self.tree_windows.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=self.tree_windows.yview)
        self.tree_windows.configure(yscrollcommand=scrollbar.set)
        
        self.tree_windows.pack(side='left', fill='both', expand=True, padx=(0, 5))
        scrollbar.pack(side='right', fill='y')
        
        # Информация
        info_frame = ttk.LabelFrame(self.tab_windows, text="Информация", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        self.label_windows_info = ttk.Label(info_frame, text="Окон загружено: 0")
        self.label_windows_info.pack(anchor='w', pady=2)
        
        ttk.Label(info_frame, text="Координаты указываются в абсолютных значениях экрана").pack(anchor='w', pady=2)
    
    def generate_grid(self):
        """Генерирует сетку окон"""
        try:
            rows = self.var_grid_rows.get()
            cols = self.var_grid_cols.get()
            window_width = self.var_window_width.get()
            window_height = self.var_window_height.get()
            start_x = self.var_start_x.get()
            start_y = self.var_start_y.get()
            gap_x = self.var_gap_x.get()
            gap_y = self.var_gap_y.get()
            
            self.windows_data = []
            
            for row in range(rows):
                for col in range(cols):
                    x1 = start_x + col * (window_width + gap_x)
                    y1 = start_y + row * (window_height + gap_y)
                    x2 = x1 + window_width
                    y2 = y1 + window_height
                    
                    window_info = {
                        'start_x': x1,
                        'start_y': y1,
                        'end_x': x2,
                        'end_y': y2,
                        'width': window_width,
                        'height': window_height,
                        'row': row,
                        'col': col
                    }
                    
                    self.windows_data.append(window_info)
            
            self.update_windows_treeview()
            self.labels_stats['windows_count'].config(text=str(len(self.windows_data)))
            self.label_windows_info.config(text=f"Окон создано: {len(self.windows_data)}")
            self.log_message(f"📐 Создана сетка {rows}x{cols} ({len(self.windows_data)} окон)", 'SUCCESS')
            
        except Exception as e:
            self.log_message(f"❌ Ошибка создания сетки: {e}", 'ERROR')
    
    def calculate_grid(self):
        """Просчитывает координаты без создания сетки"""
        try:
            rows = self.var_grid_rows.get()
            cols = self.var_grid_cols.get()
            window_width = self.var_window_width.get()
            window_height = self.var_window_height.get()
            start_x = self.var_start_x.get()
            start_y = self.var_start_y.get()
            gap_x = self.var_gap_x.get()
            gap_y = self.var_gap_y.get()
            
            total_windows = rows * cols
            total_width = cols * window_width + (cols - 1) * gap_x
            total_height = rows * window_height + (rows - 1) * gap_y
            end_x = start_x + total_width
            end_y = start_y + total_height
            
            info_text = f"Расчет сетки {rows}x{cols}:\n"
            info_text += f"• Всего окон: {total_windows}\n"
            info_text += f"• Общая ширина: {total_width}px\n"
            info_text += f"• Общая высота: {total_height}px\n"
            info_text += f"• Конечная точка: ({end_x}, {end_y})"
            
            self.label_windows_info.config(text=info_text)
            self.log_message(f"📊 Рассчитана сетка {rows}x{cols} ({total_windows} окон)", 'INFO')
            
        except Exception as e:
            self.log_message(f"❌ Ошибка расчета сетки: {e}", 'ERROR')
    
    def clear_grid(self):
        """Очищает сетку окон"""
        self.windows_data = []
        self.update_windows_treeview()
        self.labels_stats['windows_count'].config(text='0')
        self.label_windows_info.config(text="Окон загружено: 0")
        self.log_message("🗑️ Сетка окон очищена", 'INFO')
    
    def load_windows_from_file(self):
        """Загружает координаты окон из файла"""
        try:
            filetypes = [("JSON файлы", "*.json"), ("Все файлы", "*.*")]
            filepath = filedialog.askopenfilename(
                title="Выберите файл с координатами окон",
                filetypes=filetypes
            )
            
            if filepath:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    self.windows_data = data
                    self.update_windows_treeview()
                    self.labels_stats['windows_count'].config(text=str(len(self.windows_data)))
                    self.label_windows_info.config(text=f"Окон загружено: {len(self.windows_data)}")
                    self.log_message(f"📁 Загружено {len(self.windows_data)} окон из файла", 'SUCCESS')
                else:
                    self.log_message("❌ Неверный формат файла", 'ERROR')
                    
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки файла: {e}", 'ERROR')
    
    def save_windows_to_file(self):
        """Сохраняет координаты окон в файл"""
        try:
            if not self.windows_data:
                messagebox.showwarning("Предупреждение", "Нет окон для сохранения!")
                return
            
            filetypes = [("JSON файлы", "*.json"), ("Все файлы", "*.*")]
            filepath = filedialog.asksaveasfilename(
                title="Сохранить координаты окон",
                defaultextension=".json",
                filetypes=filetypes
            )
            
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.windows_data, f, indent=4, ensure_ascii=False)
                
                self.log_message(f"💾 Координаты {len(self.windows_data)} окон сохранены", 'SUCCESS')
                messagebox.showinfo("Успех", f"Координаты {len(self.windows_data)} окон сохранены!")
                
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения файла: {e}", 'ERROR')
    
    def update_windows_treeview(self):
        """Обновляет Treeview с информацией об окнах"""
        # Очищаем старые данные
        for item in self.tree_windows.get_children():
            self.tree_windows.delete(item)
        
        # Добавляем новые данные
        for i, window in enumerate(self.windows_data):
            values = (
                i + 1,
                window.get('start_x', 0),
                window.get('start_y', 0),
                window.get('end_x', 0),
                window.get('end_y', 0),
                window.get('width', 0),
                window.get('height', 0)
            )
            self.tree_windows.insert('', 'end', values=values)
    
    def setup_recovery_tab(self):
        """Вкладка восстановления"""
        title_frame = ttk.Frame(self.tab_recovery)
        title_frame.pack(fill='x', pady=10)
        
        ttk.Label(title_frame, text="Настройки восстановления окон", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(title_frame, text="Настройка автоматического восстановления окон при обнаружении триггеров").pack()
        
        # Основные настройки
        main_frame = ttk.LabelFrame(self.tab_recovery, text="Основные настройки", padding=10)
        main_frame.pack(fill='x', padx=10, pady=5)
        
        # Интервал проверки
        interval_frame = ttk.Frame(main_frame)
        interval_frame.pack(fill='x', pady=5)
        
        ttk.Label(interval_frame, text="Интервал проверки (сек):").pack(side='left', padx=5)
        self.var_check_interval = tk.IntVar(value=self.config['check_interval'])
        ttk.Spinbox(interval_frame, from_=1, to=60, textvariable=self.var_check_interval, width=10).pack(side='left', padx=5)
        
        # Кулдаун для всех групп (кроме группы 1)
        cooldown_frame = ttk.Frame(main_frame)
        cooldown_frame.pack(fill='x', pady=5)
        
        ttk.Label(cooldown_frame, text="Общий кулдаун (сек):").pack(side='left', padx=5)
        self.var_cooldown_period = tk.IntVar(value=self.cooldown_period)
        ttk.Spinbox(cooldown_frame, from_=5, to=300, textvariable=self.var_cooldown_period, width=10).pack(side='left', padx=5)
        ttk.Label(cooldown_frame, text="(Для всех групп, кроме группы 1)").pack(side='left', padx=5)
        
        # Звуковые оповещения
        sound_frame = ttk.Frame(main_frame)
        sound_frame.pack(fill='x', pady=5)
        
        self.var_sound_alerts = tk.BooleanVar(value=self.config['sound_alerts'])
        ttk.Checkbutton(sound_frame, text="Звуковые оповещения при обнаружении", 
                       variable=self.var_sound_alerts).pack(side='left', padx=5)
        
        # Автосохранение скриншотов
        screenshot_frame = ttk.Frame(main_frame)
        screenshot_frame.pack(fill='x', pady=5)
        
        self.var_auto_save_screenshots = tk.BooleanVar(value=self.config['auto_save_screenshots'])
        ttk.Checkbutton(screenshot_frame, text="Автосохранение скриншотов при обнаружении", 
                       variable=self.var_auto_save_screenshots).pack(side='left', padx=5)
        
        # Мониторинг всех окон
        monitor_frame = ttk.Frame(main_frame)
        monitor_frame.pack(fill='x', pady=5)
        
        self.var_monitor_all_windows = tk.BooleanVar(value=self.config['monitor_all_windows'])
        ttk.Checkbutton(monitor_frame, text="Мониторинг всех окон одновременно", 
                       variable=self.var_monitor_all_windows).pack(side='left', padx=5)
        
        # Уровень логирования
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill='x', pady=5)
        
        ttk.Label(log_frame, text="Уровень логирования:").pack(side='left', padx=5)
        self.var_log_level = tk.StringVar(value=self.config['log_level'])
        log_combo = ttk.Combobox(log_frame, textvariable=self.var_log_level, 
                                values=['minimal', 'normal', 'detailed'], state='readonly', width=10)
        log_combo.pack(side='left', padx=5)
        
        # НОВЫЕ НАСТРОЙКИ ОТДЫХА ПОСЛЕ ВОССТАНОВЛЕНИЯ ОКОН - ИЗМЕНЕНО
        rest_frame = ttk.LabelFrame(self.tab_recovery, text="Настройки отдыха после восстановления окон", padding=10)
        rest_frame.pack(fill='x', padx=10, pady=5)
        
        rest_enable_frame = ttk.Frame(rest_frame)
        rest_enable_frame.pack(fill='x', pady=5)
        
        self.var_rest_enabled = tk.BooleanVar(value=self.config['rest_settings']['enabled'])
        ttk.Checkbutton(rest_enable_frame, text="Включить отдых после N восстановленных окон", 
                       variable=self.var_rest_enabled).pack(side='left', padx=5)
        
        rest_params_frame = ttk.Frame(rest_frame)
        rest_params_frame.pack(fill='x', pady=5)
        
        ttk.Label(rest_params_frame, text="Окон перед отдыхом:").pack(side='left', padx=5)
        self.var_windows_before_rest = tk.IntVar(value=self.config['rest_settings']['windows_before_rest'])
        ttk.Spinbox(rest_params_frame, from_=1, to=100, textvariable=self.var_windows_before_rest, width=10).pack(side='left', padx=5)
        
        ttk.Label(rest_params_frame, text="Длительность отдыха (сек):").pack(side='left', padx=5)
        self.var_rest_duration = tk.IntVar(value=self.config['rest_settings']['rest_duration'])
        ttk.Spinbox(rest_params_frame, from_=1, to=300, textvariable=self.var_rest_duration, width=10).pack(side='left', padx=5)
        
        # Полная приостановка мониторинга во время отдыха
        rest_pause_frame = ttk.Frame(rest_frame)
        rest_pause_frame.pack(fill='x', pady=5)
        
        self.var_pause_monitoring_during_rest = tk.BooleanVar(value=self.config['rest_settings']['pause_monitoring'])
        ttk.Checkbutton(rest_pause_frame, text="Полная приостановка мониторинга во время отдыха", 
                       variable=self.var_pause_monitoring_during_rest).pack(side='left', padx=5)
        
        # Остановка действий во время отдыха
        rest_stop_actions_frame = ttk.Frame(rest_frame)
        rest_stop_actions_frame.pack(fill='x', pady=5)
        
        self.var_stop_actions_during_rest = tk.BooleanVar(value=self.config['rest_settings']['stop_actions'])
        ttk.Checkbutton(rest_stop_actions_frame, text="Остановка действий во время отдыха", 
                       variable=self.var_stop_actions_during_rest).pack(side='left', padx=5)
        
        # Оптимизация
        optim_frame = ttk.LabelFrame(self.tab_recovery, text="Оптимизация", padding=10)
        optim_frame.pack(fill='x', padx=10, pady=5)
        
        # Максимальное количество одновременных восстановлений
        max_recovery_frame = ttk.Frame(optim_frame)
        max_recovery_frame.pack(fill='x', pady=5)
        
        ttk.Label(max_recovery_frame, text="Макс. одновременных восстановлений:").pack(side='left', padx=5)
        self.var_max_concurrent_recoveries = tk.IntVar(value=self.config['optimization']['max_concurrent_recoveries'])
        ttk.Spinbox(max_recovery_frame, from_=1, to=10, textvariable=self.var_max_concurrent_recoveries, width=10).pack(side='left', padx=5)
        
        # Интервал очистки памяти
        memory_frame = ttk.Frame(optim_frame)
        memory_frame.pack(fill='x', pady=5)
        
        ttk.Label(memory_frame, text="Интервал очистки памяти (сек):").pack(side='left', padx=5)
        self.var_memory_cleanup_interval = tk.IntVar(value=self.config['optimization']['memory_cleanup_interval'])
        ttk.Spinbox(memory_frame, from_=10, to=300, textvariable=self.var_memory_cleanup_interval, width=10).pack(side='left', padx=5)
        
        # Пропуск кадров при высокой нагрузке
        skip_frame = ttk.Frame(optim_frame)
        skip_frame.pack(fill='x', pady=5)
        
        ttk.Label(skip_frame, text="Пропускать кадров при нагрузке:").pack(side='left', padx=5)
        self.var_skip_frames_on_busy = tk.IntVar(value=self.config['optimization']['skip_frames_on_busy'])
        ttk.Spinbox(skip_frame, from_=0, to=10, textvariable=self.var_skip_frames_on_busy, width=10).pack(side='left', padx=5)
        
        # Таймаут потоков
        timeout_frame = ttk.Frame(optim_frame)
        timeout_frame.pack(fill='x', pady=5)
        
        ttk.Label(timeout_frame, text="Таймаут потоков (сек):").pack(side='left', padx=5)
        self.var_thread_timeout = tk.IntVar(value=self.config['optimization']['thread_timeout'])
        ttk.Spinbox(timeout_frame, from_=10, to=120, textvariable=self.var_thread_timeout, width=10).pack(side='left', padx=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(self.tab_recovery)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="💾 Сохранить настройки восстановления", 
                  command=self.save_recovery_settings,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🧹 Очистить кэш и временные файлы", 
                  command=self.cleanup_cache).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="📊 Тест производительности", 
                  command=self.run_performance_test).pack(side='left', padx=5)
        
        # Статистика
        stats_frame = ttk.LabelFrame(self.tab_recovery, text="Статистика восстановления", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x')
        
        self.labels_recovery_stats = {}
        recovery_stats = [
            ('Всего восстановлений:', 'total_recoveries', '0'),
            ('Успешных:', 'successful_recoveries', '0'),
            ('Ошибок:', 'failed_recoveries', '0'),
            ('Активных восстановлений:', 'active_recoveries', '0'),
            ('В очереди:', 'queued_recoveries', '0'),
            ('Последнее восстановление:', 'last_recovery_time', 'Нет'),
            ('Среднее время:', 'avg_recovery_time', '0 сек'),
            ('Общее время работы:', 'total_uptime', '0 сек'),
            ('Восстановлено окон:', 'recovered_windows', '0'),  # Новая статистика
        ]
        
        for i, (label, key, value) in enumerate(recovery_stats):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(stats_grid, text=label).grid(row=row, column=col, padx=5, pady=2, sticky='w')
            self.labels_recovery_stats[key] = ttk.Label(stats_grid, text=value, font=('Arial', 9, 'bold'))
            self.labels_recovery_stats[key].grid(row=row, column=col+1, padx=5, pady=2, sticky='w')
    
    def save_recovery_settings(self):
        """Сохраняет настройки восстановления"""
        try:
            self.config['check_interval'] = self.var_check_interval.get()
            self.config['sound_alerts'] = self.var_sound_alerts.get()
            self.config['auto_save_screenshots'] = self.var_auto_save_screenshots.get()
            self.config['monitor_all_windows'] = self.var_monitor_all_windows.get()
            self.config['log_level'] = self.var_log_level.get()
            
            # НОВЫЕ НАСТРОЙКИ ОТДЫХА ПОСЛЕ ВОССТАНОВЛЕНИЯ ОКОН - ИЗМЕНЕНО
            self.config['rest_settings']['enabled'] = self.var_rest_enabled.get()
            self.config['rest_settings']['windows_before_rest'] = self.var_windows_before_rest.get()
            self.config['rest_settings']['rest_duration'] = self.var_rest_duration.get()
            self.config['rest_settings']['pause_monitoring'] = self.var_pause_monitoring_during_rest.get()
            self.config['rest_settings']['stop_actions'] = self.var_stop_actions_during_rest.get()
            
            # Оптимизация
            self.config['optimization']['max_concurrent_recoveries'] = self.var_max_concurrent_recoveries.get()
            self.config['optimization']['memory_cleanup_interval'] = self.var_memory_cleanup_interval.get()
            self.config['optimization']['skip_frames_on_busy'] = self.var_skip_frames_on_busy.get()
            self.config['optimization']['thread_timeout'] = self.var_thread_timeout.get()
            
            # Общий кулдаун
            self.cooldown_period = self.var_cooldown_period.get()
            
            self.save_config()
            
            self.log_message("💾 Настройки восстановления сохранены", 'SUCCESS')
            messagebox.showinfo("Успех", "Настройки восстановления сохранены!")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения настроек восстановления: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def cleanup_cache(self):
        """Очищает кэш и временные файлы"""
        try:
            cache_dirs = ['temp', 'cache']
            cleaned_files = 0
            
            for dir_name in cache_dirs:
                if dir_name in self.dirs:
                    cache_dir = self.dirs[dir_name]
                    for file in cache_dir.glob("*.*"):
                        try:
                            if file.is_file():
                                os.remove(file)
                                cleaned_files += 1
                        except Exception as e:
                            print(f"Не удалось удалить файл {file.name}: {e}")
            
            self.log_message(f"🧹 Очищено {cleaned_files} временных файлов", 'INFO')
            messagebox.showinfo("Успех", f"Очищено {cleaned_files} временных файлов!")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка очистки кэша: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка очистки: {e}")
    
    def run_performance_test(self):
        """Запускает тест производительности"""
        try:
            if not self.windows_data:
                messagebox.showwarning("Предупреждение", "Сначала создайте сетку окон!")
                return
            
            test_result = self.performance_test()
            
            # Отображаем результаты
            result_text = f"Результаты теста производительности:\n\n"
            result_text += f"• Всего окон: {len(self.windows_data)}\n"
            result_text += f"• Время сканирования: {test_result['scan_time']:.2f} сек\n"
            result_text += f"• Время на окно: {test_result['time_per_window']:.3f} сек\n"
            result_text += f"• Окно в секунду: {test_result['windows_per_second']:.1f}\n"
            result_text += f"• Использование памяти: {test_result['memory_usage']:.1f} МБ\n"
            result_text += f"• Загружено триггеров: {test_result['triggers_count']}"
            
            messagebox.showinfo("Тест производительности", result_text)
            self.log_message("📊 Тест производительности завершен", 'INFO')
            
        except Exception as e:
            self.log_message(f"❌ Ошибка теста производительности: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка теста: {e}")
    
    def performance_test(self):
        """Выполняет тест производительности"""
        import psutil
        import gc
        
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / 1024 / 1024  # МБ
        
        start_time = time.time()
        
        # Тестовое сканирование всех окон
        for window_idx, window_info in enumerate(self.windows_data):
            try:
                x1 = window_info.get('start_x', 0)
                y1 = window_info.get('start_y', 0)
                x2 = window_info.get('end_x', x1 + 800)
                y2 = window_info.get('end_y', y1 + 600)
                
                # Делаем тестовый скриншот
                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
                
                # Быстрая проверка на один триггер для теста
                if self.trigger_images:
                    first_trigger = list(self.trigger_images.values())[0]
                    result = cv2.matchTemplate(screenshot_cv, first_trigger['image'], cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # Принудительная сборка мусора каждые 5 окон
                if window_idx % 5 == 0:
                    gc.collect()
                    
            except Exception as e:
                continue
        
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024
        
        scan_time = end_time - start_time
        time_per_window = scan_time / len(self.windows_data) if self.windows_data else 0
        windows_per_second = len(self.windows_data) / scan_time if scan_time > 0 else 0
        memory_usage = end_memory - start_memory
        
        return {
            'scan_time': scan_time,
            'time_per_window': time_per_window,
            'windows_per_second': windows_per_second,
            'memory_usage': memory_usage,
            'triggers_count': len(self.trigger_images)
        }
    
    def setup_statusbar(self):
        """Создает статусбар"""
        self.statusbar = ttk.Frame(self.root, relief='sunken', padding=5)
        self.statusbar.pack(side='bottom', fill='x')
        
        self.label_status = ttk.Label(self.statusbar, text="Готов к работе")
        self.label_status.pack(side='left')
        
        self.label_time = ttk.Label(self.statusbar, text="")
        self.label_time.pack(side='right')
        
        self.update_time()
    
    def update_time(self):
        """Обновляет время в статусбаре"""
        current_time = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
        self.label_time.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def update_gui(self):
        """Обновляет графический интерфейс"""
        # Обновляем статистику
        self.labels_stats['total_detections'].config(text=str(self.detection_count))
        self.labels_stats['action_count'].config(text=str(self.action_counter))
        self.labels_stats['loaded_triggers'].config(text=str(len(self.trigger_images)))
        self.labels_stats['windows_count'].config(text=str(len(self.windows_data)))
        self.labels_stats['total_clicks'].config(text=str(self.total_clicks_performed))
        self.labels_stats['actions_count'].config(text=str(self.action_counter))
        self.labels_stats['recovered_windows'].config(text=str(self.recovered_windows_count))
        
        # Обновляем статус мониторинга
        if self.is_monitoring:
            if self.is_paused:
                status_text = "На паузе"
                status_color = 'orange'
            else:
                status_text = "Активен"
                status_color = 'green'
        else:
            status_text = "Неактивно"
            status_color = 'red'
        
        self.labels_stats['status'].config(text=status_text, foreground=status_color)
        
        # Обновляем последнее действие
        if self.last_detection_time:
            time_str = self.last_detection_time.strftime("%H:%M:%S")
            self.labels_stats['last_action'].config(text=time_str)
        
        # Обновляем окна в кулдауне
        self.labels_stats['windows_cooldown'].config(text=str(len(self.last_triggered_windows)))
        
        # Обновляем статус отдыха
        if self.is_resting:
            if self.rest_start_time:
                rest_elapsed = time.time() - self.rest_start_time
                rest_remaining = max(0, self.config['rest_settings']['rest_duration'] - rest_elapsed)
                rest_text = f"Отдых: {rest_remaining:.0f} сек"
                self.labels_stats['rest_status'].config(text=rest_text, foreground='orange')
            else:
                self.labels_stats['rest_status'].config(text="Отдых", foreground='orange')
        else:
            self.labels_stats['rest_status'].config(text="Активен", foreground='green')
        
        # Обновляем текущий режим
        mode_text = "Действия" if self.current_mode == 'actions_only' else "Восстановление"
        self.labels_stats['current_mode'].config(text=mode_text)
        
        # Обновляем статус автокликов
        if self.auto_clicks_running:
            self.labels_stats['auto_clicks_status'].config(text="Выполнение", foreground='green')
        elif self.auto_clicks_scheduled:
            self.labels_stats['auto_clicks_status'].config(text="Ожидание", foreground='blue')
        else:
            self.labels_stats['auto_clicks_status'].config(text="Отключено", foreground='red')
        
        # Обновляем статус кулдауна группы 1 после группы 4
        if self.group1_cooldown_after_group4_active:
            cooldown_elapsed = time.time() - self.group1_cooldown_after_group4_start
            cooldown_remaining = max(0, self.group1_cooldown_after_group4 - cooldown_elapsed)
            cooldown_text = f"Активен: {cooldown_remaining:.0f} сек"
            self.labels_stats['group1_cooldown_status'].config(text=cooldown_text, foreground='orange')
        else:
            self.labels_stats['group1_cooldown_status'].config(text="Неактивен", foreground='green')
        
        # Обновляем статус ввода пароля
        if self.password_input_active:
            self.labels_stats['password_input_status'].config(text="Активно", foreground='orange')
        else:
            self.labels_stats['password_input_status'].config(text="Неактивно", foreground='green')
        
        # Обновляем скорость работы
        self.labels_stats['detection_speed'].config(text=f"{self.detection_speed:.1f}x")
        self.labels_stats['action_speed'].config(text=f"{self.action_speed:.1f}x")
        self.labels_stats['recovery_speed'].config(text=f"{self.recovery_speed:.1f}x")
        
        # Обновляем восстановленные окна
        self.labels_stats['recovered_windows'].config(text=str(self.recovered_windows_count))
        
        # Обновляем статусбар
        if self.is_monitoring:
            if self.is_paused:
                self.label_status.config(text="Мониторинг на паузе", foreground='orange')
            else:
                status_text = f"Мониторинг активен | Окна: {len(self.windows_data)} | Триггеры: {len(self.trigger_images)}"
                self.label_status.config(text=status_text, foreground='green')
        else:
            self.label_status.config(text="Готов к работе", foreground='black')
        
        # Планируем следующее обновление
        self.root.after(1000, self.update_gui)
    
    def log_message(self, message, category='INFO'):
        """Логирует сообщение"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        if category == 'ERROR':
            color = 'red'
        elif category == 'WARNING':
            color = 'orange'
        elif category == 'SUCCESS':
            color = 'green'
        elif category == 'INFO':
            color = 'blue'
        else:
            color = 'black'
        
        self.log_queue.append((log_entry, color))
        print(log_entry)
    
    def start_monitoring(self):
        """Запускает мониторинг"""
        if self.is_monitoring:
            return
        
        if not self.windows_data:
            messagebox.showwarning("Предупреждение", "Сначала создайте сетку окон!")
            return
        
        if not self.trigger_images:
            if not messagebox.askyesno("Предупреждение", "Не загружены триггеры. Продолжить без триггеров?"):
                return
        
        self.is_monitoring = True
        self.is_paused = False
        
        self.btn_start.config(state='disabled')
        self.btn_stop.config(state='normal')
        self.btn_pause.config(state='normal')
        
        # Сбрасываем счетчики
        self.total_clicks_performed = 0
        
        self.log_message("🚀 Мониторинг запущен", 'SUCCESS')
        
        # Запускаем поток мониторинга
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Останавливает мониторинг"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.is_paused = False
        
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')
        self.btn_pause.config(state='disabled')
        
        self.log_message("⏹ Мониторинг остановлен", 'INFO')
    
    def toggle_pause(self):
        """Включает/выключает паузу"""
        if not self.is_monitoring:
            return
        
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.btn_pause.config(text="▶ ПРОДОЛЖИТЬ")
            self.log_message("⏸ Мониторинг на паузе", 'WARNING')
        else:
            self.btn_pause.config(text="⏸ ПАУЗА")
            self.log_message("▶ Мониторинг продолжен", 'INFO')
    
    def monitoring_loop(self):
        """Основной цикл мониторинга"""
        while self.is_monitoring:
            try:
                if self.is_paused:
                    time.sleep(1)
                    continue
                
                # Проверяем, находимся ли мы в режиме отдыха
                if self.is_resting:
                    # Проверяем, не закончился ли отдых
                    if self.rest_start_time:
                        rest_elapsed = time.time() - self.rest_start_time
                        if rest_elapsed >= self.config['rest_settings']['rest_duration']:
                            # Завершаем отдых и восстанавливаем состояние
                            self.end_rest_period()
                        else:
                            # Все еще отдыхаем
                            time.sleep(1)
                            continue
                    else:
                        self.is_resting = False
                
                # Проверяем текущий режим
                if self.current_mode == 'recovery_only':
                    # В режиме восстановления выполняем только проверку триггеров
                    self.check_all_windows_for_triggers()
                elif self.current_mode == 'actions_only':
                    # В режиме действий проверку триггеров можно пропускать
                    # или выполнять реже, так как основное внимание на действиях
                    if random.random() < 0.3:  # Проверяем только 30% времени
                        self.check_all_windows_for_triggers()
                
                # Оптимизация: пропускаем кадры при высокой нагрузке
                self.skip_counter += 1
                if self.skip_counter >= self.config['optimization']['skip_frames_on_busy']:
                    self.skip_counter = 0
                    time.sleep(0.01)  # Короткая пауза для снижения нагрузки
                
                # Очистка памяти при необходимости
                if time.time() - self.last_memory_cleanup > self.config['optimization']['memory_cleanup_interval']:
                    self.cleanup_memory()
                    self.last_memory_cleanup = time.time()
                
                # Интервал проверки с учетом скорости
                check_interval = self.config['check_interval'] / self.detection_speed
                time.sleep(check_interval)
                
            except Exception as e:
                self.log_message(f"❌ Ошибка в цикле мониторинга: {e}", 'ERROR')
                time.sleep(5)
    
    def start_rest_period(self):
        """Начинает период отдыха с полной приостановкой работы"""
        self.is_resting = True
        self.rest_start_time = time.time()
        self.recovered_windows_count = 0
        
        # Сохраняем текущее состояние
        self.was_monitoring_before_rest = self.is_monitoring
        self.was_actions_before_rest = self.actions_enabled
        
        # Приостанавливаем мониторинг если настроено
        if self.config['rest_settings']['pause_monitoring'] and self.is_monitoring:
            self.is_monitoring = False
            self.btn_start.config(state='normal')
            self.btn_stop.config(state='disabled')
            self.btn_pause.config(state='disabled')
        
        # Останавливаем действия если настроено
        if self.config['rest_settings']['stop_actions'] and self.actions_enabled:
            self.stop_actions()
        
        rest_duration = self.config['rest_settings']['rest_duration']
        self.log_message(f"🛌 Начинается отдых на {rest_duration} секунд", 'INFO')
        
        # Логируем состояние
        if self.config['rest_settings']['pause_monitoring']:
            self.log_message("⏸ Мониторинг приостановлен на время отдыха", 'INFO')
        if self.config['rest_settings']['stop_actions']:
            self.log_message("⏸ Действия остановлены на время отдыха", 'INFO')
    
    def end_rest_period(self):
        """Завершает период отдыха и восстанавливает работу"""
        self.is_resting = False
        self.rest_start_time = None
        
        # Восстанавливаем мониторинг если он был приостановлен
        if self.config['rest_settings']['pause_monitoring'] and self.was_monitoring_before_rest:
            self.is_monitoring = True
            self.btn_start.config(state='disabled')
            self.btn_stop.config(state='normal')
            self.btn_pause.config(state='normal')
        
        # Восстанавливаем действия если они были остановлены
        if self.config['rest_settings']['stop_actions'] and self.was_actions_before_rest:
            self.start_actions()
        
        self.log_message("✅ Отдых завершен, работа восстановлена", 'INFO')
        
        # Логируем восстановление
        if self.config['rest_settings']['pause_monitoring'] and self.was_monitoring_before_rest:
            self.log_message("▶ Мониторинг восстановлен", 'INFO')
        if self.config['rest_settings']['stop_actions'] and self.was_actions_before_rest:
            self.log_message("▶ Действия восстановлены", 'INFO')
    
    def check_all_windows_for_triggers(self):
        """Проверяет все окна на наличие триггеров"""
        if not self.windows_data or not self.trigger_images:
            return
        
        # Проверяем, не находимся ли мы в режиме отдыха
        if self.is_resting:
            # Если отдых активен и мониторинг приостановлен, просто выходим
            if self.config['rest_settings']['pause_monitoring']:
                return
            else:
                # Если мониторинг не приостановлен, просто пропускаем проверки
                # но проверяем время отдыха
                if self.rest_start_time:
                    rest_elapsed = time.time() - self.rest_start_time
                    if rest_elapsed >= self.config['rest_settings']['rest_duration']:
                        self.end_rest_period()
                    else:
                        return
                else:
                    self.is_resting = False
        
        # Проверяем ограничение на одновременные восстановления
        with self.recovery_lock:
            active_count = len(self.active_recoveries)
            if active_count >= self.config['optimization']['max_concurrent_recoveries']:
                return
        
        for window_idx, window_info in enumerate(self.windows_data):
            if not self.is_monitoring or self.is_paused:
                break
            
            # Пропускаем окна, которые уже обрабатываются
            if window_idx in self.active_recoveries:
                continue
            
            # Пропускаем окна в кулдауне (кроме группы 1)
            if window_idx in self.last_triggered_windows:
                last_time = self.last_triggered_windows[window_idx]
                if time.time() - last_time < self.cooldown_period:
                    continue
            
            try:
                # Получаем координаты окна
                x1 = window_info.get('start_x', 0)
                y1 = window_info.get('start_y', 0)
                x2 = window_info.get('end_x', x1 + 800)
                y2 = window_info.get('end_y', y1 + 600)
                
                # Делаем скриншот окна
                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
                
                # Проверяем все триггеры
                for trigger_key in self.trigger_images:
                    trigger_data = self.trigger_images[trigger_key]
                    group = trigger_data.get('group', '')
                    
                    # Проверяем кулдаун для группы 1 после группы 4
                    if group == 'group1' and self.group1_cooldown_after_group4_active:
                        if window_idx in self.group4_triggered_windows:
                            cooldown_elapsed = time.time() - self.group4_triggered_windows[window_idx]
                            if cooldown_elapsed < self.group1_cooldown_after_group4:
                                continue
                    
                    result = cv2.matchTemplate(screenshot_cv, trigger_data['image'], cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    threshold = self.config.get(f'threshold_{group}', 0.65)
                    
                    if max_val >= threshold:
                        # Триггер обнаружен!
                        self.handle_trigger_detection(trigger_key, group, window_idx, window_info, max_val, max_loc)
                        break  # Переходим к следующему окну
                
            except Exception as e:
                self.log_message(f"⚠️ Ошибка проверки окна {window_idx+1}: {e}", 'WARNING')
                continue
    
    def handle_trigger_detection(self, trigger_key, group, window_idx, window_info, confidence, location):
        """Обрабатывает обнаружение триггера"""
        try:
            # Проверяем, не находимся ли мы в режиме ввода пароля
            if self.password_input_active:
                return
            
            self.detection_count += 1
            self.last_detection_time = datetime.now()
            
            # Звуковое оповещение
            if self.config['sound_alerts']:
                try:
                    winsound.Beep(1000, 200)
                except:
                    pass
            
            # Сохранение скриншота
            if self.config['auto_save_screenshots']:
                self.save_detection_screenshot(window_info, trigger_key, confidence)
            
            # Логирование
            confidence_percent = confidence * 100
            self.log_message(f"🎯 Обнаружен {trigger_key} в окне {window_idx+1} (уверенность: {confidence_percent:.1f}%)", 'SUCCESS')
            
            # Обработка в зависимости от группы с использованием сохраненных координат
            if group == 'group1':
                self.handle_group1_trigger(window_idx, window_info)
            elif group == 'group2':
                self.handle_group2_trigger(window_idx, window_info)
            elif group == 'group3':
                self.handle_group3_trigger(window_idx, window_info)
            elif group == 'group4':
                self.handle_group4_trigger(window_idx, window_info, trigger_key)
            elif group == 'group5':
                self.handle_group5_trigger(window_idx, window_info, trigger_key)
            elif group == 'group6':
                self.handle_group6_trigger(window_idx, window_info, trigger_key)
            
            # Добавляем окно в кулдаун (кроме группы 1)
            if group != 'group1':
                self.last_triggered_windows[window_idx] = time.time()
            
            # Проверяем, не нужно ли начать отдых
            if self.config['rest_settings']['enabled']:
                self.recovered_windows_count += 1
                if self.recovered_windows_count >= self.config['rest_settings']['windows_before_rest']:
                    self.start_rest_period()
            
        except Exception as e:
            self.log_message(f"❌ Ошибка обработки триггера: {e}", 'ERROR')
    
    def handle_group1_trigger(self, window_idx, window_info):
        """Обрабатывает триггер группы 1 (2 клика)"""
        try:
            # Получаем координаты кликов для группы 1 из конфигурации
            clicks = self.config['group1_clicks']
            
            if len(clicks) < 2:
                self.log_message(f"⚠️ Для группы 1 настроено недостаточно кликов: {len(clicks)}", 'WARNING')
                return
            
            # Первый клик
            first_click = clicks[0]
            abs_x1 = window_info['start_x'] + first_click['x']
            abs_y1 = window_info['start_y'] + first_click['y']
            
            # Выполняем первый клик с учетом скорости
            pyautogui.moveTo(abs_x1, abs_y1, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            self.total_clicks_performed += 1
            time.sleep(0.1 / self.recovery_speed)
            
            # Второй клик
            second_click = clicks[1]
            abs_x2 = window_info['start_x'] + second_click['x']
            abs_y2 = window_info['start_y'] + second_click['y']
            
            # Выполняем второй клик с учетом скорости
            pyautogui.moveTo(abs_x2, abs_y2, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            self.total_clicks_performed += 1
            
            self.log_message(f"✅ Выполнены 2 клика в окне {window_idx+1} (группа 1)", 'SUCCESS')
            
        except Exception as e:
            self.log_message(f"❌ Ошибка обработки группы 1: {e}", 'ERROR')
    
    def handle_group2_trigger(self, window_idx, window_info):
        """Обрабатывает триггер группы 2 (1 клик)"""
        try:
            # Получаем координаты клика для группы 2 из конфигурации
            click_config = self.config['group2_click']
            x = click_config['x']
            y = click_config['y']
            
            abs_x = window_info['start_x'] + x
            abs_y = window_info['start_y'] + y
            
            # Выполняем клик с учетом скорости
            pyautogui.moveTo(abs_x, abs_y, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            
            # Увеличиваем счетчик кликов
            self.total_clicks_performed += 1
            
            self.log_message(f"✅ Выполнен клик в окне {window_idx+1} (группа 2)", 'SUCCESS')
            
        except Exception as e:
            self.log_message(f"❌ Ошибка обработки группы 2: {e}", 'ERROR')
    
    def handle_group3_trigger(self, window_idx, window_info):
        """Обрабатывает триггер группы 3 (1 клик)"""
        try:
            # Получаем координаты клика для группы 3 из конфигурации
            click_config = self.config['group3_click']
            x = click_config['x']
            y = click_config['y']
            
            abs_x = window_info['start_x'] + x
            abs_y = window_info['start_y'] + y
            
            # Выполняем клик с учетом скорости
            pyautogui.moveTo(abs_x, abs_y, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            
            # Увеличиваем счетчик кликов
            self.total_clicks_performed += 1
            
            self.log_message(f"✅ Выполнен клик в окне {window_idx+1} (группа 3)", 'SUCCESS')
            
        except Exception as e:
            self.log_message(f"❌ Ошибка обработки группы 3: {e}", 'ERROR')
    
    def handle_group4_trigger(self, window_idx, window_info, trigger_key):
        """Обрабатывает триггер группы 4 (1 клик для всех 20 триггеров)"""
        try:
            # Получаем координаты клика для группы 4 из конфигурации
            click_config = self.config['group4_click']
            x = click_config['x']
            y = click_config['y']
            
            abs_x = window_info['start_x'] + x
            abs_y = window_info['start_y'] + y
            
            # Выполняем клик с учетом скорости
            pyautogui.moveTo(abs_x, abs_y, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            
            # Увеличиваем счетчик кликов
            self.total_clicks_performed += 1
            
            # Записываем окно в список окон с сработавшей группой 4
            self.group4_triggered_windows[window_idx] = time.time()
            
            # Получаем номер триггера
            trig_num = int(trigger_key.replace('group4_trigger', ''))
            self.log_message(f"⚡ Группа 4 (триггер {trig_num}) в окне {window_idx+1} - клик ({x},{y})", 'RECOVERY')
            
            # Увеличиваем счетчик восстановленных окон для системы отдыха
            self.recovered_windows_count += 1
            
            # Проверяем, не пора ли отдохнуть
            self.check_rest_required()
            
            # Сохраняем скриншот при обнаружении
            if self.config['auto_save_screenshots']:
                self.save_detection_screenshot(window_idx, f"group4_trigger{trig_num:02d}")
            
            # Звуковое оповещение
            if self.config['sound_alerts']:
                try:
                    winsound.Beep(1500, 300)
                except:
                    pass
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Ошибка обработки триггера группы 4: {e}", 'ERROR')
            return False
        
    def handle_group5_trigger(self, window_idx, window_info, trigger_key):
        """Обрабатывает триггер группы 5 (клик + пароль + клик)"""
        try:
            # Получаем конфигурацию для группы 5
            config = self.config['group5_trigger']
            first_click = config['first_click']
            password = config['password']
            second_click = config['second_click']
            
            # Настройки скорости ввода пароля
            password_settings = self.config.get('password_input_settings', {
                'delay_before_password': 0.2,
                'delay_between_chars': 0.1,
                'min_delay_variation': 0.05,
                'max_delay_variation': 0.15
                })
            
            # Первый клик
            abs_x1 = window_info['start_x'] + first_click['x']
            abs_y1 = window_info['start_y'] + first_click['y']
            
            pyautogui.moveTo(abs_x1, abs_y1, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            self.total_clicks_performed += 1
            
            # Задержка перед вводом пароля с вариацией
            delay_before = password_settings['delay_before_password'] / self.recovery_speed
            delay_before += random.uniform(
                password_settings['min_delay_variation'] / self.recovery_speed,
                password_settings['max_delay_variation'] / self.recovery_speed
            )
            time.sleep(max(0.05, delay_before))
            
            # Ввод пароля с настраиваемой задержкой между символами
            self.password_input_active = True
            for char in password:
                pyautogui.write(char)
                # Задержка между символами с вариацией
                delay_between = password_settings['delay_between_chars'] / self.recovery_speed
                delay_between += random.uniform(
                    password_settings['min_delay_variation'] / self.recovery_speed,
                    password_settings['max_delay_variation'] / self.recovery_speed
                )
                time.sleep(max(0.02, delay_between))
            
            time.sleep(0.1 / self.recovery_speed)
            self.password_input_active = False
            
            # Второй клик
            abs_x2 = window_info['start_x'] + second_click['x']
            abs_y2 = window_info['start_y'] + second_click['y']
            
            pyautogui.moveTo(abs_x2, abs_y2, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            self.total_clicks_performed += 1
            
            self.log_message(f"⚡ Группа 5 в окне {window_idx+1} - клик({first_click['x']},{first_click['y']}) + пароль + клик({second_click['x']},{second_click['y']})", 'RECOVERY')
            
            # Увеличиваем счетчик восстановленных окон для системы отдыха
            self.recovered_windows_count += 1
            
            # Проверяем, не пора ли отдохнуть
            self.check_rest_required()
            
            # Сохраняем скриншот при обнаружении
            if self.config['auto_save_screenshots']:
                self.save_detection_screenshot(window_idx, "group5_trigger")
            
            # Звуковое оповещение
            if self.config['sound_alerts']:
                try:
                    winsound.Beep(1200, 200)
                    time.sleep(0.1)
                    winsound.Beep(1400, 200)
                except:
                    pass
            
            return True
            
        except Exception as e:
            self.password_input_active = False
            self.log_message(f"❌ Ошибка обработки триггера группы 5: {e}", 'ERROR')
            return False
    
    def handle_group6_trigger(self, window_idx, window_info, trigger_key):
        """Обрабатывает триггер группы 6 (5 разных кликов)"""
        try:
            # Получаем номер триггера
            trig_num = int(trigger_key.replace('group6_trigger', ''))
            
            # Для группы 6 используем 5 разных кликов (по порядку триггеров)
            if trig_num <= len(self.config['group6_clicks']):
                click_config = self.config['group6_clicks'][trig_num - 1]
            else:
                # Если триггеров больше 5, используем последний клик
                click_config = self.config['group6_clicks'][-1]
            
            x = click_config['x']
            y = click_config['y']
            
            abs_x = window_info['start_x'] + x
            abs_y = window_info['start_y'] + y
            
            # Выполняем клик с учетом скорости
            pyautogui.moveTo(abs_x, abs_y, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            
            # Увеличиваем счетчик кликов
            self.total_clicks_performed += 1
            
            self.log_message(f"⚡ Группа 6 (триггер {trig_num}) в окне {window_idx+1} - клик ({x},{y})", 'RECOVERY')
            
            # Увеличиваем счетчик восстановленных окон для системы отдыха
            self.recovered_windows_count += 1
            
            # Проверяем, не пора ли отдохнуть
            self.check_rest_required()
            
            # Сохраняем скриншот при обнаружении
            if self.config['auto_save_screenshots']:
                self.save_detection_screenshot(window_idx, f"group6_trigger{trig_num:02d}")
            
            # Звуковое оповещение
            if self.config['sound_alerts']:
                try:
                    winsound.Beep(1600, 250)
                except:
                    pass
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Ошибка обработки триггера группы 6: {e}", 'ERROR')
            return False

    def check_rest_required(self):
        """Проверяет, не пора ли сделать перерыв после восстановления окон"""
        if not self.config['rest_settings']['enabled']:
            return
        
        windows_before_rest = self.config['rest_settings']['windows_before_rest']
        
        if self.recovered_windows_count >= windows_before_rest and not self.is_resting:
            self.start_rest_period()

    def start_rest_period(self):
        """Начинает период отдыха"""
        try:
            self.is_resting = True
            self.rest_start_time = time.time()
            rest_duration = self.config['rest_settings']['rest_duration']
            
            # Сохраняем предыдущие состояния
            self.was_monitoring_before_rest = self.is_monitoring
            self.was_actions_before_rest = self.actions_enabled
            
            # Полная приостановка мониторинга во время отдыха
            if self.config['rest_settings']['pause_monitoring'] and self.is_monitoring:
                self.stop_monitoring()
            
            # Остановка действий во время отдыха
            if self.config['rest_settings']['stop_actions'] and self.actions_enabled:
                self.stop_actions()
            
            # Остановка восстановления во время отдыха
            if self.config['rest_settings']['stop_recovery']:
                self.stop_recovery_mode()
            
            self.log_message(f"⏸ Начинается отдых на {rest_duration} секунд", 'REST')
            
            # Запускаем таймер для завершения отдыха
            self.rest_timer = threading.Timer(rest_duration, self.end_rest_period)
            self.rest_timer.daemon = True
            self.rest_timer.start()
            
            # Обновляем интерфейс
            self.update_gui()
            
        except Exception as e:
            self.log_message(f"❌ Ошибка начала отдыха: {e}", 'ERROR')

    def end_rest_period(self):
        """Завершает период отдыха"""
        try:
            self.is_resting = False
            self.rest_start_time = None
            
            # Восстанавливаем мониторинг, если он был активен
            if self.config['rest_settings']['pause_monitoring'] and self.was_monitoring_before_rest:
                self.start_monitoring()
            
            # Восстанавливаем действия, если они были активны
            if self.config['rest_settings']['stop_actions'] and self.was_actions_before_rest:
                self.start_actions()
            
            # Восстанавливаем режим восстановления, если он был активен
            if self.config['rest_settings']['stop_recovery']:
                self.start_recovery_mode()
            
            # Сбрасываем счетчик восстановленных окон
            self.recovered_windows_count = 0
            
            self.log_message("▶️ Отдых завершен, работа возобновлена", 'REST')
            
            # Обновляем интерфейс
            self.update_gui()
            
        except Exception as e:
            self.log_message(f"❌ Ошибка завершения отдыха: {e}", 'ERROR')

    def save_detection_screenshot(self, window_idx, trigger_name):
        """Сохраняет скриншот окна при обнаружении триггера"""
        try:
            if not self.windows_data or window_idx >= len(self.windows_data):
                return
            
            window_info = self.windows_data[window_idx]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filename = f"{timestamp}_window{window_idx+1:03d}_{trigger_name}.png"
            filepath = self.dirs['screenshots'] / filename
            
            # Делаем скриншот окна
            screenshot = ImageGrab.grab(bbox=(
                window_info['start_x'],
                window_info['start_y'],
                window_info['end_x'],
                window_info['end_y']
            ))
            
            screenshot.save(filepath)
            self.log_message(f"📸 Скриншот сохранен: {filename}", 'INFO')
            
        except Exception as e:
            print(f"⚠️ Ошибка сохранения скриншота: {e}")

    def cleanup_memory(self):
        """Очищает память для предотвращения утечек"""
        try:
            current_time = time.time()
            
            if current_time - self.last_memory_cleanup > self.config['optimization']['memory_cleanup_interval']:
                import gc
                gc.collect()
                self.last_memory_cleanup = current_time
                self.log_message("🧹 Очистка памяти выполнена", 'INFO')
        except Exception as e:
            print(f"⚠️ Ошибка очистки памяти: {e}")

    def check_window_cooldown(self, window_idx, group_name):
        """Проверяет, находится ли окно в кулдауне"""
        try:
            # Проверяем общий кулдаун для всех групп
            if window_idx in self.last_triggered_windows:
                last_trigger_time = self.last_triggered_windows[window_idx]
                if time.time() - last_trigger_time < self.cooldown_period:
                    return True
            
            # Проверяем специальный кулдаун для группы 1 после группы 4
            if group_name == 'group1' and self.group1_cooldown_after_group4_active:
                # Проверяем, есть ли это окно в списке окон с сработавшей группой 4
                if window_idx in self.group4_triggered_windows:
                    group4_trigger_time = self.group4_triggered_windows[window_idx]
                    if time.time() - group4_trigger_time < self.group1_cooldown_after_group4:
                        return True
            
            return False
            
        except Exception as e:
            self.log_message(f"❌ Ошибка проверки кулдауна: {e}", 'ERROR')
            return False

    def start_monitoring(self):
        """Запускает мониторинг"""
        if self.is_monitoring:
            return
        
        if not self.windows_data:
            messagebox.showwarning("Предупреждение", "Сначала создайте сетку окон!")
            return
        
        if not self.trigger_images:
            if not messagebox.askyesno("Предупреждение", 
                                      "Триггеры не загружены. Продолжить без триггеров?"):
                return
        
        self.is_monitoring = True
        self.is_paused = False
        
        self.btn_start.config(state='disabled')
        self.btn_stop.config(state='normal')
        self.btn_pause.config(state='normal')
        
        # Запускаем поток мониторинга
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.log_message("🚀 Мониторинг запущен", 'SUCCESS')

    def stop_monitoring(self):
        """Останавливает мониторинг"""
        self.is_monitoring = False
        
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')
        self.btn_pause.config(state='disabled')
        
        self.log_message("⏹ Мониторинг остановлен", 'INFO')

    def toggle_pause(self):
        """Переключает паузу"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.btn_pause.config(text="▶ ВОЗОБНОВИТЬ")
            self.log_message("⏸ Мониторинг на паузе", 'INFO')
        else:
            self.btn_pause.config(text="⏸ ПАУЗА")
            self.log_message("▶ Мониторинг возобновлен", 'INFO')

    def monitoring_loop(self):
        """Основной цикл мониторинга"""
        last_check_time = 0
        
        while self.is_monitoring:
            try:
                # Проверяем паузу
                if self.is_paused:
                    time.sleep(1)
                    continue
                
                current_time = time.time()
                
                # Проверяем интервал проверки с учетом скорости
                check_interval = self.config['check_interval'] / self.detection_speed
                if current_time - last_check_time < check_interval:
                    time.sleep(0.1)
                    continue
                
                # Пропускаем кадры при высокой нагрузке
                if self.skip_counter < self.config['optimization']['skip_frames_on_busy']:
                    self.skip_counter += 1
                    continue
                
                self.skip_counter = 0
                last_check_time = current_time
                
                # Проверяем все окна
                for window_idx, window_info in enumerate(self.windows_data):
                    if not self.is_monitoring:
                        break
                    
                    self.check_window_for_triggers(window_idx, window_info)
                
                # Очистка памяти
                self.cleanup_memory()
                
                # Обновляем интерфейс каждые 5 циклов
                self.consecutive_checks += 1
                if self.consecutive_checks >= 5:
                    self.consecutive_checks = 0
                    self.root.after(0, self.update_gui)
                
            except Exception as e:
                self.log_message(f"❌ Ошибка в цикле мониторинга: {e}", 'ERROR')
                time.sleep(1)

    def check_window_for_triggers(self, window_idx, window_info):
        """Проверяет окно на наличие триггеров"""
        try:
            # Получаем область окна
            x1 = window_info.get('start_x', 0)
            y1 = window_info.get('start_y', 0)
            x2 = window_info.get('end_x', x1 + 800)
            y2 = window_info.get('end_y', y1 + 600)
            
            # Делаем скриншот окна
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            
            # Проверяем триггеры группы 1 (15 триггеров)
            if not self.check_window_cooldown(window_idx, 'group1'):
                for trigger_key in self.group1_triggers:
                    if self.check_trigger(screenshot_cv, trigger_key, 'group1'):
                        self.handle_group1_trigger(window_idx, window_info, trigger_key)
                        break
            
            # Проверяем триггер группы 2
            if not self.check_window_cooldown(window_idx, 'group2'):
                if self.group2_trigger and self.check_trigger(screenshot_cv, self.group2_trigger, 'group2'):
                    self.handle_group2_trigger(window_idx, window_info)
            
            # Проверяем триггер группы 3
            if not self.check_window_cooldown(window_idx, 'group3'):
                if self.group3_trigger and self.check_trigger(screenshot_cv, self.group3_trigger, 'group3'):
                    self.handle_group3_trigger(window_idx, window_info)
            
            # Проверяем триггеры группы 4 (20 триггеров)
            if not self.check_window_cooldown(window_idx, 'group4'):
                for trigger_key in self.group4_triggers:
                    if self.check_trigger(screenshot_cv, trigger_key, 'group4'):
                        self.handle_group4_trigger(window_idx, window_info, trigger_key)
                        break
            
            # Проверяем триггер группы 5 (1 триггер)
            if not self.check_window_cooldown(window_idx, 'group5'):
                for trigger_key in self.group5_triggers:
                    if self.check_trigger(screenshot_cv, trigger_key, 'group5'):
                        self.handle_group5_trigger(window_idx, window_info, trigger_key)
                        break
            
            # Проверяем триггеры группы 6 (8 триггеров)
            if not self.check_window_cooldown(window_idx, 'group6'):
                for trigger_key in self.group6_triggers:
                    if self.check_trigger(screenshot_cv, trigger_key, 'group6'):
                        self.handle_group6_trigger(window_idx, window_info, trigger_key)
                        break
            
        except Exception as e:
            self.log_message(f"❌ Ошибка проверки окна {window_idx+1}: {e}", 'ERROR')

    def check_trigger(self, screenshot_cv, trigger_key, group_name):
        """Проверяет наличие триггера на скриншоте"""
        try:
            if trigger_key not in self.trigger_images:
                return False
            
            trigger_data = self.trigger_images[trigger_key]
            threshold = self.config[f'threshold_{group_name}']
            
            result = cv2.matchTemplate(screenshot_cv, trigger_data['image'], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            return max_val >= threshold
            
        except Exception as e:
            self.log_message(f"❌ Ошибка проверки триггера {trigger_key}: {e}", 'ERROR')
            return False

    def handle_group1_trigger(self, window_idx, window_info, trigger_key):
        """Обрабатывает триггер группы 1 (2 клика)"""
        try:
            # Получаем номер триггера
            trig_num = int(trigger_key.replace('group1_trigger', ''))
            
            # Получаем координаты для 2 кликов
            click_configs = self.config['group1_clicks']
            
            # Первый клик
            click1 = click_configs[0]
            abs_x1 = window_info['start_x'] + click1['x']
            abs_y1 = window_info['start_y'] + click1['y']
            
            pyautogui.moveTo(abs_x1, abs_y1, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            self.total_clicks_performed += 1
            
            # Второй клик
            click2 = click_configs[1]
            abs_x2 = window_info['start_x'] + click2['x']
            abs_y2 = window_info['start_y'] + click2['y']
            
            pyautogui.moveTo(abs_x2, abs_y2, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            self.total_clicks_performed += 1
            
            self.log_message(f"⚡ Группа 1 (триггер {trig_num}) в окне {window_idx+1} - 2 клика", 'RECOVERY')
            
            # Увеличиваем счетчик восстановленных окон для системы отдыха
            self.recovered_windows_count += 1
            
            # Проверяем, не пора ли отдохнуть
            self.check_rest_required()
            
            # Сохраняем скриншот при обнаружении
            if self.config['auto_save_screenshots']:
                self.save_detection_screenshot(window_idx, f"group1_trigger{trig_num:02d}")
            
            # Звуковое оповещение
            if self.config['sound_alerts']:
                try:
                    winsound.Beep(1000, 200)
                except:
                    pass
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Ошибка обработки триггера группы 1: {e}", 'ERROR')
            return False

    def handle_group2_trigger(self, window_idx, window_info):
        """Обрабатывает триггер группы 2 (1 клик)"""
        try:
            # Получаем координаты клика для группы 2 из конфигурации
            click_config = self.config['group2_click']
            x = click_config['x']
            y = click_config['y']
            
            abs_x = window_info['start_x'] + x
            abs_y = window_info['start_y'] + y
            
            # Выполняем клик с учетом скорости
            pyautogui.moveTo(abs_x, abs_y, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            
            # Увеличиваем счетчик кликов
            self.total_clicks_performed += 1
            
            self.log_message(f"⚡ Группа 2 в окне {window_idx+1} - клик ({x},{y})", 'RECOVERY')
            
            # Увеличиваем счетчик восстановленных окон для системы отдыха
            self.recovered_windows_count += 1
            
            # Проверяем, не пора ли отдохнуть
            self.check_rest_required()
            
            # Сохраняем скриншот при обнаружении
            if self.config['auto_save_screenshots']:
                self.save_detection_screenshot(window_idx, "group2_trigger")
            
            # Звуковое оповещение
            if self.config['sound_alerts']:
                try:
                    winsound.Beep(1100, 250)
                except:
                    pass
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Ошибка обработки триггера группы 2: {e}", 'ERROR')
            return False

    def handle_group3_trigger(self, window_idx, window_info):
        """Обрабатывает триггер группы 3 (1 клик)"""
        try:
            # Получаем координаты клика для группы 3 из конфигурации
            click_config = self.config['group3_click']
            x = click_config['x']
            y = click_config['y']
            
            abs_x = window_info['start_x'] + x
            abs_y = window_info['start_y'] + y
            
            # Выполняем клик с учетом скорости
            pyautogui.moveTo(abs_x, abs_y, duration=0.1 / self.recovery_speed)
            time.sleep(0.05 / self.recovery_speed)
            pyautogui.click()
            
            # Увеличиваем счетчик кликов
            self.total_clicks_performed += 1
            
            self.log_message(f"⚡ Группа 3 в окне {window_idx+1} - клик ({x},{y})", 'RECOVERY')
            
            # Увеличиваем счетчик восстановленных окон для системы отдыха
            self.recovered_windows_count += 1
            
            # Проверяем, не пора ли отдохнуть
            self.check_rest_required()
            
            # Сохраняем скриншот при обнаружении
            if self.config['auto_save_screenshots']:
                self.save_detection_screenshot(window_idx, "group3_trigger")
            
            # Звуковое оповещение
            if self.config['sound_alerts']:
                try:
                    winsound.Beep(1300, 200)
                except:
                    pass
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Ошибка обработки триггера группы 3: {e}", 'ERROR')
            return False
        
    def setup_password_settings_tab(self):
        """Вкладка настройки скорости ввода пароля"""
        title_frame = ttk.Frame(self.tab_password_settings)
        title_frame.pack(fill='x', pady=10)
            
        ttk.Label(title_frame, text="🔐 Настройки скорости ввода пароля", 
                  font=('Arial', 14, 'bold')).pack()
        tk.Label(title_frame, text="Настройка задержек при вводе пароля для группы 5").pack()
            
        # Получаем настройки из конфигурации
        password_settings = self.config.get('password_input_settings', {
            'delay_before_password': 0.2,
            'delay_between_chars': 0.1,
            'min_delay_variation': 0.05,
            'max_delay_variation': 0.15   
        })
            
        # Основные настройки
        main_frame = ttk.LabelFrame(self.tab_password_settings, text="Основные настройки задержек", padding=10)
        main_frame.pack(fill='x', padx=10, pady=5)
            
        # Задержка перед вводом пароля
        delay_before_frame = ttk.Frame(main_frame)
        delay_before_frame.pack(fill='x', pady=5)
            
        ttk.Label(delay_before_frame, text="Задержка перед вводом пароля (сек):").pack(side='left', padx=5)
        self.var_delay_before_password = tk.DoubleVar(value=password_settings['delay_before_password'])
        ttk.Spinbox(delay_before_frame, from_=0.05, to=5.0, increment=0.05, 
                    textvariable=self.var_delay_before_password, width=8).pack(side='left', padx=5)
            
        # Задержка между символами
        delay_between_frame = ttk.Frame(main_frame)
        delay_between_frame.pack(fill='x', pady=5)
        
        ttk.Label(delay_between_frame, text="Задержка между символами (сек):").pack(side='left', padx=5)
        self.var_delay_between_chars = tk.DoubleVar(value=password_settings['delay_between_chars'])
        ttk.Spinbox(delay_between_frame, from_=0.01, to=2.0, increment=0.01, 
                    textvariable=self.var_delay_between_chars, width=8).pack(side='left', padx=5)
            
        # Настройки вариации задержек
        variation_frame = ttk.LabelFrame(self.tab_password_settings, text="Настройки вариации задержек", padding=10)
        variation_frame.pack(fill='x', padx=10, pady=5)
            
        # Минимальная вариация
        min_var_frame = ttk.Frame(variation_frame)
        min_var_frame.pack(fill='x', pady=5)
            
        ttk.Label(min_var_frame, text="Минимальная вариация (сек):").pack(side='left', padx=5)
        self.var_min_delay_variation = tk.DoubleVar(value=password_settings['min_delay_variation'])
        ttk.Spinbox(min_var_frame, from_=0.01, to=1.0, increment=0.01, 
                    textvariable=self.var_min_delay_variation, width=8).pack(side='left', padx=5)
        ttk.Label(min_var_frame, text="(добавляется случайное значение к задержкам)").pack(side='left', padx=5)
            
        # Максимальная вариация
        max_var_frame = ttk.Frame(variation_frame)
        max_var_frame.pack(fill='x', pady=5)
            
        ttk.Label(max_var_frame, text="Максимальная вариация (сек):").pack(side='left', padx=5)
        self.var_max_delay_variation = tk.DoubleVar(value=password_settings['max_delay_variation'])
        ttk.Spinbox(max_var_frame, from_=0.01, to=2.0, increment=0.01, 
                        textvariable=self.var_max_delay_variation, width=8).pack(side='left', padx=5)
            
        # Кнопки управления
        btn_frame = ttk.Frame(self.tab_password_settings)
        btn_frame.pack(fill='x', padx=10, pady=10)
            
        ttk.Button(btn_frame, text="💾 Сохранить настройки пароля", 
                    command=self.save_password_settings,
                    style='Accent.TButton').pack(side='left', padx=5)
            
        ttk.Button(btn_frame, text="🔍 Тестовый ввод пароля", 
                    command=self.test_password_input).pack(side='left', padx=5)
            
        ttk.Button(btn_frame, text="↩️ Сбросить к значениям по умолчанию", 
                    command=self.reset_password_settings).pack(side='left', padx=5)
        
        # Статус
        status_frame = ttk.LabelFrame(self.tab_password_settings, text="Статус", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
            
        self.label_password_status = ttk.Label(status_frame, text="Настройки не сохранены", foreground='red')
        self.label_password_status.pack(anchor='w', pady=2)
            
        # Информация
        info_frame = ttk.LabelFrame(self.tab_password_settings, text="Информация", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
            
        info_text = """
        Настройки применяются при обработке триггера группы 5:
            
        1. Задержка перед вводом пароля - пауза между кликом и началом ввода
        2. Задержка между символами - пауза между каждой буквой пароля
        3. Вариации - случайные значения добавляются к задержкам для естественности
       
        Формула расчета задержки:
        Итоговая_задержка = Базовая_задержка + random(Минимальная_вариация, Максимальная_вариация)
        """
            
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')
            
    def save_password_settings(self):
        """Сохраняет настройки скорости ввода пароля"""
        try:
            password_settings = {
                'delay_before_password': self.var_delay_before_password.get(),
                'delay_between_chars': self.var_delay_between_chars.get(),
                'min_delay_variation': self.var_min_delay_variation.get(),
                'max_delay_variation': self.var_max_delay_variation.get()
            }
            
            self.config['password_input_settings'] = password_settings
            self.save_config()
            
            self.label_password_status.config(text="✅ Настройки пароля сохранены", foreground='green')
            self.log_message("💾 Настройки скорости ввода пароля сохранены", 'SUCCESS')
            messagebox.showinfo("Успех", "Настройки скорости ввода пароля сохранены!")
            
        except Exception as e:
            self.label_password_status.config(text="❌ Ошибка сохранения", foreground='red')
            self.log_message(f"❌ Ошибка сохранения настроек пароля: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")

    def reset_password_settings(self):
        """Сбрасывает настройки пароля к значениям по умолчанию"""
        try:
            self.var_delay_before_password.set(0.2)
            self.var_delay_between_chars.set(0.1)
            self.var_min_delay_variation.set(0.05)
            self.var_max_delay_variation.set(0.15)
            
            self.label_password_status.config(text="Настройки сброшены к значениям по умолчанию", foreground='orange')
            self.log_message("↩️ Настройки пароля сброшены к значениям по умолчанию", 'INFO')
            
        except Exception as e:
            self.log_message(f"❌ Ошибка сброса настроек пароля: {e}", 'ERROR')

    def test_password_input(self):
        """Тестовый ввод пароля"""
        try:
            # Получаем текущие настройки
            password_settings = self.config.get('password_input_settings', {
                'delay_before_password': 0.2,
                'delay_between_chars': 0.1,
                'min_delay_variation': 0.05,
                'max_delay_variation': 0.15
            })
            
            password = self.config['group5_trigger']['password']
            
            messagebox.showinfo("Тест ввода пароля", 
                              f"Будет выполнен тестовый ввод пароля: {password}\n\n"
                              f"Параметры:\n"
                              f"• Задержка перед вводом: {password_settings['delay_before_password']} сек\n"
                              f"• Задержка между символами: {password_settings['delay_between_chars']} сек\n"
                              f"• Вариации: {password_settings['min_delay_variation']}-{password_settings['max_delay_variation']} сек")
            
            # Имитируем ввод пароля
            self.password_input_active = True
            
            # Задержка перед вводом
            delay_before = password_settings['delay_before_password']
            delay_before += random.uniform(
                password_settings['min_delay_variation'],
                password_settings['max_delay_variation']
            )
            time.sleep(max(0.05, delay_before))
            
            # Ввод каждого символа
            for char in password:
                pyautogui.write(char)
                delay_between = password_settings['delay_between_chars']
                delay_between += random.uniform(
                    password_settings['min_delay_variation'],
                    password_settings['max_delay_variation']
                )
                time.sleep(max(0.02, delay_between))
            
            time.sleep(0.1)
            self.password_input_active = False
            
            self.log_message(f"🔍 Тестовый ввод пароля выполнен: {password}", 'INFO')
            messagebox.showinfo("Успех", "Тестовый ввод пароля выполнен!")
            
        except Exception as e:
            self.password_input_active = False
            self.log_message(f"❌ Ошибка тестового ввода пароля: {e}", 'ERROR')
            messagebox.showerror("Ошибка", f"Ошибка тестового ввода: {e}")
    
    def run(self):
        """Запускает приложение"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            self.log_message(f"❌ Критическая ошибка: {e}", 'ERROR')
            messagebox.showerror("Критическая ошибка", f"Программа завершилась с ошибкой:\n{e}")

    def on_closing(self):
        """Обрабатывает закрытие приложения"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            # Останавливаем все потоки
            self.stop_monitoring()
            self.stop_actions()
            
            # Сохраняем конфигурацию
            self.save_config()
            
            # Уничтожаем окно
            self.root.destroy()
    ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')

if __name__ == "__main__":
    app = TriggerDetectorPro()
    app.run()
