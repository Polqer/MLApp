import DB_create
import customtkinter as ct
import sqlite3 as sql3
import Login
from Model import path_to_file
from tkinter import filedialog
from PIL import Image
import os
import shutil
import datetime

ct.set_appearance_mode("dark")
class MyFrame(ct.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.label_num = 0
        self.button_num = 0
        self.entry_num = 0
        self.pack(pady=20, padx=60)

    def add_entry(self, text):
        new_entry = ct.CTkEntry(master=self, placeholder_text=text, font=("Roboto", 24))
        setattr(self, f'self.label_{self.entry_num}', new_entry)
        self.entry_num += 1
        return new_entry

    def add_label(self, text):
        new_label=ct.CTkLabel(master=self, text=text, font=("Roboto", 24))
        setattr(self, f'self.label_{self.label_num}', new_label)
        self.label_num +=1
        return  new_label

    def add_button(self, command, text):
        new_button = ct.CTkButton(master=self, text=text, command= command, font=("Roboto", 24))
        setattr(self, f'self.button_{self.button_num}', new_button)
        self.button_num += 1
        return new_button

class FramePhotos(ct.CTkScrollableFrame):
    def __init__(self, id, appmain, master, **kwargs):
        super().__init__(master, **kwargs)
        self.appmain = appmain
        self.patient_id = id
        self.pack(pady=20, padx=60, fill="both", expand=True)

        self._create_headers()

        for i in range(4):
            self.grid_columnconfigure(i, weight=1)

    def _create_headers(self):
        headers = ["Название", "Результат анализа", "Вероятность", "Дата"]
        for col, header in enumerate(headers):
            ct.CTkLabel(self, text=header, font=("Arial", 14, "bold")).grid(row=0, column=col, padx=10, pady=10,
                                                                            sticky="ew")


    def add_row_photo(self, name, resultML, percent, date, path_photo):
        row = len(self.winfo_children()) // 4 + 1

        self.new_label_name = ct.CTkLabel(master=self, text=name)
        self.new_label_name.grid(row=row, column=0, padx=5, pady=10, sticky="ew")

        result_text = "Злокачественная" if resultML else "Доброкачественная"
        self.new_label_resultML = ct.CTkLabel(master=self, text=f"{result_text} опухоль",
                                              text_color="red" if resultML else "green")
        self.new_label_resultML.grid(row=row, column=1, padx=5, pady=10, sticky="ew")

        self.new_label_percent = ct.CTkLabel(master=self, text=percent)
        self.new_label_percent.grid(row=row, column=2, padx=5, pady=10, sticky="ew")

        self.new_label_date = ct.CTkLabel(master=self, text=date)
        self.new_label_date.grid(row=row, column=3, padx=5, pady=10, sticky="ew")

        self.button_photo = ct.CTkButton(master = self, command=lambda: self.show_photo(path_photo), text="Открыть фото")
        self.button_photo.grid(row=row, column=4, padx=5, pady=10, sticky="ew")

    def show_photo(self, path_photo):
        with Image.open(path_photo) as im:
            im.show()


    def form_photo(self, patient_id):
        self.appmain.withdraw()
        self.photo = ct.CTkToplevel(self)
        self.frame_photo = MyFrame(self.photo)
        label = self.frame_photo.add_label(f'Название:')
        label.grid(row=1, column=0, padx=5, pady=10, sticky="w")
        entry = self.frame_photo.add_entry(f'Название')
        entry.grid(row=1, column=1, padx=5, pady=10, sticky="e")
        label = self.frame_photo.add_label(f'Выбрать mat файл:')
        label.grid(row=2, column=0, padx=5, pady=10, sticky="w")
        button = self.frame_photo.add_button(lambda :self.upload_file(),"Выбрать файл")
        button.grid(row=2, column=1, padx=5, pady=10, sticky="e")

        self.button = ct.CTkButton(self.frame_photo, text='Сохранить', command=lambda: self.send_to_ML(self.file_path, entry.get()))
        self.button.grid(row=7, column=1,padx=5, pady=10, sticky="w")

    @staticmethod
    def save_research(lst_strings):
        connection = sql3.connect('my_DB.db')
        cur = connection.cursor()

        lst=['path_mat', 'path_array', 'name', 'resultML', 'percent', 'date', 'patient_id']
        print((', '.join(lst_strings)))
        cur.execute(f'''
                           INSERT INTO Photos ({', '.join(lst)})
                           VALUES (?, ?, ?, ?, ? ,?, ?)
                           ''', tuple(lst_strings)
                    )
        connection.commit()
        connection.close()

    def send_to_ML(self, path, name):
        path_photo, prediction, probability = path_to_file(path)
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        lst=[path, path_photo, name, str(prediction), str(round(probability, 2))+'%', str(timestamp), str(self.patient_id)]
        self.save_research(lst)
        self.appmain.update_table(self.patient_id)
        self.appmain.deiconify()
        self.destroy()


    def upload_file(self):
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл исследования",
                filetypes=[("Mat файл", "*.mat")],
                initialdir=os.path.expanduser("~")
            )

            if not file_path:
                return None
            os.makedirs('Mat_files', exist_ok=True)

            filename = os.path.basename(file_path)
            dest_path = os.path.join('Mat_files', filename)

            if os.path.exists(dest_path):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join('Mat_files', f"{name}_{timestamp}{ext}")
            shutil.copy(file_path, dest_path)
            self.file_path = dest_path
        except:
            pass

