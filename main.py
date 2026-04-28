import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library (Личная кинотека)")
        self.root.geometry("750x550")
        
        self.movies = []
        self.data_file = "movies.json"
        
        self.setup_ui()
        self.load_data()  # Автоматическая загрузка при старте

    def setup_ui(self):
        # ── Форма добавления ──
        input_frame = ttk.LabelFrame(self.root, text="Добавить фильм")
        input_frame.pack(fill="x", padx=10, pady=5)

        fields = [
            ("Название:", "title"), ("Жанр:", "genre"),
            ("Год выпуска:", "year"), ("Рейтинг (0-10):", "rating")
        ]
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            self.entries[key] = ttk.Entry(input_frame, width=35)
            self.entries[key].grid(row=i, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(input_frame, text="Добавить фильм", command=self.add_movie).grid(
            row=4, column=0, columnspan=2, pady=10, sticky="ew"
        )

        # ── Фильтрация ──
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация")
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.filter_genre = ttk.Combobox(filter_frame, state="readonly", width=28)
        self.filter_genre.grid(row=0, column=1, padx=5, pady=5)
        self.filter_genre["values"] = ["Все жанры"]

        ttk.Label(filter_frame, text="Год выпуска:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.filter_year = ttk.Entry(filter_frame, width=10)
        self.filter_year.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(filter_frame, text="Применить", command=self.apply_filter).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter).grid(row=0, column=5, padx=5, pady=5)

        # ── Таблица ──
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(table_frame, columns=("title", "genre", "year", "rating"), show="headings")
        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год выпуска")
        self.tree.heading("rating", text="Рейтинг")
        self.tree.column("title", width=250)
        self.tree.column("genre", width=120)
        self.tree.column("year", width=100, anchor="center")
        self.tree.column("rating", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ── Кнопки JSON ──
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_data).pack(side="left", padx=5)

    # ── Валидация ──
    def validate_input(self):
        title = self.entries["title"].get().strip()
        genre = self.entries["genre"].get().strip()
        year_str = self.entries["year"].get().strip()
        rating_str = self.entries["rating"].get().strip()

        if not title or not genre:
            messagebox.showerror("Ошибка ввода", "Поля 'Название' и 'Жанр' не могут быть пустыми.")
            return False, None

        try:
            year = int(year_str)
            if not (1888 <= year <= 2100):
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Год выпуска должен быть целым числом (1888–2100).")
            return False, None

        try:
            rating = float(rating_str)
            if not (0 <= rating <= 10):
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Рейтинг должен быть числом от 0 до 10.")
            return False, None

        return True, {"title": title, "genre": genre, "year": year, "rating": rating}

    # ── Добавление фильма ──
    def add_movie(self):
        is_valid, movie = self.validate_input()
        if not is_valid:
            return

        self.movies.append(movie)
        self.update_table()
        self.update_filter_combobox()
        self.clear_inputs()
        self.save_data(auto=True)

    def clear_inputs(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def update_filter_combobox(self):
        genres = sorted(set(m["genre"] for m in self.movies))
        current = self.filter_genre.get()
        self.filter_genre["values"] = ["Все жанры"] + genres
        if current in self.filter_genre["values"]:
            self.filter_genre.set(current)
        else:
            self.filter_genre.current(0)

    # ── Таблица и фильтрация ──
    def update_table(self, data=None):
        self.tree.delete(*self.tree.get_children())
        for m in (data or self.movies):
            self.tree.insert("", tk.END, values=(m["title"], m["genre"], m["year"], m["rating"]))

    def apply_filter(self):
        genre = self.filter_genre.get()
        year_str = self.filter_year.get().strip()
        filtered = self.movies

        if genre and genre != "Все жанры":
            filtered = [m for m in filtered if m["genre"] == genre]
        if year_str:
            try:
                year = int(year_str)
                filtered = [m for m in filtered if m["year"] == year]
            except ValueError:
                messagebox.showwarning("Внимание", "Год в фильтре должен быть числом.")
                return
        self.update_table(filtered)

    def reset_filter(self):
        self.filter_genre.current(0)
        self.filter_year.delete(0, tk.END)
        self.update_table()

    # ── JSON ──
    def save_data(self, auto=False):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
            if not auto:
                messagebox.showinfo("Успех", "Данные сохранены в movies.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
                self.update_table()
                self.update_filter_combobox()
                if not hasattr(self, "_startup"):
                    messagebox.showinfo("Успех", "Данные загружены из movies.json")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")
        else:
            self.movies = []
            self.update_table()
        self._startup = True

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibraryApp(root)
    root.mainloop()
