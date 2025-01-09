import tkinter as tk
from tkinter import filedialog, messagebox
import os
import random
from tkinter import font
import re
from docx import Document

class QuizApp():
    def __init__(self):
        pass

    def parse_quiz(self, text, duplicates=True):
        blocks = [block.strip() for block in text.strip().split("\n\n") if block.strip()]
        
        self.questions = []
        seen_questions = set()
        
        for block in blocks:
            lines = block.split("\n")
            question = lines[0].strip()
            
            if not duplicates and question in seen_questions:
                continue
            
            answers = [line.strip() for line in lines[1:]]
            correct_answers = [re.sub(r"^\+\s*", "", answer).strip() for answer in answers if re.match(r"^\s*\+\s*", answer)]
            all_answers = [re.sub(r"^\+\s*", "", answer).strip() for answer in answers]
            
            random.shuffle(all_answers)
            
            self.questions.append({
                "question": question,
                "all_answers": all_answers,
                "correct_answers": correct_answers
            })
            
            if not duplicates:
                seen_questions.add(question)
        
        random.shuffle(self.questions)

        return self.questions

    def read_file(self, file_path):
        try:
            if file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            elif file_path.endswith('.docx'):
                doc = Document(file_path)
                text = ''
                for paragraph in doc.paragraphs:
                    text += paragraph.text + '\n'
                return text
            else:
                return ""
        except FileNotFoundError:
            return f"Файл по пути {file_path} не найден."
        except Exception as e:
            return f"Произошла ошибка: {e}"

