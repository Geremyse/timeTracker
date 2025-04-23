import tkinter as tk
from tkinter import messagebox
import time
import matplotlib.pyplot as plt
import pandas as pd

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер времени")

        self.tasks = []
        self.current_task = None
        self.timer_running = False
        self.start_time = None
        self.elapsed_time = 0

        self.create_widgets()

    def create_widgets(self):
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

        self.task_listbox = tk.Listbox(self.root)
        self.task_listbox.pack()

        self.chart_button = tk.Button(self.root, text="Показать график", command=self.show_chart)
        self.chart_button.pack()

        self.export_button = tk.Button(self.root, text="Экспорт в CSV", command=self.export_to_csv)
        self.export_button.pack()

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("История задач")

        history_listbox = tk.Listbox(history_window)
        history_listbox.pack()

        for task, elapsed in self.tasks:
            history_listbox.insert(tk.END, f"{task} - {elapsed:.2f} секунд")

    def start_timer(self):
        task_name = self.task_entry.get()
        if task_name:
            self.current_task = task_name
            self.timer_running = True
            self.start_time = time.time()  # Запоминаем время начала
            self.task_listbox.insert(tk.END, f"Запущена задача: {task_name}")
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Предупреждение", "Введите название задачи.")

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.elapsed_time = time.time() - self.start_time  # Вычисляем затраченное время
            self.tasks.append((self.current_task, self.elapsed_time))  # Сохраняем задачу и время
            self.task_listbox.insert(tk.END,
                                     f"Задача завершена: {self.current_task} (Время: {self.elapsed_time:.2f} секунд)")
            self.current_task = None
        else:
            messagebox.showwarning("Предупреждение", "Таймер не запущен.")

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


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()
