### Проверять файл при запуске теста
### Полная проверка, если в файл были внесены изменения /// Исправить количество вопросов в тесте, которое не изменяется, после первого прохождения
### Исправить ошибку с текстом за пределами кнопок
### Исправить проблему с окном, меняющим размер и положение
### Исправить подсчет правильных оценок в случае возврата к предыдущему вопросы (Сначала неправильный ответ, потом исправить)
### Если между вопросами стоят пробелы, то вопросы соединяются
### Галочки "Показывать одинаковые варианты ответов/вопросы"
### Поментка, если файл выбран

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import random
from tkinter import font
import docx

test = {}
all_questions = []
current_labels = []
current_buttons = []
selected_files = False
current_question_index = 0
selected_questions = []
right_answers = 0
num = 0
number_label = None
custom_font = None
correct_answers_list = []

def process_file(cquest):
    global test, all_questions, selected_files, selected_questions, current_question_index, correct_answers_list
    filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select File", filetypes=(("Text files", "*.txt"), ("Word files", "*.docx"), ("All files", "*.*")))
    status = True
    if filename:
        if filename.endswith('.docx'):
            doc = docx.Document(filename)
            data = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

            print(data)
        else:
            with open(filename, 'r', encoding="UTF-8") as file:
                data = file.read()

        questions = [block.strip() for block in data.strip().split('\n\n') if block.strip()]
        test = {}
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

                if answer is None:
                    if status:
                        messagebox.showwarning(title="Предупреждение!", message="Внимание, не на все вопросы имеются ответы\nВопросы, не имеющие ответа, будут пропущены\n\nДля того чтобы указать ответ, поставьте + в начале правильного варианта ответа")
                        status = False

                else:
                    test[f'ask{question_number}'] = {
                        'name': question,
                        'variants': variants,
                        'answer': answer
                    }
                    question_number += 1

        all_questions = list(test.keys())

        count_question = 0
        try:
            if cquest != "":
                count_question = int(cquest)
            else:
                count_question = len(all_questions)
                messagebox.showwarning(title="Предупреждение!", message="Вы не выбрали количество вопросов, в тесте будут отображаться все имеющиеся вопросы!")
        except ValueError:
            print('76')

        if count_question > len(all_questions) or count_question <= 0:
            count_question = len(all_questions)

        selected_questions = random.sample(all_questions, count_question)
        correct_answers_list = [None] * count_question
        selected_files = True
        current_question_index = 0

def entry_check(entry):
    number = entry.get()
    if number == "":
        return 1
    else:
        try:
            number = int(number)
            return 1
        except ValueError:
            messagebox.showerror(title="Ошибка", message="Количество вопросов указано неверно")
            return 0

def start(entry):
    global selected_files, selected_questions, current_question_index, num, correct_answers_list
    if entry_check(entry):
        if selected_files and len(selected_questions) > 0:
            if entry.get() == "" or int(entry.get()) == 0 or int(entry.get()) > len(selected_questions):
                num = len(selected_questions)
                number = num
            else:
                number = int(entry.get())
                num = int(entry.get())

            if number >= len(all_questions) or num <= 0:
                number = len(all_questions)

            selected_questions = random.sample(all_questions, num)
            correct_answers_list = [None] * num
            screen_destroy()
            current_question_index = 0
            screen_update()
        else:
            messagebox.showerror(title="Ошибка", message="Вы не выбрали файл, содержащий вопросы, либо вопросы внутри файла хранятся неправильно!")

def screen_destroy():
    global current_labels, current_buttons
    for widget in current_labels + current_buttons:
        widget.destroy()
    current_labels.clear()
    current_buttons.clear()

    choose_file_button.destroy()
    count_label.destroy()
    count_entry.destroy()
    test_start_button.destroy()
    try:
        number_label.destroy()
        reset_button.destroy()
    except AttributeError:
        pass
    except tk.TclError:
        pass

