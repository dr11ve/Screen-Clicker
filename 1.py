from pynput.mouse import Controller, Button
from pynput.keyboard import Controller as KeyboardController, Key, Listener
import time
import random
import tkinter as tk
from tkinter import messagebox, simpledialog
import os

# Файл для сохранения координат
COORD_FILE = "coordinates.txt"

# Инициализация контроллеров
mouse = Controller()  # Контроллер мыши
keyboard_controller = KeyboardController()  # Контроллер клавиатуры

# Глобальные переменные
click_points = []
num_squares = 4  # По умолчанию 4 зоны
min_clicks = 500
max_clicks = 2000
min_delay_click = 0.1
max_delay_click = 0.4
min_delay_cycle = 35
max_delay_cycle = 55
running = True
cycle_count = 0  # Счётчик циклов

# Функция обработки кликов в окне Tkinter
def on_click(event):
    global click_points
    if len(click_points) < num_squares * 2:
        canvas_x, canvas_y = event.x, event.y
        screen_x = root.winfo_rootx() + canvas_x
        screen_y = root.winfo_rooty() + canvas_y
        click_points.append((screen_x, screen_y))
        print(f"Выбрана точка: ({screen_x}, {screen_y})")
        
        canvas.create_oval(canvas_x - 5, canvas_y - 5, canvas_x + 5, canvas_y + 5, fill="red")
        
        if len(click_points) == num_squares * 2:
            root.destroy()

# Функция для остановки скрипта
def stop_script():
    global running
    running = False
    print("Скрипт остановлен нажатием пробела.")
    listener.stop()

# Функция для выбора количества зон
def ask_num_squares():
    global num_squares
    num_squares = simpledialog.askinteger("Выбор зон", "Сколько зон кликов вы хотите выбрать?", minvalue=1, maxvalue=20)
    if not num_squares:
        exit()

# Функция для настройки кликов и задержек
def ask_click_settings():
    global min_clicks, max_clicks, min_delay_click, max_delay_click, min_delay_cycle, max_delay_cycle
    min_clicks = simpledialog.askinteger("Настройки кликов", "Минимальное количество кликов:", minvalue=1)
    max_clicks = simpledialog.askinteger("Настройки кликов", "Максимальное количество кликов:", minvalue=min_clicks)
    min_delay_click = simpledialog.askfloat("Задержка между кликами", "Минимальная задержка (сек):", minvalue=0.01)
    max_delay_click = simpledialog.askfloat("Задержка между кликами", "Максимальная задержка (сек):", minvalue=min_delay_click)
    min_delay_cycle = simpledialog.askfloat("Задержка между циклами", "Минимальная задержка (сек):", minvalue=0.1)
    max_delay_cycle = simpledialog.askfloat("Задержка между циклами", "Максимальная задержка (сек):", minvalue=min_delay_cycle)

# Функция для выбора зон кликов
def select_squares():
    global root, canvas
    root = tk.Tk()
    root.title("Выберите зоны кликов")
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")

    label = tk.Label(root, text=f"Кликните в {num_squares * 2} точках (по 2 на каждую зону)", font=("Arial", 14), bg="white")
    label.pack()

    canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="lightgray")
    canvas.pack(fill="both", expand=True)
    canvas.bind("<Button-1>", on_click)

    root.mainloop()

# Сохранение координат в файл
def save_coordinates():
    with open(COORD_FILE, "w") as file:
        file.write(f"{num_squares}\n")
        for x, y in click_points:
            file.write(f"{x},{y}\n")
    print("Координаты сохранены.")

# Загрузка координат из файла
def load_coordinates():
    if os.path.exists(COORD_FILE):
        with open(COORD_FILE, "r") as file:
            lines = file.readlines()
            num_squares_saved = int(lines[0].strip())
            points = [tuple(map(int, line.strip().split(","))) for line in lines[1:]]
            if len(points) == num_squares_saved * 2:
                print(f"Загружены сохранённые координаты ({num_squares_saved} зон).")
                return num_squares_saved, points
    return None

# Эмуляция клика с человеческим поведением
def simulate_real_click(x, y, area):
    current_x, current_y = mouse.position
    
    # Если курсор далеко от цели, плавно перемещаем его к начальной точке
    if abs(current_x - x) > 50 or abs(current_y - y) > 50:
        steps = random.randint(5, 15)
        for i in range(steps + 1):
            interp_x = current_x + (x - current_x) * i / steps
            interp_y = current_y + (y - current_y) * i / steps
            mouse.position = (interp_x, interp_y)
            time.sleep(random.uniform(0.005, 0.02))
    
    # Выполнение клика
    mouse.press(Button.left)
    time.sleep(random.uniform(0.03, 0.08))
    mouse.release(Button.left)
    
    # Периодическое небольшое смещение с шансом 20%
    if random.random() < 0.2:  # 20% шанс смещения
        offset_x = random.randint(-10, 10)  # Небольшие отклонения в пределах ±10 пикселей
        offset_y = random.randint(-10, 10)
        new_x = max(min(x + offset_x, area["x2"]), area["x1"])
        new_y = max(min(y + offset_y, area["y2"]), area["y1"])
        mouse.position = (new_x, new_y)
        time.sleep(random.uniform(0.05, 0.15))  # Пауза после смещения

# Обновление страницы для macOS (Command + R)
def refresh_page():
    print("Обновляем страницу (Command + R)")
    keyboard_controller.press(Key.cmd)
    keyboard_controller.press('r')
    keyboard_controller.release('r')
    keyboard_controller.release(Key.cmd)
    time.sleep(2)

# Основной цикл кликов
def main_loop():
    global cycle_count
    while running:
        cycle_count += 1
        print(f"Цикл #{cycle_count}")
        
        for area in areas:
            num_clicks = random.randint(min_clicks, max_clicks)
            print(f"Кликаем в зоне {area} {num_clicks} раз")
            
            # Начальная точка в центре области
            target_x = (area["x1"] + area["x2"]) // 2
            target_y = (area["y1"] + area["y2"]) // 2
            mouse.position = (target_x, target_y)
            
            for _ in range(num_clicks):
                if not running:
                    break
                simulate_real_click(target_x, target_y, area)
                # Задержка между кликами с учетом человеческого фактора
                time.sleep(random.uniform(min_delay_click, max_delay_click))
            refresh_page()  # Обновление после каждой области

        delay = random.uniform(min_delay_cycle, max_delay_cycle)
        print(f"Ожидание перед следующим циклом: {delay:.2f} сек")
        time.sleep(delay)

# Запуск слушателя клавиатуры
listener = Listener(on_press=lambda key: stop_script() if key == Key.space else None)
listener.start()

# Основной запуск
loaded_data = load_coordinates()

if loaded_data:
    num_squares, click_points = loaded_data
else:
    ask_num_squares()
    select_squares()
    save_coordinates()

# Запрос настроек
ask_click_settings()

# Преобразование точек в области
areas = []
for i in range(0, num_squares * 2, 2):
    x1, y1 = click_points[i]
    x2, y2 = click_points[i + 1]
    areas.append({"x1": min(x1, x2), "y1": min(y1, y2), "x2": max(x1, x2), "y2": max(y1, y2)})

# Старт
print("Старт через 3 секунды...")
time.sleep(3)
main_loop()