import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from abc import ABC, abstractmethod
from datetime import datetime
import os

# ==================== ООП КЛАСОВЕ ====================

class Person(ABC):
    """Абстрактен клас за представяне на човек"""
    
    def __init__(self, name, age, id_number):
        self._name = name
        self._age = age
        self._id_number = id_number
    
    @property
    def name(self):
        return self._name
    
    @property
    def age(self):
        return self._age
    
    @property
    def id_number(self):
        return self._id_number
    
    @abstractmethod
    def get_info(self):
        pass
    
    @abstractmethod
    def get_role(self):
        pass


class Student(Person):
    """Клас за представяне на студент"""
    
    def __init__(self, name, age, id_number, faculty, year, grades=None):
        super().__init__(name, age, id_number)
        self._faculty = faculty
        self._year = year
        self._grades = grades if grades else []
        self._enrolled_date = datetime.now().strftime("%Y-%m-%d")
    
    @property
    def faculty(self):
        return self._faculty
    
    @property
    def year(self):
        return self._year
    
    @property
    def grades(self):
        return self._grades
    
    def add_grade(self, subject, grade):
        if 2 <= grade <= 6:
            self._grades.append({"subject": subject, "grade": grade})
            return True
        return False
    
    def calculate_average(self):
        if not self._grades:
            return 0.0
        total = sum(g["grade"] for g in self._grades)
        return round(total / len(self._grades), 2)
    
    def get_info(self):
        avg = self.calculate_average()
        return (f"Студент: {self._name} | Възраст: {self._age} | "
                f"Факултет: {self._faculty} | Курс: {self._year} | "
                f"Среден успех: {avg:.2f}")
    
    def get_role(self):
        return "Студент"
    
    def to_dict(self):
        return {
            "name": self._name,
            "age": self._age,
            "id_number": self._id_number,
            "faculty": self._faculty,
            "year": self._year,
            "grades": self._grades,
            "enrolled_date": self._enrolled_date
        }
    
    @classmethod
    def from_dict(cls, data):
        student = cls(
            data.get("name", "Unknown"),
            data.get("age", 0),
            data.get("id_number", "0"),
            data.get("faculty", "N/A"),
            data.get("year", 1),
            data.get("grades", [])
        )
        student._enrolled_date = data.get("enrolled_date", datetime.now().strftime("%Y-%m-%d"))
        return student


class GraduateStudent(Student):
    """Клас за магистър/докторант"""
    
    def __init__(self, name, age, id_number, faculty, year, thesis_topic, grades=None):
        super().__init__(name, age, id_number, faculty, year, grades)
        self._thesis_topic = thesis_topic
    
    @property
    def thesis_topic(self):
        return self._thesis_topic
    
    def get_info(self):
        avg = self.calculate_average()
        return (f"Магистър: {self._name} | Възраст: {self._age} | "
                f"Факултет: {self._faculty} | Курс: {self._year} | "
                f"Тема: {self._thesis_topic} | Среден успех: {avg:.2f}")
    
    def get_role(self):
        return "Магистър/Докторант"
    
    def to_dict(self):
        data = super().to_dict()
        data["thesis_topic"] = self._thesis_topic
        data["type"] = "graduate"
        return data
    
    @classmethod
    def from_dict(cls, data):
        # Тук използваме .get() за по-голяма сигурност
        student = cls(
            data.get("name", "Unknown"),
            data.get("age", 0),
            data.get("id_number", "0"),
            data.get("faculty", "N/A"),
            data.get("year", 1),
            data.get("thesis_topic", "Няма зададена тема"),
            data.get("grades", [])
        )
        student._enrolled_date = data.get("enrolled_date", datetime.now().strftime("%Y-%m-%d"))
        return student


