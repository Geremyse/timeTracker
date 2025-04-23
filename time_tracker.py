import tkinter as tk
from tkinter import messagebox

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер времени")

        self.tasks = []
        self.current_task = None
        self.timer_running = False

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

        self.task_listbox = tk.Listbox(self.root)
        self.task_listbox.pack()

    def start_timer(self):
        task_name = self.task_entry.get()
        if task_name:
            self.current_task = task_name
            self.timer_running = True
            self.task_listbox.insert(tk.END, f"Запущена задача: {task_name}")
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Предупреждение", "Введите название задачи.")

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.task_listbox.insert(tk.END, f"Задача завершена: {self.current_task}")
            self.current_task = None
        else:
            messagebox.showwarning("Предупреждение", "Таймер не запущен.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()
