import customtkinter as ctk
from tkinter import messagebox
import time
import matplotlib.pyplot as plt
import pandas as pd
from plyer import notification
import random

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер времени")
        self.root.resizable(False, False)  # Запрещаем изменение размера окна

        self.tasks = []
        self.active_tasks = {}
        self.task_frames = {}
        self.break_start_time = {}
        self.time_before_break = {}
        self.work_time = 25
        self.settings_window = None  # Добавляем атрибут для хранения окна настроек
        self.notifications_enabled = True

        self.create_widgets()
        self.create_animations()

    def create_widgets(self):
        # Основные виджеты
        self.task_label = ctk.CTkLabel(self.root, text="Задача:", font=ctk.CTkFont(size=14, weight="bold"))
        self.task_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.task_entry = ctk.CTkEntry(self.root, width=200, font=ctk.CTkFont(size=14))
        self.task_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.start_button = AnimatedButton(self.root, text="Запустить таймер", command=self.start_timer, font=ctk.CTkFont(size=14))
        self.start_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.history_button = AnimatedButton(self.root, text="Показать историю", command=self.show_history, font=ctk.CTkFont(size=14))
        self.history_button.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.chart_button = AnimatedButton(self.root, text="Показать график", command=self.show_chart, font=ctk.CTkFont(size=14))
        self.chart_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.export_button = AnimatedButton(self.root, text="Экспорт в CSV", command=self.export_to_csv, font=ctk.CTkFont(size=14))
        self.export_button.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.settings_button = AnimatedButton(self.root, text="Настройки", command=self.open_settings, font=ctk.CTkFont(size=14))
        self.settings_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # Фрейм для задач
        self.tasks_frame = ctk.CTkFrame(self.root, corner_radius=10, border_width=2)
        self.tasks_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def create_animations(self):
        # Анимация изменения цвета фона
        self.color_button = ctk.CTkButton(self.root, text="Изменить цвет", command=self.change_background_color, font=ctk.CTkFont(size=14))
        self.color_button.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    def change_background_color(self):
        # Изменение цвета фона приложения
        colors = ["lightblue", "lightgreen", "lightyellow", "lightcoral"]
        self.root.configure(bg=random.choice(colors))


    def show_history(self):
        history_window = ctk.CTkToplevel(self.root)
        history_window.title("История задач")
        history_window.resizable(False, False)  # Запрещаем изменение размера окна

        history_listbox = ctk.CTkTextbox(history_window, width=400, height=300, font=ctk.CTkFont(size=12))
        history_listbox.pack(pady=10)

        for task, elapsed in self.tasks:
            history_listbox.insert(ctk.END, f"{task} - {elapsed:.2f} секунд\n")

    def start_timer(self):
        if len(self.active_tasks) >= 6:
            messagebox.showwarning("Предупреждение", "Нельзя запустить более 5 задач одновременно.")
            return

        task_name = self.task_entry.get()
        if task_name:
            if task_name in self.active_tasks:
                messagebox.showwarning("Предупреждение", "Эта задача уже запущена.")
                return

            self.active_tasks[task_name] = time.time()
            self.add_task_frame(task_name)
            self.task_entry.delete(0, ctk.END)

            self.root.after(self.work_time * 60 * 1000, lambda: self.start_break(task_name))
        else:
            messagebox.showwarning("Предупреждение", "Введите название задачи.")

    def add_task_frame(self, task_name):
        # Определяем позицию в сетке
        row = len(self.task_frames) // 2
        col = len(self.task_frames) % 2

        frame = ctk.CTkFrame(self.tasks_frame, corner_radius=10, border_width=2)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        task_label = ctk.CTkLabel(frame, text=task_name, width=200, font=ctk.CTkFont(size=14, weight="bold"))
        task_label.pack(pady=5)

        time_label = ctk.CTkLabel(frame, text="00:00:00", font=ctk.CTkFont(size=14))
        time_label.pack(pady=5)

        break_label = ctk.CTkLabel(frame, text="Перерыв: 00:00:00", font=ctk.CTkFont(size=14))
        break_label.pack(pady=5)

        stop_button = AnimatedButton(frame, text="Остановить", command=lambda: self.stop_task(task_name), font=ctk.CTkFont(size=14))
        stop_button.pack(pady=5)

        self.task_frames[task_name] = (frame, time_label, break_label)
        self.update_timer(task_name)

    def update_timer(self, task_name):
        if task_name in self.active_tasks:
            elapsed_time = time.time() - self.active_tasks[task_name]
            time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            self.task_frames[task_name][1].configure(text=time_str)

        if task_name in self.break_start_time:
            break_elapsed_time = time.time() - self.break_start_time[task_name]
            break_time_str = time.strftime("%H:%M:%S", time.gmtime(break_elapsed_time))
            self.task_frames[task_name][2].configure(text=f"Перерыв: {break_time_str}")

        self.root.after(1000, lambda: self.update_timer(task_name))

    def stop_timer(self):
        # Удаляем метод, так как он больше не нужен
        pass

    def show_chart(self):
        if not self.tasks:
            messagebox.showwarning("Предупреждение", "Нет данных для отображения графика.")
            return

        task_names = [task[0] for task in self.tasks]
        elapsed_times = [task[1] for task in self.tasks]

        plt.figure(figsize=(10, 6))
        plt.barh(task_names, elapsed_times, color='skyblue')
        plt.xlabel('Время (секунды)')
        plt.title('Время, затраченное на задачи')
        plt.show()

    def export_to_csv(self):
        if not self.tasks:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта.")
            return

        df = pd.DataFrame(self.tasks, columns=["Задача", "Время (секунды)"])
        df.to_csv("task_history.csv", index=False)
        messagebox.showinfo("Успех", "Данные успешно экспортированы в task_history.csv")

    def open_settings(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()  # Если окно настроек уже открыто, поднимаем его
            return

        self.settings_window = ctk.CTkToplevel(self.root)
        self.settings_window.title("Настройки")
        self.settings_window.resizable(False, False)  # Запрещаем изменение размера окна
        self.root.withdraw()  # Делаем главное окно неактивным

        ctk.CTkLabel(self.settings_window, text="Рабочее время (в минутах):", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.work_time_entry = ctk.CTkEntry(self.settings_window, font=ctk.CTkFont(size=14))
        self.work_time_entry.pack(pady=5)

        ctk.CTkLabel(self.settings_window, text="Время перерыва (в минутах):", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.break_time_entry = ctk.CTkEntry(self.settings_window, font=ctk.CTkFont(size=14))
        self.break_time_entry.pack(pady=5)

        self.notifications_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.settings_window, text="Включить уведомления", variable=self.notifications_var, font=ctk.CTkFont(size=14)).pack(pady=5)

        save_button = ctk.CTkButton(self.settings_window, text="Сохранить", command=lambda: self.save_settings(self.settings_window), font=ctk.CTkFont(size=14))
        save_button.pack(pady=10)

        self.settings_window.protocol("WM_DELETE_WINDOW", self.on_settings_close)  # Обработчик закрытия окна настроек

    def on_settings_close(self):
        self.settings_window.destroy()  # Удаляем ссылку на окно настроек
        self.settings_window = None
        self.root.deiconify()  # Возвращаем главное окно

    def save_settings(self, window):
        try:
            self.work_time = int(self.work_time_entry.get())
            if self.work_time <= 0:
                raise ValueError("Рабочее время должно быть положительным числом.")

            self.break_time = int(self.break_time_entry.get())
            if self.break_time < 0:
                raise ValueError("Время перерыва не может быть отрицательным.")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            return

        self.notifications_enabled = self.notifications_var.get()
        messagebox.showinfo("Успех", "Настройки сохранены.")
        window.destroy()

    def start_break(self, task_name):
        if task_name in self.active_tasks:
            start_time = self.active_tasks.pop(task_name)
            elapsed_time = time.time() - start_time
            self.tasks.append((task_name, elapsed_time))

            self.break_start_time[task_name] = time.time()
            self.time_before_break[task_name] = elapsed_time

            if self.notifications_enabled:
                notification.notify(
                    title="Время перерыва!",
                    message=f"Вы проработали {self.work_time} минут над задачей '{task_name}'. Пора сделать перерыв на {self.break_time} минут.",
                    timeout=10
                )

            self.update_timer(task_name)
            self.root.after(self.break_time * 60 * 1000, lambda: self.end_break(task_name))

    def end_break(self, task_name):
        if task_name in self.break_start_time:
            break_elapsed_time = time.time() - self.break_start_time.pop(task_name)
            self.tasks.append((f"Перерыв для {task_name}", break_elapsed_time))

            if self.notifications_enabled:
                notification.notify(
                    title="Перерыв завершен!",
                    message=f"Перерыв для задачи '{task_name}' завершен. Время перерыва: {break_elapsed_time:.2f} секунд. Возвращайтесь к работе.",
                    timeout=10
                )

            elapsed_time_before_break = self.time_before_break.pop(task_name)
            self.active_tasks[task_name] = time.time() - elapsed_time_before_break
            self.update_timer(task_name)

            self.root.after(self.work_time * 60 * 1000, lambda: self.start_break(task_name))

    def stop_task(self, task_name):
        if task_name in self.active_tasks:
            start_time = self.active_tasks.pop(task_name)
            elapsed_time = time.time() - start_time
            self.tasks.append((task_name, elapsed_time))
        elif task_name in self.break_start_time:
            break_start_time = self.break_start_time.pop(task_name)
            break_elapsed_time = time.time() - break_start_time
            self.tasks.append((f"Перерыв для {task_name}", break_elapsed_time))

        if task_name in self.task_frames:
            frame, _, _ = self.task_frames.pop(task_name)
            frame.destroy()

        if self.notifications_enabled:
            notification.notify(
                title="Задача завершена",
                message=f"Вы завершили задачу: {task_name}",
                timeout=10
            )

class AnimatedButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_color = self.cget("fg_color")  # Измените 'background' на 'fg_color'
        self.hover_color = "lightblue"
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(fg_color=self.hover_color)  # Измените 'background' на 'fg_color'

    def on_leave(self, event):
        self.configure(fg_color=self.default_color)  # Измените 'background' на 'fg_color'



    def move(self):
        coordinates = self.canvas.coords(self.image)
        if coordinates[2] >= self.canvas.winfo_width() or coordinates[0] < 0:
            self.xVelocity = -self.xVelocity
        if coordinates[3] >= self.canvas.winfo_height() or coordinates[1] < 0:
            self.yVelocity = -self.yVelocity

        self.canvas.move(self.image, self.xVelocity, self.yVelocity)

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = TimeTrackerApp(root)
    root.mainloop()
