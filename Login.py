import customtkinter as ct
import sqlite3 as sql3

ct.set_appearance_mode("dark")

class ToplevelWindowError(ct .CTkToplevel):
    def __init__(self,  *args, text='Неизвестная ошибка', **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

        self.label = ct.CTkLabel(self, text=text)
        self.label.pack(padx=20, pady=20)


class AppLogin(ct.CTk):
    def __init__(self):
        super().__init__()

        self.id=None
        self.toplevel_window=None
        self.username=None
        self.firstname=None
        self.secondname=None
        self.middlename=None

        self.title("MLApp")
        self.geometry("800x500")

        self.button_change = ct.CTkSegmentedButton(self, values=['Войти', 'Зарегистрироваться'],
                                                   command=self.change)

        self.button_change.pack(pady=20, padx=60, fill="both")

        self.frame_login = ct.CTkFrame(master=self)
        self.frame_login.pack(pady=20, padx=60, fill="both", expand=True)

        self.label = ct.CTkLabel(master=self.frame_login, text="Форма авторизации", font=("Roboto", 24))
        self.label.pack(pady=12, padx=10)

        self.entry_username_login = ct.CTkEntry(master=self.frame_login, placeholder_text="Имя пользователя")
        self.entry_username_login.pack(pady=8, padx=10)

        self.entry_password_login = ct.CTkEntry(master=self.frame_login, placeholder_text="Пароль", show="*")
        self.entry_password_login.pack(pady=8, padx=10)

        self.button_login = ct.CTkButton(master=self.frame_login, command=self.login, text='Войти')
        self.button_login.pack(pady=8, padx=10)

        self.frame_register = ct.CTkFrame(master=self, width=400, height=400)

        self.label = ct.CTkLabel(master=self.frame_register, text="Форма регистрации", font=("Roboto", 24))
        self.label.pack(pady=12, padx=10)

        self.entry_username_register = ct.CTkEntry(master=self.frame_register, placeholder_text="Имя пользователя")
        self.entry_username_register.pack(pady=8, padx=10)

        self.entry_password_register = ct.CTkEntry(master=self.frame_register, placeholder_text="Пароль", show="*")
        self.entry_password_register.pack(pady=8, padx=10)

        self.entry_firstname = ct.CTkEntry(master=self.frame_register, placeholder_text="Имя")
        self.entry_firstname.pack(pady=8, padx=10)

        self.entry_secondname = ct.CTkEntry(master=self.frame_register, placeholder_text="Фамилия")
        self.entry_secondname.pack(pady=8, padx=10)

        self.entry_middlename = ct.CTkEntry(master=self.frame_register, placeholder_text="Отчество")
        self.entry_middlename.pack(pady=8, padx=10)

        self.entry_position = ct.CTkEntry(master=self.frame_register, placeholder_text="Должность")
        self.entry_position.pack(pady=8, padx=10)

        self.button_register = ct.CTkButton(master=self.frame_register, command=self.register, text='Зарегистрироваться')
        self.button_register.pack(pady=8, padx=10)


    def login(self):
        self.username = self.entry_username_login.get().replace(' ', '')
        self.password = self.entry_password_login.get()

        connection = sql3.connect('my_DB.db')
        cursor = connection.cursor()

        res = cursor.execute(f'''
        SELECT username, password FROM Users
        WHERE username='{self.username}'
        ''')

        if (self.username, self.password) in res.fetchall():
            res = cursor.execute(f'''
                    SELECT * FROM Users
                    WHERE username='{self.username}'
                    ''')
            column = ['id','username', 'password','position','firstname','secondname','middlename']
            info = res.fetchall()[0]
            [setattr(self, f'{column[i]}', info[i]) for i in range(len(info))]
            self.destroy()
        else:
            self.toplevel_window = ToplevelWindowError(self, text='Ошибка авторизации')

        connection.close()


    def register(self):
        connection = sql3.connect('my_DB.db')
        cursor = connection.cursor()

        try:
            cursor.execute(f'''
            INSERT INTO Users
            VALUES(
            NULL, 
            '{self.entry_username_register.get().replace(' ', '')}',
            '{self.entry_password_register.get()}',
            '{self.entry_position.get()}',
            '{self.entry_firstname.get()}',
            '{self.entry_secondname.get()}',
            '{self.entry_middlename.get()}'
            )
            ''')
        except:
            self.toplevel_window = ToplevelWindowError(self, text='Пользователь с таким именем пользователя уже существует!')

        self.entry_username_register.delete(0, 'end')
        self.entry_password_register.delete(0, 'end')
        self.entry_position.delete(0, 'end')
        self.entry_firstname.delete(0, 'end')
        self.entry_secondname.delete(0, 'end')
        self.entry_middlename.delete(0, 'end')

        self.toplevel_window = ToplevelWindowError(self, text='Регистрация прошла успешно!')
        self.toplevel_window.focus()

        connection.commit()
        connection.close()

    def change(self, value):
        if value == 'Войти':
            self.frame_register.pack_forget()
            self.frame_login.pack(pady=20, padx=60, fill="both", expand=True)
        elif value == 'Зарегистрироваться':
            self.frame_login.pack_forget()
            self.frame_register.pack(pady=20, padx=60, fill="both", expand=True)





app = AppLogin()
app.mainloop()