class UI():
    def __init__(self):
        self.quiz = QuizApp()

        self.root = tk.Tk()
        self.root.geometry("800x600")

        self.font_initialize()
        self.variable_initialize()

    def variable_initialize(self):
        self.file_path = ""
        self.text_from_file = ""
        self.right_answer = []
        self.answer = []
        self.entry_num_from_user = 0
        self.num_question = 1
        self.question_count = 0
        self.test = []
        self.checkbox_repeat_var = tk.BooleanVar(value=True)
        self.checkbox_show_correct_answer_var = tk.BooleanVar(value=True)

    def font_initialize(self):
        self.question_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=12, weight="bold")
        
    def start_window(self):
        self.choose_file_button = tk.Button(self.root, text="Выбрать файл" if self.file_path == "" else self.file_path.split("/")[-1], command=lambda: self.select_file())
        self.choose_file_button.pack(pady=10)

        self.count_label = tk.Label(self.root, text="Укажите количество вопросов для тестирования")
        self.count_label.pack(pady=10)

        self.count_entry = tk.Entry(self.root)
        self.count_entry.pack(pady=0)
        self.count_entry.insert(0, self.entry_num_from_user)

        self.test_start_button = tk.Button(self.root, text="Начать тестирование", command=lambda: self.test_start())
        self.test_start_button.pack(pady=20)

        self.settings_button = tk.Button(self.root, text="Настройки", command=lambda: self.settings_window())
        self.settings_button.pack(pady=20)

    def settings_window(self):
        self.settings_window_instance = tk.Toplevel(self.root)
        self.settings_window_instance.title("Настройки")
        self.settings_window_instance.geometry("300x200")
        self.settings_window_instance.grab_set()

        checkmark_repeat_question = tk.Checkbutton(self.settings_window_instance, text="Повтор одинаковых вопросов", anchor="w", variable=self.checkbox_repeat_var)
        checkmark_repeat_question.pack(pady=10)

        checkmark_show_correct_answer = tk.Checkbutton(self.settings_window_instance, text="Показывать правильный ответ", anchor="w", variable=self.checkbox_show_correct_answer_var)
        checkmark_show_correct_answer.pack(pady=10)


    def destroy_start_window(self):
        self.choose_file_button.destroy()
        self.count_label.destroy()
        self.count_entry.destroy()
        self.test_start_button.destroy()
        self.settings_button.destroy()

    def test_start(self):
        if self.open_file(True):
            self.destroy_start_window()

            self.num_question = 0
            self.show_error_num = 0
            self.right_answer = []
            self.answer = []
            self.main_cycle()

    def select_file(self):
        self.file_path = filedialog.askopenfilename(title="Выберите файл")
        if self.file_path:
            file_name = self.file_path.split("/")[-1]
            self.choose_file_button.config(text=file_name)

        self.open_file(False)
            
    def open_file(self, start):
        prev_text_from_file = self.text_from_file
        if self.file_path != "":
            self.text_from_file = self.quiz.read_file(self.file_path)
        elif ((prev_text_from_file == self.text_from_file and prev_text_from_file == "") or (prev_text_from_file != "" and self.text_from_file == "")) and not start:
            return False
        elif self.text_from_file != "":
            self.test = self.quiz.parse_quiz(self.text_from_file, self.checkbox_repeat_var.get())
            try:
                entry_num = abs(int(self.count_entry.get()))
                self.entry_num_from_user = str(entry_num)
                if entry_num != 0:
                    self.test = self.test[:entry_num]
                self.question_count = len(self.test)
                return True
            except ValueError:
                messagebox.showerror(title="Ошибка", message="Количество вопросов указано неверно")
                return False
        else:
            messagebox.showerror(title="Ошибка", message="Вы не выбрали файл, содержащий вопросы, либо вопросы внутри файла хранятся неправильно!")

    def main_cycle(self):
        if self.num_question < self.question_count:
            self.create_question_text(self.root, self.num_question)
            self.create_question_button(self.root, self.num_question, True)
        else:
            percentage_correct = (self.right_answer.count(True) / self.num_question) * 100
            mark = 2 if percentage_correct < 40 else 3 if percentage_correct < 70 else 4 if percentage_correct < 90 else 5
            messagebox.showinfo("Тест завершен", f"Вы ответили правильно на {self.right_answer.count(True)}/{self.num_question}\nПроцент правильных ответов: {percentage_correct:.1f}%\nВаша оценка: {mark}")
            if self.right_answer.count(False) > 0:
                self.show_error_window()
            self.start_window()

    def show_error_window(self):
        self.error_window = tk.Toplevel(self.root)
        self.error_window.title("Проверка на ошибки")
        self.error_window.geometry("600x400")
        self.error_window.grab_set()
        self.show_error_num = 0

        self.error_cycle()

    def error_cycle(self):
        self.create_question_text(self.error_window, self.show_error_num)
        self.create_question_button(self.error_window, self.show_error_num, False)

        for btn in self.current_button:
            btn.config(command=lambda: None)

        while self.show_error_num < self.question_count:
            if self.right_answer[self.show_error_num] == True:
                self.show_error_num += 1
            else:
                break

        for btn in self.current_button:
            if btn['text'] in self.test[self.show_error_num]['correct_answers']:
                btn.config(bg='green', fg='black')
            if btn['text'] == self.answer[self.show_error_num]:
                btn.config(bg='red', fg='black')

        self.create_show_error_button()

    def create_show_error_button(self):
        if self.show_error_num > 0:
            self.back_button = tk.Button(self.error_window, text="К предыдущему вопросу", command=lambda: self.error_show_command(0))
            self.back_button.pack(padx=10, side="left")
            self.current_button.append(self.back_button)

        if self.show_error_num < self.question_count - 1:
            self.forward_button = tk.Button(self.error_window, text="К следующему вопросу", command=lambda: self.error_show_command(1))
            self.forward_button.pack(padx=10, side="right")
            self.current_button.append(self.forward_button)

    def error_show_command(self, action):
        if action == 0:
            # Переход к предыдущему вопросу с ошибкой
            self.show_error_num -= 1
            while self.show_error_num >= 0 and self.right_answer[self.show_error_num] == True:
                self.show_error_num -= 1
        elif action == 1:
            # Переход к следующему вопросу с ошибкой
            self.show_error_num += 1
            while self.show_error_num < self.question_count and self.right_answer[self.show_error_num] == True:
                self.show_error_num += 1
        
        self.delete_question()
        self.error_cycle()


    def create_question_text(self, window, question):
        self.question_text_label = tk.Label(window, text=self.test[question]['question'], font=self.question_font, wraplength=600)
        self.question_text_label.pack(pady=10)

        self.number_label = tk.Label(window, text=f"{question + 1}/{self.question_count}")
        self.number_label.pack(side="bottom", anchor="se")
        
    def create_question_button(self, window, question, prev):
        self.current_button = []
        for var in self.test[question]['all_answers']:
            button = tk.Button(window, text=var, font=self.button_font, wraplength=600)
            button.config(command=lambda v=var, b=button: self.check_answer(v, b))
            button.pack(side='top', fill='x', padx=(10, 0), pady=5, anchor='w')
            self.current_button.append(button)
        
        if prev:
            reset_button = tk.Button(window, text="Перезапустить тестирование", command=self.restart_test)
            reset_button.pack(side="bottom", anchor="sw")
            self.current_button.append(reset_button)
            
            if question > 0:
                prev_button = tk.Button(window, text="Предыдущий вопрос", command=self.prev_question)
                prev_button.pack(side="bottom", anchor="sw", pady=40)
                self.current_button.append(prev_button)

    def check_answer(self, variant, button):
        if variant in self.test[self.num_question]['correct_answers']:
            if self.checkbox_show_correct_answer_var.get():
                button.config(bg='green', fg='black')
            else:
                button.config(bg='black', fg='white')
            self.right_answer.append(True)
        else:
            if self.checkbox_show_correct_answer_var.get():
                button.config(bg='red', fg='black')
                for btn in self.current_button:
                    if btn['text'] in self.test[self.num_question]['correct_answers']:
                        btn.config(bg='green', fg='black')
            else:
                button.config(bg='black', fg='white')
            self.right_answer.append(False)
        self.answer.append(variant)

        for btn in self.current_button:
            btn.config(command=lambda: None)

        self.num_question += 1
        self.root.after(1000, self.next_question)

    def next_question(self):
        self.delete_question()
        self.main_cycle()

    def prev_question(self):
        self.delete_question()
        self.num_question -= 1
        self.right_answer.pop()
        self.answer.pop()
        self.main_cycle()

    def delete_question(self):
        self.question_text_label.destroy()
        self.number_label.destroy()
        for widget in self.current_button:
            widget.destroy()

    def restart_test(self):
        self.delete_question()
        self.start_window()

if __name__ == "__main__":
    App = UI()
    App.start_window()
    App.root.mainloop()