class FramePatients(ct.CTkScrollableFrame):
    def __init__(self, appmain, master, **kwargs):
        super().__init__(master=master)
        self.pack(pady=20, padx=60, fill="both", expand=True)
        self.appmain = appmain
        self.master = master

    def create_patient(self, entry_lst):
        connection = sql3.connect('my_DB.db')
        cur = connection.cursor()
        lst = ['firstname', 'secondname', 'middlename', 'birthday', 'passport', 'polis', 'doctor_id']
        lst_strings = []
        for i in range(len(lst)-1):
            if entry_lst[i].get() != '':
                lst_strings.append(f'{entry_lst[i].get()}')
        lst_strings.append(f'{Login.app.id}')
        cur.execute(f'''
                   INSERT INTO Patients ({', '.join(lst)})
                   VALUES (?, ?, ?, ?, ? ,?, ?)
                   ''', tuple(lst_strings)
                    )
        connection.commit()
        connection.close()

        self.appmain.deiconify()
        self.master.update_table()
        self.destroy()

    def redact_patient(self, id, entry_lst):
        connection = sql3.connect('my_DB.db')
        cur = connection.cursor()
        lst = ['firstname', 'secondname', 'middlename', 'birthday', 'passport', 'polis']
        lst_strings =[]
        for i in range(len(lst)):
            if entry_lst[i].get() != '' :
                lst_strings.append(f'{lst[i]}=\'{entry_lst[i].get()}\'')
        cur.execute(f'''
                UPDATE Patients SET
                {(', '.join(lst_strings))}
                WHERE id ={id}
                '''
                          )
        connection.commit()
        connection.close()

        self.appmain.deiconify()
        self.master.update_table()
        self.destroy()

    def form_patient(self, id=None):
        self.appmain.withdraw()
        if id:
            res = self.appmain.request_patient_by_id(id)
        self.patient = ct.CTkToplevel(self)
        self.frame_patient = MyFrame(self.patient)
        entry_lst = []
        lst = ['id', 'Имя', 'Фамилия', 'Отчество', 'День рождения', 'Паспорт', 'Полис']
        for i in range(1, len(lst)):
            label = self.frame_patient.add_label(f'{lst[i]}:')
            label.grid(row=i, column=0, padx=5, pady=10, sticky="w")
            entry = self.frame_patient.add_entry(f' {res[0][i]}'if id else "")
            entry_lst.append(entry)
            entry.grid(row=i, column=1, padx=5, pady=10, sticky="e")

        if id:
            self.button = ct.CTkButton(self.frame_patient, text='Сохранить', command=lambda: self.redact_patient(id, entry_lst))
        else:
            self.button = ct.CTkButton(self.frame_patient, text='Сохранить', command=lambda: self.create_patient(entry_lst))
        self.button.grid(row=7, column=1,padx=5, pady=10, sticky="w")

    def add_row_patient(self, appmain, name, patient_id):
        self.new_frame = ct.CTkFrame(master=self)
        self.new_frame.pack(pady=5, padx=20, fill="both", expand=True)
        self.new_label = ct.CTkLabel(master=self.new_frame, text=name)
        self.new_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.new_button_redact = ct.CTkButton(master=self.new_frame, text='Редактировать',
                                              command=lambda: self.form_patient(patient_id))

        self.new_button_redact.grid(row=0, column=1, padx=5, pady=10)
        self.new_button_diagnosis = ct.CTkButton(master=self.new_frame, text='Список фотографий',
                                                 command=lambda: appmain.frame_photos(patient_id, name))

        self.new_button_diagnosis.grid(row=0, column=2, padx=5, pady=10)
        self.new_frame.grid_columnconfigure(0, weight=1, minsize=200, pad=10)

