import customtkinter as ctk
import sqlite3 as sql
from functools import partial
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def get_base_path(filename):
    app_data_dir = os.path.join(os.environ['APPDATA'], 'MyPasswordManager')

    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)

    return os.path.join(app_data_dir, filename)


class PasswordManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Passwords manager")

        self.window_width = 500
        self.window_height = 620
        self.center_window()
        self.resizable(False, False)

        # database
        self.db = sql.connect(get_base_path('passwords.db'))
        self.c = self.db.cursor()
        self.c.execute("""
                   CREATE TABLE IF NOT EXISTS passwords (
                       id INTEGER PRIMARY KEY,
                       site TEXT NOT NULL,
                       login TEXT,
                       password TEXT NOT NULL
                   )
               """)
        self.db.commit()

        self.add_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.setup_add_screen()
        self.setup_list_screen()

        self.add_frame.pack(fill="both", expand=True)

        #before closing
        self.protocol('WM_DELETE_WINDOW', self.on_closing)


    def setup_add_screen(self):
        self.add_screen_label = ctk.CTkLabel(self.add_frame, text='Adding a new password',
                                             font=("Roboto", 22, "bold"),text_color=("#3a3a3a", "#eeeee0"))
        self.add_screen_label.pack(pady=(40, 30))

        #input fields
        self.service_name_input = self.create_input_field(self.add_frame, 'Service name:')
        self.login_input = self.create_input_field(self.add_frame, 'Login:')
        self.password_input = self.create_input_field(self.add_frame, 'Password:', show='*')

        self.show_pass_check = ctk.CTkCheckBox(
            self.add_frame,
            text="Show password",
            command=self.toggle_password,
            checkbox_width=18,
            checkbox_height=18,
            font=("Arial", 11),
            width=300
        )
        self.show_pass_check.pack(pady=(0, 5), anchor ='w', padx=100)

        #buttons
        self.add_button = self.create_button(self.add_frame, button_text='Add new password', button_command=self.save_data)
        self.goto_list_button = self.create_button(self.add_frame, button_text='Check my passwords',
                                                   button_command=self.show_list_screen, top_margin=10)

        self.notification_label = ctk.CTkLabel(
            self,
            text="",
            fg_color="#2d8a4e",
            text_color="white",
            corner_radius=10,
            height=30,
            font=("Arial", 12, "bold")
        )

    def setup_list_screen(self):
        self.list_label = ctk.CTkLabel(self.list_frame, text='Your passwords:',
                                       font=("Roboto", 22, "bold"), text_color=("#3a3a3a", "#eeeee0"))
        self.list_label.pack(pady=(40, 15))

        self.scroll_frame = ctk.CTkScrollableFrame(self.list_frame, width=440, height=400)
        self.scroll_frame.pack(pady=20)

        self.goto_add_button = self.create_button(self.list_frame, button_text='Add new password',
                                                  button_command=self.show_add_screen, down_margin=15, top_margin=18)

    def show_list_screen(self):
        self.add_frame.pack_forget()  # Прячем экран добавления
        self.list_frame.pack(fill="both", expand=True)  # Показываем список

        self.c.execute("SELECT id, site, login, password FROM passwords")
        data = self.c.fetchall()

        for id, sname, log, passw in data:
            self.create_entry_on_list(id, sname, log)


    def show_add_screen(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.list_frame.pack_forget()  # Прячем список
        self.add_frame.pack(fill="both", expand=True)


    def center_window(self):
        self.update_idletasks()

        scaling = self._get_window_scaling()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_center = int(((screen_width / 2) - (self.window_width / 2)) * scaling)
        y_center = int(((screen_height / 2) - (self.window_height / 2)) * scaling)

        self.geometry(f'{self.window_width}x{self.window_height}+{x_center}+{y_center}')


    @staticmethod
    def create_input_field(master, label_text, placeholder = '', show=''):
        label = ctk.CTkLabel(master, text=label_text, font=("Arial", 12), text_color="gray", width=300, anchor='w')
        label.pack(pady=(10, 0))

        entry = ctk.CTkEntry(master, placeholder_text=placeholder, width=300, height=40, show=show)
        entry.pack(pady=(0, 15))

        return entry

    @staticmethod
    def create_button(master, button_text, button_command, top_margin = 35, down_margin = 20):
        button = ctk.CTkButton(
            master,
            text=button_text,
            command=button_command,
            font=("Roboto", 16, "bold"),
            height=45,
            width=300,
            corner_radius=10,  # Слегка закругленные углы
            fg_color="#1f6aa5",  # Основной цвет
            hover_color="#144870",  # Цвет при наведении (чуть темнее)
            border_width=2,  # Тонкая рамка
            border_color="#242424"
        )
        button.pack(pady=(top_margin,down_margin))

        return button

    def create_entry_on_list(self, id, service_name, login):
        item_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#2b2b2b", corner_radius=10)
        item_frame.pack(fill="x", padx=10, pady=5)

        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", padx=15, pady=10)

        name_label = ctk.CTkLabel(info_frame, text=service_name, font=("Arial", 14, "bold"))
        name_label.pack(anchor="w")

        login_label = ctk.CTkLabel(info_frame, text=login, font=("Arial", 11), text_color="gray")
        login_label.pack(anchor="w")

        delete_btn = ctk.CTkButton(
            item_frame,
            text="🗑",
            width=40,
            height=40,
            fg_color="#3d3d3d",
            hover_color="#c0392b",
            command=partial(self.delete_entry, id, item_frame)
        )
        delete_btn.pack(side="right", padx=15)

        copy_btn = ctk.CTkButton(
            item_frame,
            text="📋",
            width=40,
            height=40,
            fg_color="#3d3d3d",
            command=partial(self.copy_password, id)
        )
        copy_btn.pack(side="right", padx=5)

    def toggle_password(self):
        if self.show_pass_check.get() == 1:
            self.password_input.configure(show='')
        else:
            self.password_input.configure(show='*')


    def save_data(self):
        service = self.service_name_input.get()
        login = self.login_input.get()
        password = self.password_input.get()

        if service and password:
            self.c.execute("""INSERT INTO passwords (site, login, password)
                              VALUES (?, ?, ?)
            """, (service, login, password))
            self.db.commit()

        self.service_name_input.delete(0, 'end')
        self.login_input.delete(0, 'end')
        self.password_input.delete(0, 'end')

    def delete_entry(self, del_id, frame):
        self.c.execute('DELETE FROM passwords WHERE id = ?', (del_id, ))
        self.db.commit()

        frame.destroy()

    def copy_password(self, copy_id):
        self.clipboard_clear()
        self.c.execute('SELECT password FROM passwords WHERE id = ?', (copy_id, ))
        self.clipboard_append(self.c.fetchone())
        self.update()

        self.show_toast('Password coppied!')

    def show_toast(self, message):
        self.notification_label.configure(text=message)

        self.notification_label.place(relx=0.5, rely=0.85, anchor="center")

        self.after(2000, self.notification_label.place_forget)

    def on_closing(self):
        self.db.close()
        self.destroy()



if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()