class StudentManager:
    """Клас за управление на студентите"""
    
    def __init__(self, filename="students.json"):
        self._students = []
        self._filename = filename
        self.load_from_file()
    
    def add_student(self, student):
        if any(s.id_number == student.id_number for s in self._students):
            raise ValueError(f"Студент с ID {student.id_number} вече съществува!")
        self._students.append(student)
        self.save_to_file()
    
    def remove_student(self, id_number):
        for i, student in enumerate(self._students):
            if student.id_number == id_number:
                removed = self._students.pop(i)
                self.save_to_file()
                return removed
        raise ValueError(f"Студент с ID {id_number} не е намерен!")
    
    def find_student(self, id_number):
        for student in self._students:
            if student.id_number == id_number:
                return student
        return None
    
    def get_all_students(self):
        return self._students
    
    def save_to_file(self):
        try:
            data = [s.to_dict() for s in self._students]
            with open(self._filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Грешка при запазване: {e}")
    
    def load_from_file(self):
        try:
            if not os.path.exists(self._filename):
                self._students = []
                return

            with open(self._filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._students = []
                for item in data:
                    if item.get("type") == "graduate":
                        self._students.append(GraduateStudent.from_dict(item))
                    else:
                        self._students.append(Student.from_dict(item))
        except (FileNotFoundError, json.JSONDecodeError):
            self._students = []
        except Exception as e:
            print(f"Грешка при зареждане: {e}")
            self._students = []


# ==================== GUI ПРИЛОЖЕНИЕ ====================

class StudentManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Система за управление на студенти")
        self.root.geometry("1200x700")
        
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'light': '#ecf0f1',
            'dark': '#34495e',
            'white': '#ffffff'
        }
        
        self.root.configure(bg=self.colors['light'])
        self.manager = StudentManager()
        self.setup_styles()
        self.create_widgets()
        self.refresh_student_list()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Primary.TButton', background=self.colors['secondary'], foreground='white', font=('Arial', 10, 'bold'))
        style.configure('Success.TButton', background=self.colors['success'], foreground='white', font=('Arial', 10, 'bold'))
        style.configure('Danger.TButton', background=self.colors['danger'], foreground='white', font=('Arial', 10, 'bold'))
        style.configure('Treeview', rowheight=30, font=('Arial', 10))
        style.configure('Treeview.Heading', background=self.colors['primary'], foreground='white', font=('Arial', 11, 'bold'))

    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg=self.colors['primary'], height=70)
        header.pack(fill=tk.X)
        tk.Label(header, text="🎓 СТУДЕНТСКА ИНФОРМАЦИОННА СИСТЕМА", font=('Arial', 18, 'bold'), bg=self.colors['primary'], fg='white').pack(pady=15)

        main_frame = tk.Frame(self.root, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Menu
        menu_frame = tk.Frame(main_frame, bg='white', width=220)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        menu_frame.pack_propagate(False)

        ttk.Button(menu_frame, text="➕ Нов Бакалавър", style='Primary.TButton', command=self.add_student_dialog).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(menu_frame, text="🎓 Нов Магистър", style='Primary.TButton', command=self.add_graduate_dialog).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(menu_frame, text="📝 Добави Оценка", style='Success.TButton', command=self.add_grade_dialog).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(menu_frame, text="🗑 Изтрий", style='Danger.TButton', command=self.delete_student).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(menu_frame, text="📊 Статистика", style='Success.TButton', command=self.show_statistics).pack(fill=tk.X, padx=10, pady=5)

        self.info_label = tk.Label(menu_frame, text="Общо: 0", font=('Arial', 11, 'bold'), bg='white', fg=self.colors['primary'])
        self.info_label.pack(side=tk.BOTTOM, pady=20)

        # Right Table
        table_frame = tk.Frame(main_frame, bg='white')
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        cols = ('ID', 'Име', 'Възраст', 'Факултет', 'Курс', 'Успех')
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings')
        for col in cols: self.tree.heading(col, text=col); self.tree.column(col, width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def refresh_student_list(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        students = self.manager.get_all_students()
        for s in students:
            self.tree.insert('', tk.END, values=(s.id_number, s.name, s.age, s.faculty, s.year, f"{s.calculate_average():.2f}"))
        self.info_label.config(text=f"Студенти в базата: {len(students)}")

    def add_student_dialog(self):
        self._base_dialog("Добавяне на Бакалавър", is_graduate=False)

    def add_graduate_dialog(self):
        self._base_dialog("Добавяне на Магистър", is_graduate=True)

    def _base_dialog(self, title, is_graduate):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x450")
        dialog.configure(bg='white')
        
        fields = [("Име:", "name"), ("Възраст (16-100):", "age"), ("Фак. Номер:", "id"), ("Факултет:", "fac"), ("Курс:", "year")]
        if is_graduate: fields.append(("Тема дипломна:", "thesis"))
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(dialog, text=label, bg='white').pack(pady=(10, 0))
            e = tk.Entry(dialog, bg=self.colors['light'], relief=tk.FLAT, bd=5)
            e.pack(padx=20, fill=tk.X)
            entries[key] = e

        def save():
            try:
                name = entries['name'].get().strip()
                age = int(entries['age'].get())
                id_num = entries['id'].get().strip()
                fac = entries['fac'].get().strip()
                year = int(entries['year'].get())

                # ВАЛИДАЦИЯ НА ДАННИТЕ
                if not name or not id_num: raise ValueError("Името и ID са задължителни!")
                if not (16 <= age <= 100): raise ValueError("Възрастта трябва да е между 16 и 100!")
                if year < 1: raise ValueError("Курсът трябва да е поне 1!")

                if is_graduate:
                    thesis = entries['thesis'].get().strip()
                    if not thesis: raise ValueError("Въведете тема на дипломна работа!")
                    student = GraduateStudent(name, age, id_num, fac, year, thesis)
                else:
                    if year > 4: raise ValueError("Бакалавърският курс е до 4-ти!")
                    student = Student(name, age, id_num, fac, year)

                self.manager.add_student(student)
                messagebox.showinfo("Успех", "Записът е добавен!")
                dialog.destroy()
                self.refresh_student_list()
            except ValueError as e:
                messagebox.showerror("Грешка", f"Невалидни данни: {e}")

        tk.Button(dialog, text="ЗАПАЗИ", bg=self.colors['success'], fg='white', command=save).pack(pady=20)

    def add_grade_dialog(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("!", "Изберете студент!")
        
        id_num = self.tree.item(sel[0])['values'][0]
        student = self.manager.find_student(str(id_num))
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Оценка")
        dialog.geometry("300x200")
        
        tk.Label(dialog, text=f"Предмет:").pack()
        subj = tk.Entry(dialog); subj.pack()
        tk.Label(dialog, text=f"Оценка (2-6):").pack()
        grd = tk.Entry(dialog); grd.pack()

        def add():
            try:
                if student.add_grade(subj.get(), float(grd.get())):
                    self.manager.save_to_file()
                    self.refresh_student_list()
                    dialog.destroy()
                else: raise ValueError()
            except: messagebox.showerror("!", "Грешна оценка!")
        
        tk.Button(dialog, text="Добави", command=add).pack(pady=10)

    def delete_student(self):
        sel = self.tree.selection()
        if not sel: return
        id_num = str(self.tree.item(sel[0])['values'][0])
        if messagebox.askyesno("?", "Изтриване?"):
            self.manager.remove_student(id_num)
            self.refresh_student_list()

    def show_statistics(self):
        students = self.manager.get_all_students()
        if not students: return messagebox.showinfo("Статистика", "Няма данни.")
        
        avg = sum(s.calculate_average() for s in students) / len(students)
        best = max(students, key=lambda s: s.calculate_average())
        
        msg = f"Общо студенти: {len(students)}\n"
        msg += f"Среден успех на випуска: {avg:.2f}\n"
        msg += f"Най-добър студент: {best.name} ({best.calculate_average():.2f})"
        messagebox.showinfo("📊 Статистика", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementGUI(root)
    root.mainloop()