class AppMain(ct.CTk):
    def __init__(self):
        super().__init__()
        self.title("MLApp")
        self.geometry("800x500")
        self.change_flag = 'Pat'
        self.image_back = ct.CTkImage(dark_image=Image.open('Images/back.png'), size=(20, 20))
        self.scroll_frame = None
        self.frame_patients()

    def clear(self):
        try:
            self.frame_title.pack_forget()
        except:
            print("Не очистилось((")


    def frame_patients(self):
        self.clear()
        self.frame_title = ct.CTkFrame(master=self)
        self.frame_title.pack(pady=20, padx=60, fill="both")
        self.title_label = ct.CTkLabel(master=self.frame_title, text=f'Здравствуйте, {Login.app.firstname.capitalize()} '
                                                               f'{Login.app.secondname.capitalize()}'
                                                               f' {Login.app.middlename.capitalize() if
                                                               Login.app.middlename is not None else ""}!',
                                 font=("Roboto", 24))
        self.title_label.grid(row=0, column=0,pady=20, padx=60)

        self.create_table_of_patients()
        self.title_button = ct.CTkButton(master=self.frame_title, text='Добавить пациента',
                                                   command=lambda: self.scroll_frame.form_patient())
        self.title_button.grid(row=0, column=1,pady=20, padx=60)

    def frame_photos(self, patient_id, name):
        self.clear()
        self.frame_title = ct.CTkFrame(master=self)
        self.frame_title.pack(pady=20, padx=60, fill="both")

        self.back_button = self.title_button = ct.CTkButton(master=self.frame_title, image=self.image_back, text="",
                                   command=lambda: self.frame_patients(), width=20, height=20)
        self.back_button.grid(row=0, column=0, pady=10, padx=10)
        self.title_label = ct.CTkLabel(master=self.frame_title, text=f'Пациент, {name}!',
                                 font=("Roboto", 24))
        self.title_label.grid(row=0, column=1,pady=20, padx=60)

        self.create_table_of_photos(patient_id)
        self.title_button = ct.CTkButton(master=self.frame_title, text='Новое исследование',
                                   command=lambda: self.scroll_frame.form_photo(patient_id))
        self.title_button.grid(row=0, column=2,pady=20, padx=60)


    @staticmethod
    def request_all_patients():
        connection = sql3.connect('my_DB.db')
        cur = connection.cursor()

        res = cur.execute(f'''
        SELECT * FROM Patients
        WHERE doctor_id ={Login.app.id}
        '''
                          ).fetchall()
        connection.close()
        return res

    @staticmethod
    def request_patient_by_id(id):
        connection = sql3.connect('my_DB.db')
        cur = connection.cursor()

        res = cur.execute(f'''
                SELECT * FROM Patients
                WHERE id ={id}
                '''
                          ).fetchall()
        connection.close()
        return res

    @staticmethod
    def request_photos_by_patient_id(id):
        connection = sql3.connect('my_DB.db')
        cur = connection.cursor()

        res = cur.execute(f'''
                        SELECT * FROM Photos
                        WHERE patient_id ={id}
                        '''
                          ).fetchall()
        connection.close()
        return res

    def create_table_of_patients(self):
        if self.scroll_frame:
            self.scroll_frame.pack_forget()
        self.scroll_frame = FramePatients(self, self)
        list_of_patients = self.request_all_patients()
        for i in list_of_patients:
            self.scroll_frame.add_row_patient(self,f'{i[2]} {i[1]} {i[3] if i[3] is not None else ""}', i[0])

    def create_table_of_photos(self, patient_id):
        if self.scroll_frame:
            self.scroll_frame.pack_forget()
        self.scroll_frame = FramePhotos(patient_id, appmain=self, master=self)
        list_of_photos = self.request_photos_by_patient_id(patient_id)
        for i in list_of_photos:
            self.scroll_frame.add_row_photo(i[3], i[4], i[5], i[6], i[2])

    def update_table(self, patient_id=None):
        if isinstance(self.scroll_frame,FramePatients):
            self.create_table_of_patients()
        else:
            self.create_table_of_photos(patient_id)




if Login.app.username is not None:
    app = AppMain()
    app.mainloop()