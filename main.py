import json
import os
from tkinter import *
from tkinter import ttk, messagebox

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("850x500")
        self.root.resizable(True, True)

        # Файл для хранения данных
        self.data_file = "movies.json"

        # Список фильмов
        self.movies = []

        # Переменные для полей ввода
        self.title_var = StringVar()
        self.genre_var = StringVar()
        self.year_var = StringVar()
        self.rating_var = StringVar()

        # Переменные для фильтров
        self.filter_genre_var = StringVar()
        self.filter_year_var = StringVar()

        # Загрузка данных при старте
        self.load_data()

        # Создание интерфейса
        self.create_widgets()

        # Обновление таблицы
        self.refresh_table()

    def create_widgets(self):
        # === Панель ввода нового фильма ===
        input_frame = LabelFrame(self.root, text="Добавить новый фильм", padx=10, pady=10, font=("Arial", 10, "bold"))
        input_frame.pack(fill="x", padx=10, pady=5)

        # Название
        Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        Entry(input_frame, textvariable=self.title_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        # Жанр
        Label(input_frame, text="Жанр:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        Entry(input_frame, textvariable=self.genre_var, width=20).grid(row=0, column=3, padx=5, pady=5)

        # Год
        Label(input_frame, text="Год выпуска:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        Entry(input_frame, textvariable=self.year_var, width=10).grid(row=1, column=1, padx=5, pady=5)

        # Рейтинг
        Label(input_frame, text="Рейтинг (0-10):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        Entry(input_frame, textvariable=self.rating_var, width=10).grid(row=1, column=3, padx=5, pady=5)

        # Кнопка добавления
        Button(input_frame, text="Добавить фильм", command=self.add_movie, bg="#4CAF50", fg="white", padx=10).grid(row=2, column=0, columnspan=4, pady=10)

        # === Панель фильтрации ===
        filter_frame = LabelFrame(self.root, text="Фильтрация", padx=10, pady=10, font=("Arial", 10, "bold"))
        filter_frame.pack(fill="x", padx=10, pady=5)

        Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5, pady=5)
        Entry(filter_frame, textvariable=self.filter_genre_var, width=20).grid(row=0, column=1, padx=5, pady=5)

        Label(filter_frame, text="Фильтр по году:").grid(row=0, column=2, padx=5, pady=5)
        Entry(filter_frame, textvariable=self.filter_year_var, width=10).grid(row=0, column=3, padx=5, pady=5)

        Button(filter_frame, text="Применить фильтр", command=self.refresh_table, bg="#2196F3", fg="white").grid(row=0, column=4, padx=10, pady=5)
        Button(filter_frame, text="Сбросить фильтры", command=self.clear_filters, bg="#FF9800", fg="white").grid(row=0, column=5, padx=5, pady=5)

        # === Таблица для отображения фильмов ===
        table_frame = Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание таблицы Treeview
        columns = ("ID", "Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Настройка заголовков
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Год", text="Год")
        self.tree.heading("Рейтинг", text="Рейтинг")

        # Настройка ширины колонок
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Название", width=250)
        self.tree.column("Жанр", width=150)
        self.tree.column("Год", width=80, anchor="center")
        self.tree.column("Рейтинг", width=80, anchor="center")

        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка удаления выбранного фильма
        Button(self.root, text="Удалить выбранный фильм", command=self.delete_movie, bg="#f44336", fg="white", padx=10).pack(pady=10)

    def add_movie(self):
        # Получение данных из полей
        title = self.title_var.get().strip()
        genre = self.genre_var.get().strip()
        year_str = self.year_var.get().strip()
        rating_str = self.rating_var.get().strip()

        # Проверка на пустые поля
        if not title or not genre or not year_str or not rating_str:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        # Проверка года
        try:
            year = int(year_str)
            if year < 1888 or year > 2030:
                messagebox.showerror("Ошибка", "Год должен быть от 1888 до 2030!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом!")
            return

        # Проверка рейтинга
        try:
            rating = float(rating_str)
            if rating < 0 or rating > 10:
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
            return

        # Создание ID (автоинкремент)
        movie_id = max([m["id"] for m in self.movies] + [0]) + 1

        # Добавление фильма
        movie = {
            "id": movie_id,
            "title": title,
            "genre": genre,
            "year": year,
            "rating": rating
        }
        self.movies.append(movie)

        # Сохранение и обновление
        self.save_data()
        self.refresh_table()

        # Очистка полей
        self.title_var.set("")
        self.genre_var.set("")
        self.year_var.set("")
        self.rating_var.set("")

        messagebox.showinfo("Успех", f"Фильм \"{title}\" добавлен!")

    def delete_movie(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите фильм для удаления!")
            return

        # Получение ID фильма
        item = self.tree.item(selected[0])
        movie_id = item["values"][0]

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", "Удалить выбранный фильм?"):
            self.movies = [m for m in self.movies if m["id"] != movie_id]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Фильм удален!")

    def refresh_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Фильтрация
        filtered_movies = self.movies.copy()

        genre_filter = self.filter_genre_var.get().strip().lower()
        if genre_filter:
            filtered_movies = [m for m in filtered_movies if genre_filter in m["genre"].lower()]

        year_filter = self.filter_year_var.get().strip()
        if year_filter:
            try:
                year_int = int(year_filter)
                filtered_movies = [m for m in filtered_movies if m["year"] == year_int]
            except ValueError:
                pass  # Если ввели не число, просто игнорируем фильтр по году

        # Сортировка по ID (или можно по году/названию)
        filtered_movies.sort(key=lambda x: x["id"])

        # Заполнение таблицы
        for movie in filtered_movies:
            self.tree.insert("", "end", values=(
                movie["id"],
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}"
            ))

    def clear_filters(self):
        self.filter_genre_var.set("")
        self.filter_year_var.set("")
        self.refresh_table()

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.movies = []
        else:
            # Начальные тестовые данные
            self.movies = [
                {"id": 1, "title": "Побег из Шоушенка", "genre": "Драма", "year": 1994, "rating": 9.3},
                {"id": 2, "title": "Крестный отец", "genre": "Криминал", "year": 1972, "rating": 9.2},
                {"id": 3, "title": "Темный рыцарь", "genre": "Боевик", "year": 2008, "rating": 9.0},
                {"id": 4, "title": "Криминальное чтиво", "genre": "Криминал", "year": 1994, "rating": 8.9}
            ]
            self.save_data()

if __name__ == "__main__":
    root = Tk()
    app = MovieLibrary(root)
    root.mainloop()
