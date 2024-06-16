import tkinter as tk
from tkinter import filedialog, messagebox
import os
import random
from tkinter import font
import docx

class QuizApp:
    def __init__(self):
        self.test = {}
        self.all_questions = []
        self.current_labels = []
        self.current_buttons = []
        self.selected_files = False
        self.current_question_index = 0
        self.selected_questions = []
        self.right_answers = 0
        self.num = 0
        self.correct_answers_list = []
        self.file_path = ""
        self.file_mod_time = 0
        self.custom_font = None
        self.custom_font_2 = None
        self.root = tk.Tk()
        self.root.geometry("800x600")
        self.warning_shown = False
        self.initialize_fonts()
        self.create_main_window(first_start=True)

    def process_file(self, cquest):
        if self.selected_files:
            self.change_file()
        else:
            filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select File", filetypes=(("Text files", "*.txt"), ("Word files", "*.docx"), ("All files", "*.*")))
            if not filename:
                return
            self.file_path = filename

            if os.path.getmtime(self.file_path) != self.file_mod_time:
                if self.warning_shown:
                    self.warning_shown = False

                if self.file_path.endswith('.docx'):
                    doc = docx.Document(self.file_path)
                    data = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                else:
                    with open(self.file_path, 'r', encoding="UTF-8") as file:
                        data = file.read()

                questions = []
                current_question = ""

                for line in data.splitlines():
                    if line.strip():
                        current_question += line + "\n"
                    else:
                        if current_question:
                            questions.append(current_question.strip())
                            current_question = ""

                if current_question:
                    questions.append(current_question.strip())

                self.test = {}
                question_number = 1
                for question_block in questions:
                    lines = question_block.split('\n')
                    if len(lines) > 0:
                        question = lines[0].strip()
                        variants = []
                        answer = None
                        for line in lines[1:]:
                            line = line.strip()
                            if line.startswith('+'):
                                answer = line[1:]
                                variants.append(line[1:])
                            elif line:
                                variants.append(line)

                        if answer:
                            self.test[f'ask{question_number}'] = {
                                'name': question,
                                'variants': variants,
                                'answer': answer
                            }
                            question_number += 1
                        elif not self.warning_shown:
                            self.warning_shown = True
                            messagebox.showwarning(title="Предупреждение!", message="Внимание, не на все вопросы имеются ответы\nВопросы, не имеющие ответа, будут пропущены\n\nДля того чтобы указать ответ, поставьте + в начале правильного варианта ответа")

                self.all_questions = list(self.test.keys())
                count_question = int(cquest) if cquest else len(self.all_questions)
                if count_question > len(self.all_questions) or count_question <= 0:
                    count_question = len(self.all_questions)

                self.selected_questions = random.sample(self.all_questions, count_question)
                self.correct_answers_list = [None] * count_question
                self.selected_files = True
                self.current_question_index = 0
                self.file_mod_time = os.path.getmtime(self.file_path)

                self.file_name = os.path.basename(self.file_path)
                self.choose_file_button.config(text=self.file_name)

    def change_file(self):
        self.file_path = ""
        self.file_mod_time = 0
        self.selected_files = False
        self.selected_questions.clear()
        self.correct_answers_list.clear()
        self.reset()
        self.process_file(self.count_entry.get())

    def entry_check(self, entry):
        try:
            int(entry.get())
            return True
        except ValueError:
            messagebox.showerror(title="Ошибка", message="Количество вопросов указано неверно")
            return False

    def start(self, entry):
        if self.entry_check(entry):
            if self.selected_files and len(self.selected_questions) > 0:
                if os.path.getmtime(self.file_path) != self.file_mod_time:
                    self.process_file(entry.get())

                self.num = int(entry.get()) if entry.get() and int(entry.get()) > 0 else len(self.selected_questions)
                if self.num > len(self.all_questions):
                    self.num = len(self.all_questions)

                self.selected_questions = random.sample(self.all_questions, self.num)
                self.correct_answers_list = [None] * self.num
                self.screen_destroy()
                self.current_question_index = 0
                self.screen_update()
            else:
                messagebox.showerror(title="Ошибка", message="Вы не выбрали файл, содержащий вопросы, либо вопросы внутри файла хранятся неправильно!")

    def screen_destroy(self):
        for widget in self.current_labels + self.current_buttons:
            widget.destroy()
        self.current_labels.clear()
        self.current_buttons.clear()
        try:
            self.choose_file_button.destroy()
            self.count_label.destroy()
            self.count_entry.destroy()
            self.test_start_button.destroy()
        except AttributeError:
            pass

    def on_button_click(self, variant, correct_answer, button):
        if self.correct_answers_list[self.current_question_index] is None:
            if variant == correct_answer:
                button.config(bg='green', fg='black')
                self.right_answers += 1
                self.correct_answers_list[self.current_question_index] = True
            else:
                button.config(bg='red', fg='black')
                self.correct_answers_list[self.current_question_index] = False
                for btn in self.current_buttons:
                    if btn['text'] == correct_answer:
                        btn.config(bg='green', fg='black')
        else:
            if self.correct_answers_list[self.current_question_index]:
                self.right_answers -= 1
            elif not self.correct_answers_list[self.current_question_index]:
                self.right_answers += 1

            if variant == correct_answer:
                button.config(bg='green', fg='black')
                self.correct_answers_list[self.current_question_index] = True
            else:
                button.config(bg='red', fg='black')
                for btn in self.current_buttons:
                    if btn['text'] == correct_answer:
                        btn.config(bg='green', fg='black')
                self.correct_answers_list[self.current_question_index] = False
        
        for btn in self.current_buttons:
            btn.config(command=lambda: None)

        self.root.after(1000, self.next_question)


    def next_question(self):
        self.current_question_index += 1
        if self.current_question_index < len(self.selected_questions):
            self.screen_update()
        else:
            percentage_correct = (self.right_answers / len(self.selected_questions)) * 100
            mark = 2 if percentage_correct < 40 else 3 if percentage_correct < 70 else 4 if percentage_correct < 90 else 5
            messagebox.showinfo("Тест завершен", f"Вы ответили правильно на {self.right_answers}/{len(self.selected_questions)}\nПроцент правильных ответов: {percentage_correct:.1f}%\nВаша оценка: {mark}")
            self.reset()

    def reset(self):
        self.screen_destroy()
        self.right_answers = 0
        self.create_main_window(first_start=False)

        self.choose_file_button.config(text=self.file_name)

    def prev_question(self):
        if self.current_question_index > 0:
            if self.correct_answers_list[self.current_question_index] is True:
                self.right_answers -= 1
            elif self.correct_answers_list[self.current_question_index] is False:
                self.right_answers += 1

            self.correct_answers_list[self.current_question_index] = None
            self.current_question_index -= 1
            self.screen_update()

    def screen_update(self):
        self.screen_destroy()
        if self.current_question_index < len(self.selected_questions):
            question_key = self.selected_questions[self.current_question_index]
            question_info = self.test[question_key]
            random.shuffle(question_info['variants'])

            question_label = tk.Label(self.root, text=question_info['name'], font=self.custom_font_2, wraplength=600)
            question_label.pack(pady=10)
            self.current_labels.append(question_label)

            for variant in question_info['variants']:
                button = tk.Button(self.root, text=variant, font=self.custom_font, wraplength=600)
                button.config(command=lambda v=variant, b=button: self.on_button_click(v, question_info['answer'], b))
                button.pack(side='top', fill='x', padx=(10, 0), pady=5, anchor='w')
                self.current_buttons.append(button)

            number_label = tk.Label(self.root, text=f"{self.current_question_index + 1}/{len(self.selected_questions)}")
            number_label.pack(side="bottom", anchor="se")
            self.current_labels.append(number_label)

            reset_button = tk.Button(self.root, text="Перезапустить тестирование", command=self.reset)
            reset_button.pack(side="bottom", anchor="sw")
            self.current_buttons.append(reset_button)

            if self.current_question_index > 0:
                prev_button = tk.Button(self.root, text="Предыдущий вопрос", command=self.prev_question)
                prev_button.pack(side="bottom", anchor="sw", pady=40)
                self.current_buttons.append(prev_button)

    def initialize_fonts(self):
        self.custom_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.custom_font_2 = font.Font(family="Helvetica", size=14, weight="bold")

    def create_main_window(self, first_start):
        self.choose_file_button = tk.Button(self.root, text="Выбрать файл", command=lambda: self.process_file(self.count_entry.get()))
        self.choose_file_button.pack(pady=10)

        self.count_label = tk.Label(self.root, text="Укажите количество вопросов для тестирования")
        self.count_label.pack(pady=10)

        self.count_entry = tk.Entry(self.root)
        self.count_entry.pack(pady=0)

        if not first_start:
            self.count_entry.insert(0, str(self.num))

        self.test_start_button = tk.Button(self.root, text="Начать тестирование", command=lambda: self.start(self.count_entry))
        self.test_start_button.pack(pady=20)

if __name__ == "__main__":
    app = QuizApp()
    app.root.mainloop()
