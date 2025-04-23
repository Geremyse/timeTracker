import tkinter as tk
from tkinter import messagebox
import time
import matplotlib.pyplot as plt
import pandas as pd
from plyer import notification

class TimeTrackerApp:
    def __init__(self, root):
        print("Initializing TimeTrackerApp")
        self.root = root
        self.root.title("Трекер времени")

        self.tasks = []
        self.active_tasks = {}  # Хранит информацию о каждой активной задаче
        self.task_frames = {}  # Хранит фреймы для каждой задачи
        self.break_start_time = {}  # Хранит время начала перерыва для каждой задачи
        self.time_before_break = {}  # Хранит время, прошедшее до перерыва
        self.work_time = 25  # По умолчанию 25 минут
        self.notifications_enabled = True

        self.create_widgets()

    def create_widgets(self):
        print("Creating widgets")
        self.task_label = tk.Label(self.root, text="Задача:")
        self.task_label.pack()

        self.task_entry = tk.Entry(self.root)
        self.task_entry.pack()

        self.start_button = tk.Button(self.root, text="Запустить таймер", command=self.start_timer)
        self.start_button.pack()

        self.stop_button = tk.Button(self.root, text="Остановить таймер", command=self.stop_timer)
        self.stop_button.pack()

        self.history_button = tk.Button(self.root, text="Показать историю", command=self.show_history)
        self.history_button.pack()

        self.chart_button = tk.Button(self.root, text="Показать график", command=self.show_chart)
        self.chart_button.pack()

        self.export_button = tk.Button(self.root, text="Экспорт в CSV", command=self.export_to_csv)
        self.export_button.pack()

        self.settings_button = tk.Button(self.root, text="Настройки", command=self.open_settings)
        self.settings_button.pack()

        self.tasks_canvas = tk.Canvas(self.root)
        self.tasks_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tasks_canvas.yview)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self.tasks_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.tasks_canvas.bind('<Configure>', lambda e: self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox("all")))

        self.tasks_frame = tk.Frame(self.tasks_canvas)
        self.tasks_canvas.create_window((0, 0), window=self.tasks_frame, anchor="nw")

    def show_history(self):
        print("Showing history")
        history_window = tk.Toplevel(self.root)
        history_window.title("История задач")

        history_listbox = tk.Listbox(history_window)
        history_listbox.pack()

        for task, elapsed in self.tasks:
            history_listbox.insert(tk.END, f"{task} - {elapsed:.2f} секунд")

    def start_timer(self):
        print("Starting timer")
        task_name = self.task_entry.get()
        if task_name:
            if task_name in self.active_tasks:
                messagebox.showwarning("Предупреждение", "Эта задача уже запущена.")
                return

            self.active_tasks[task_name] = time.time()  # Запоминаем время начала
            self.add_task_frame(task_name)
            self.task_entry.delete(0, tk.END)

            # Запускаем таймер для рабочего времени
            self.root.after(self.work_time * 60 * 1000, lambda: self.start_break(task_name))
        else:
            messagebox.showwarning("Предупреждение", "Введите название задачи.")

    def add_task_frame(self, task_name):
        frame = tk.Frame(self.tasks_frame, borderwidth=2, relief="groove")
        frame.pack(fill=tk.X, pady=2)

        task_label = tk.Label(frame, text=task_name)
        task_label.pack(side=tk.LEFT, padx=5)

        time_label = tk.Label(frame, text="00:00:00")
        time_label.pack(side=tk.LEFT, padx=5)

        break_label = tk.Label(frame, text="Перерыв: 00:00:00")
        break_label.pack(side=tk.LEFT, padx=5)

        stop_button = tk.Button(frame, text="Остановить", command=lambda: self.stop_task(task_name))
        stop_button.pack(side=tk.RIGHT, padx=5)

        self.task_frames[task_name] = (frame, time_label, break_label)
        self.update_timer(task_name)

    def update_timer(self, task_name):
        if task_name in self.active_tasks:
            elapsed_time = time.time() - self.active_tasks[task_name]
            time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            self.task_frames[task_name][1].config(text=time_str)

        if task_name in self.break_start_time:
            # Обновление времени перерыва
            break_elapsed_time = time.time() - self.break_start_time[task_name]
            break_time_str = time.strftime("%H:%M:%S", time.gmtime(break_elapsed_time))
            self.task_frames[task_name][2].config(text=f"Перерыв: {break_time_str}")

        self.root.after(1000, lambda: self.update_timer(task_name))

    def stop_timer(self):
        print("Stopping timer")
        task_name = self.task_entry.get()
        if task_name in self.active_tasks:
            start_time = self.active_tasks.pop(task_name)
            elapsed_time = time.time() - start_time
            self.tasks.append((task_name, elapsed_time))

            # Удаляем фрейм задачи
            frame, _ = self.task_frames.pop(task_name)
            frame.destroy()

            if self.notifications_enabled:
                notification.notify(
                    title="Задача завершена",
                    message=f"Вы завершили задачу: {task_name} (Время: {elapsed_time:.2f} секунд)",
                    timeout=10
                )
        else:
            messagebox.showwarning("Предупреждение", "Эта задача не запущена.")

    def show_chart(self):
        print("Showing chart")
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
        print("Exporting to CSV")
        if not self.tasks:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта.")
            return

        df = pd.DataFrame(self.tasks, columns=["Задача", "Время (секунды)"])
        df.to_csv("task_history.csv", index=False)
        messagebox.showinfo("Успех", "Данные успешно экспортированы в task_history.csv")

    def open_settings(self):
        print("Opening settings")
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки")

        tk.Label(settings_window, text="Рабочее время (в минутах):").pack()
        self.work_time_entry = tk.Entry(settings_window)
        self.work_time_entry.pack()

        tk.Label(settings_window, text="Время перерыва (в минутах):").pack()
        self.break_time_entry = tk.Entry(settings_window)
        self.break_time_entry.pack()

        tk.Label(settings_window, text="Уведомления:").pack()
        self.notifications_var = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_window, text="Включить уведомления", variable=self.notifications_var).pack()

        save_button = tk.Button(settings_window, text="Сохранить", command=lambda: self.save_settings(settings_window))
        save_button.pack()

    def save_settings(self, window):
        print("Saving settings")
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

            # Сохраняем время начала перерыва и время, прошедшее до перерыва
            self.break_start_time[task_name] = time.time()
            self.time_before_break[task_name] = elapsed_time

            if self.notifications_enabled:
                notification.notify(
                    title="Время перерыва!",
                    message=f"Вы проработали {self.work_time} минут над задачей '{task_name}'. Пора сделать перерыв на {self.break_time} минут.",
                    timeout=10
                )

            # Обновляем таймер перерыва
            self.update_timer(task_name)

            # Запускаем таймер для окончания перерыва
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

            # Возвращаем задачу в активное состояние с учетом времени до перерыва
            elapsed_time_before_break = self.time_before_break.pop(task_name)
            self.active_tasks[task_name] = time.time() - elapsed_time_before_break
            self.update_timer(task_name)

            # Запускаем таймер для следующего перерыва
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

        # Удаляем фрейм задачи
        if task_name in self.task_frames:
            frame, _, _ = self.task_frames.pop(task_name)
            frame.destroy()

        if self.notifications_enabled:
            notification.notify(
                title="Задача завершена",
                message=f"Вы завершили задачу: {task_name}",
                timeout=10
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()