def on_button_click(variant, correct_answer, button):
    global right_answers, correct_answers_list, current_question_index
    if variant == correct_answer:
        button.config(bg='green', fg='black')
        if correct_answers_list[current_question_index] is None:
            right_answers += 1
        correct_answers_list[current_question_index] = True
    else:
        button.config(bg='red', fg='black')
        if correct_answers_list[current_question_index] is None:
            correct_answers_list[current_question_index] = False
        for btn in current_buttons:
            if btn['text'] == correct_answer:
                btn.config(bg='green', fg='black')
    for btn in current_buttons:
        btn.config(command=lambda: print())
    root.after(1000, next_question)

def next_question():
    global current_question_index
    current_question_index += 1
    if current_question_index < len(selected_questions):
        screen_update()
    else:
        percentage_correct = (right_answers / len(selected_questions)) * 100
        mark = 0
        if percentage_correct < 40:
            mark = 2
        elif percentage_correct < 70:
            mark = 3
        elif percentage_correct < 90:
            mark = 4
        elif percentage_correct <= 100:
            mark = 5
        messagebox.showinfo("Тест завершен", f"Вы ответили правильно на {right_answers}/{len(selected_questions)}\nПроцент правильных ответов: {percentage_correct:.1f}%\nВаша оценка: {mark}")
        reset()

def reset():
    root.destroy()
    restart()

def prev_question():
    global current_question_index, right_answers
    if current_question_index > 0:
        if correct_answers_list[current_question_index] is True:
            right_answers -= 1
        correct_answers_list[current_question_index] = None
        current_question_index -= 1
        screen_update()

def screen_update():
    global current_labels, current_buttons, reset_button, test, selected_questions, current_question_index, number_label

    screen_destroy()
    if current_question_index < len(selected_questions):
        question_key = selected_questions[current_question_index]
        question_info = test[question_key]
        random.shuffle(question_info['variants'])
        
        question_label = tk.Label(root, text=question_info['name'], font=custom_font_2, wraplength=600)
        question_label.pack(pady=10)
        current_labels.append(question_label)

        for variant in question_info['variants']:
            button = tk.Button(root, text=variant, font=custom_font)
            button.config(command=lambda v=variant, b=button: on_button_click(v, question_info['answer'], b))
            button.pack(side='top', fill='x', padx=(10, 0), pady=5, anchor='w')
            current_buttons.append(button)

        number_label = tk.Label(root, text=f"{current_question_index+1}/{len(selected_questions)}")
        number_label.pack(side="bottom", anchor="se")

        reset_button = tk.Button(root, text="Перезапустить тестирование", command=reset)
        reset_button.pack(side="bottom", anchor="sw")

        if current_question_index > 0:
            prev_button = tk.Button(root, text="Предыдущий вопрос", command=prev_question)
            prev_button.pack(side="bottom", anchor="sw",pady=40)
            current_buttons.append(prev_button)

def restart():
    global test, all_questions, current_labels, current_buttons, selected_files, current_question_index, selected_questions, right_answers, correct_answers_list
    current_labels = []
    current_buttons = []
    current_question_index = 0
    right_answers = 0
    correct_answers_list = []
    create_main_window(False)

def create_main_window(first_start):
    global root, choose_file_button, count_label, count_entry, test_start_button, custom_font, custom_font_2

    root = tk.Tk()
    root.geometry("800x600")

    choose_file_button = tk.Button(root, text="Выбрать файл", command=lambda: process_file(count_entry.get()))
    choose_file_button.pack(pady=10)

    count_label = tk.Label(root, text="Укажите количество вопросов для тестирования")
    count_label.pack(pady=10)

    count_entry = tk.Entry(root)
    count_entry.pack(pady=0)

    if not first_start:
        insert_num = str(num)
        count_entry.delete(0, tk.END)
        count_entry.insert(0, insert_num)

    test_start_button = tk.Button(root, text="Начать тестирование", command=lambda: start(count_entry))
    test_start_button.pack(pady=20)

    custom_font = font.Font(family="Helvetica", size=12, weight="bold")
    custom_font_2 = font.Font(family="Helvetica", size=14, weight="bold")

    root.mainloop()

create_main_window(True)
