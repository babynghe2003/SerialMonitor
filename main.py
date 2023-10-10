from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import serial as sr
import tkinter as tk
import serial.tools.list_ports
import customtkinter as ctk
from tkinter import messagebox
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from tkinter import filedialog
import matplotlib as mpl
import os.path
import matplotlib.backends.backend_pdf
import threading
import time
from random import randint
import datetime


class CustomNavigationToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.parent = parent
        self.patient_info = {
            'Họ Tên bệnh nhân': 'Nguyễn Văn A',
            'Ngày sinh': '01/01/1990',
            'Giới tính': 'Nam',
            'Địa chỉ': '123 Đường ABC, Quận XYZ',
            'Số bệnh phẩm': '12345',
            'Xét nghiệm gửi': 'Xét nghiệm máu',
            'Điện thoại': '0123 456 789',
            'Chẩn đoán': 'Chẩn đoán mẫu bình thường',
            'Chất lượng mẫu': 'Mẫu đạt chất lượng',
            'Bác sĩ chỉ định': 'Nguyễn Thị B',
            'Thời gian xét nghiệm': '01/10/2023 09:30 AM'
        }

    # Create a function to generate the first page with patient information
    def create_patient_info_page(self, patient_info):
        fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 page size in inches (portrait)
        ax.axis('off')  # Turn off axes

        # Create a title
        ax.text(0.5, 0.95, 'PHIẾU KẾT QUẢ XÉT NGHIỆM', fontsize=16, fontweight='bold', ha='center', va='center')

        # Split patient information into two columns
        column1_info = {}
        column2_info = {}
        info_items = list(patient_info.items())
        mid_index = len(info_items) // 2

        for i, (key, value) in enumerate(info_items):
            if i < mid_index:
                column1_info[key] = value
            else:
                column2_info[key] = value

        # Add patient information to the figure in two columns
        y_position = 0.85
        column_spacing = 0.4

        for key, value in column1_info.items():
            ax.text(0.0, y_position, f"{key}:", fontsize=12, fontweight='bold')
            ax.text(0.3, y_position, value, fontsize=12)
            y_position -= 0.05

        y_position = 0.85
        for key, value in column2_info.items():
            ax.text(0.6, y_position, f"{key}:", fontsize=12, fontweight='bold')
            ax.text(0.85, y_position, value, fontsize=12)
            y_position -= 0.05

        return fig

    def create_figure_from_data(self, data1, data2):

        fig1 = Figure(figsize=(8.27, 11.69))
        fig1.tight_layout()

        ax1 = fig1.add_subplot(211)
        ax1.set_title("BIỂU ĐỒ ÁP LỰC")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("mmHg")
        ax1.set_xlim(0, 100)
        ax1.set_ylim(0, 100)
        ax1.grid(linestyle='--')

        lines1 = ax1.plot(np.arange(0, len(data1) / 5, 0.2), data1, label="", linestyle='dashed')[0]
        lines2 = ax1.plot(np.arange(0, len(data2) / 5, 0.2), data2, label="Áp lực đường ruột")[0]

        ax1.legend()

        ax2 = fig1.add_subplot(212)
        ax2.set_title("BIỂU ĐỒ ÁP LỰC")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("mmHg")
        ax2.set_xlim(0, 100)
        ax2.set_ylim(0, 100)
        ax2.grid(linestyle='--')

        lines3 = ax2.plot(np.arange(0, len(data1) / 5, 0.2), data1, label="", linestyle='dashed')[0]
        lines4 = ax2.plot(np.arange(0, len(data2) / 5, 0.2), data2, label="Áp lực đường ruột")[0]

        ax2.legend()

        return fig1, ax1, ax2

    def save_figure(self, *args):
        filetypes = {'pdf': 'Portable Document Format'}
        print(filetypes)
        default_filetype = 'pdf'

        # Tk doesn't provide a way to choose a default filetype,
        # so we just have to put it first
        default_filetype_name = filetypes.pop(default_filetype)
        sorted_filetypes = ([(default_filetype, default_filetype_name)]
                            + sorted(filetypes.items()))
        tk_filetypes = [(name, '*.%s' % ext) for ext, name in sorted_filetypes]

        # adding a default extension seems to break the
        # asksaveasfilename dialog when you choose various save types
        # from the dropdown.  Passing in the empty string seems to
        # work - JDH!
        # defaultextension = self.canvas.get_default_filetype()
        defaultextension = 'pdf'
        initialdir = os.path.expanduser(mpl.rcParams['savefig.directory'])
        initialfile = 'figure.pdf'
        fname = tk.filedialog.asksaveasfilename(
            master=self.canvas.get_tk_widget().master,
            title='Save the figure',
            filetypes=tk_filetypes,
            defaultextension=defaultextension,
            initialdir=initialdir,
            initialfile=initialfile,
        )

        if fname in ["", ()]:
            return
        # Save dir for next time, unless empty str (i.e., use cwd).
        if initialdir != "":
            mpl.rcParams['savefig.directory'] = (
                os.path.dirname(str(fname)))

        pdf = matplotlib.backends.backend_pdf.PdfPages(fname)
        try:
            data1 = self.parent.parent.data
            data2 = self.parent.parent.data2
            leng = len(self.parent.parent.data)
            # line2 = self.parent.ax2
            range_x = self.parent.parent.range_x
            number_pages = leng / range_x
            print(range_x)
            print(leng)
            page_number = 0
            pdf.savefig(self.create_patient_info_page(self.parent.parent.patient_info))
            pgnum = 1
            fig1, ax1, ax2 = self.create_figure_from_data(data1, data2)
            while page_number <= leng / 5:
                ax1.set_xlim(page_number, page_number + range_x)
                page_number = page_number + range_x
                ax2.set_xlim(page_number, page_number + range_x)
                pdf.savefig(fig1)
                page_number = page_number + range_x
                pgnum+=1
            pdf.close()
        except Exception as e:
            tk.messagebox.showerror("Error saving file", str(e))


class ToolbarFrame(ctk.CTkFrame):
    def __init__(self, parent, options):
        super().__init__(parent, bg_color='#242a36')
        self.parent = parent

        self.start_button = ctk.CTkButton(self, text="RUN", font=('calbiri', 12, 'bold'),
                                          command=self.parent.plot_start)
        self.start_button.grid(row=0, column=0, padx=(20, 2), pady=20)

        self.reset_button = ctk.CTkButton(self, text="RESET", font=('calbiri', 12), command=self.parent.plot_reset)
        self.reset_button.grid(row=0, column=1, padx=(20, 2), pady=20)

        self.port_label = ctk.CTkLabel(self, text='Port ')
        self.port_label.grid(row=0, column=2, padx=(20, 2), pady=20)

        self.combobox_var = ctk.StringVar(value=options[0])
        self.combobox = ctk.CTkComboBox(self, values=options, command=self.parent.combobox_callback,
                                        variable=self.combobox_var)
        self.combobox_var.set(options[0])
        self.combobox.grid(row=0, column=3, padx=(2, 2), pady=20)

        self.range_label = ctk.CTkLabel(self, text='Số tín hiệu')
        self.range_label.grid(row=0, column=4, padx=(20, 2), pady=20)

        self.entry = ctk.CTkEntry(self, validate="key",
                                  validatecommand=((self.register(lambda text: text.isdigit()), '%P'), '%P'))
        self.entry.grid(row=0, column=5, padx=(2, 2), pady=20)
        self.entry.bind('<Return>', self.parent.range_callback)
        self.entry.bind('<FocusOut>', self.parent.range_callback)
        self.entry.insert(0, "Placeholder")
        self.about_button = ctk.CTkButton(self, text="About", command=self.parent.show_about, width=40)
        self.about_button.grid(row=0, column=6, padx=(20, 2), pady=20, sticky='e')

        self.about_button = ctk.CTkButton(self, text="Patient Info", command=self.parent.patient_info, width=40)
        self.about_button.grid(row=0, column=7, padx=(20, 2), pady=20, sticky='e')

    def update_options(self, options):
        self.combobox.configure(values=options)
        # self.combobox.update(options)


class FigureFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.fig1 = Figure()
        self.fig1.tight_layout()

        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.set_title("BIỂU ĐỒ ÁP LỰC")
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("mmHg")
        self.ax1.set_xlim(0, 100)
        self.ax1.set_ylim(0, 100)
        self.ax1.grid(linestyle='--')

        self.lines1 = self.ax1.plot([], [], label="", linestyle='dashed')[0]
        self.lines2 = self.ax1.plot([], [], label="Áp lực đường ruột")[0]

        self.ax1.legend()
        self.canvas = FigureCanvasTkAgg(self.fig1, master=self)
        self.canvas.get_tk_widget().pack(side=ctk.BOTTOM, fill=ctk.BOTH, expand=True)

        self.toolbar = CustomNavigationToolbar(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=ctk.BOTTOM, fill=ctk.BOTH, expand=True)

    def update_plots(self, data1, data2):
        len_data = len(data1) / 5
        if len_data < self.parent.range_x:
            len_data = self.parent.range_x
        self.lines1.set_xdata(np.arange(0, len(data1) / 5, 0.2))
        self.lines1.set_ydata(data1)
        self.ax1.set_xlim(len_data - self.parent.range_x, len_data)
        if len(data1) > 0 and len(data2) > 0:
            self.ax1.set_ylim(min(min(data1), min(data2)) - 10, max(max(data1), max(data2)) + 10)

        self.lines2.set_xdata(np.arange(0, len(data2) / 5, 0.2))
        self.lines2.set_ydata(data2)

        self.canvas.draw()


class SerialMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.serial = None
        self.title("Serial Monitor")
        self.configure(background='#242a36')
        self.geometry("950x800")
        # self.iconbitmap('logo.ico')
        self.ports = []
        self.options = ['null']
        self.choice = self.options[0]
        self.lock = threading.Lock()
        self.range_x = 100

        self.data = np.array([])
        self.data2 = np.array([])
        self.cond = False
        self.message = ""
        self.inputAllow = False
        self.toolbar_frame = ToolbarFrame(self, self.options)
        self.toolbar_frame.pack(side='top', fill='x')
        self.figure_frame = FigureFrame(self)
        self.figure_frame.pack(side='top', fill='both', expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.update_port_list_thread = threading.Thread(target=self.update_port_list, daemon=True)
        self.update_port_list_thread.start()
        self.patient_info = {
            'Họ Tên bệnh nhân': 'Nguyễn Văn A',
            'Năm sinh': '01/01/1990',
            'Giới tính': 'Nam',
            'Địa chỉ': '123 Đường ABC, Quận XYZ',
            'Số bệnh phẩm': '12345',
            'Xét nghiệm gửi': 'Xét nghiệm máu',
            'Điện thoại': '0123 456 789',
            'Chẩn đoán': 'Chẩn đoán mẫu bình thường',
            'Chất lượng mẫu': 'Mẫu đạt chất lượng',
            'Bác sĩ chỉ định': 'Nguyễn Thị B',
            'Thời gian xét nghiệm': datetime.datetime.now()
        }
        # self.update_port_list()
        # self.plot_data()

    def plot_data(self):
        while self.cond and self.serial is not None:
            try:
                print("getting")
                a = self.serial.read(1)
                if a.decode('utf-8') == '*':
                    self.inputAllow = True
                if self.inputAllow:
                    self.message = self.message + a.decode('utf-8')
                if a.decode('utf-8') == '#':
                    if len(self.message) == 8:
                        print(self.message)
                        self.data = np.append(self.data, float(self.message[1:4]))
                        self.data2 = np.append(self.data2, float(self.message[4:7]))
                        self.figure_frame.update_plots(self.data, self.data2)
                    self.message = ""
                    self.inputAllow = False
                print("getting succed")
            except sr.SerialTimeoutException as e:
                messagebox.showwarning("Timeout", "Serial read timeout!")
                self.stop_plot()
                break
            except Exception as e:
                print(e)
                self.serial.close()
                self.stop_plot()
                break
        print("End getting")
        self.stop_plot()

    def plot_data_demo(self):
        while self.cond:
            try:
                self.data = np.append(self.data, randint(0, 100))
                self.data2 = np.append(self.data2, randint(0, 100))
                self.figure_frame.update_plots(self.data, self.data2)
            except sr.SerialTimeoutException as e:
                messagebox.showwarning("Timeout", "Serial read timeout!")
                self.stop_plot()
                break
            except Exception as e:
                print(e)
                self.serial.close()
                self.stop_plot()
                break
            time.sleep(0.2)
        print("End getting")
        self.stop_plot()

    def start_plot_data_thread(self):
        with self.lock:
            plot_data_thread = threading.Thread(target=self.plot_data)
            plot_data_thread.daemon = True
            plot_data_thread.start()

    def show_about(self):
        # Define the information to be displayed
        company = "My Company"
        team = "My Team"
        version = "1.0"
        app_name = "My App"

        # Create a custom message box
        about_window = tk.Toplevel(self)
        about_window.title("About")

        # Add the resized logo image to the custom message box
        # logo_photo = ImageTk.PhotoImage(resized_image)
        logo_label = tk.Label(about_window)
        logo_label.grid(row=0, column=0, padx=30, pady=30, sticky="w")

        # Add the about information to the custom message box
        about_info = f"Company: {company}\nTeam: {team}\nVersion: {version}\nApp Name: {app_name}"
        info_label = tk.Label(about_window, text=about_info)
        info_label.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        screen_width = about_window.winfo_screenwidth()
        screen_height = about_window.winfo_screenheight()
        x = int((screen_width - about_window.winfo_reqwidth()) / 2)
        y = int((screen_height - about_window.winfo_reqheight()) / 2)
        about_window.geometry(f"+{x}+{y}")

        # Show the custom message box
        about_window.focus_set()
        about_window.grab_set()
        about_window.transient(self)
        about_window.wait_window()

    def patient_info(self):
        def update_patient_info():
            self.patient_info = {
                'Họ Tên bệnh nhân': name_entry.get(),
                'Năm sinh': birth_year_entry.get(),
                'Giới tính': gender_var.get(),
                'Địa chỉ': address_entry.get(),
                'Số bệnh phẩm': '12345',
                'Xét nghiệm gửi': 'Xét nghiệm máu',
                'Điện thoại': birth_year_entry.get(),
                'Chẩn đoán': 'Chẩn đoán mẫu bình thường',
                'Chất lượng mẫu': 'Mẫu đạt chất lượng',
                'Bác sĩ chỉ định': 'Nguyễn Thị B',
                'Thời gian': datetime.datetime.now()
            }
            success_message = f"Form submitted successfully!"
            messagebox.showinfo("Success", success_message)
        patient_info_windows = ctk.CTkToplevel()
        patient_info_windows.title("Patient Information Form")

        # Create and place labels
        name_label = ctk.CTkLabel(patient_info_windows,font=('calbiri', 12), text="Tên:")
        name_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        birth_year_label = ctk.CTkLabel(patient_info_windows,font=('calbiri', 12), text="Năm sinh:")
        birth_year_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

        phone_number_label = ctk.CTkLabel(patient_info_windows,font=('calbiri', 12), text="Số điện thoại:")
        phone_number_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')

        address_label = ctk.CTkLabel(patient_info_windows,font=('calbiri', 12), text="Địa chỉ:")
        address_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')

        age_label = ctk.CTkLabel(patient_info_windows,font=('calbiri', 12), text="Tuổi:")
        age_label.grid(row=4, column=0, padx=10, pady=5, sticky='w')

        gender_label = ctk.CTkLabel(patient_info_windows,font=('calbiri', 12), text="Giới tính:")
        gender_label.grid(row=5, column=0, padx=10, pady=5, sticky='w')

        # Create and place entry fields
        name_entry = ctk.CTkEntry(patient_info_windows)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        birth_year_entry = ctk.CTkEntry(patient_info_windows)
        birth_year_entry.grid(row=1, column=1, padx=10, pady=5)

        phone_number_entry = ctk.CTkEntry(patient_info_windows)
        phone_number_entry.grid(row=2, column=1, padx=10, pady=5)

        address_entry = ctk.CTkEntry(patient_info_windows)
        address_entry.grid(row=3, column=1, padx=10, pady=5)

        # Create and place a radio button for gender
        gender_var = tk.StringVar()
        male_radio = ctk.CTkRadioButton(patient_info_windows, text="Nam", variable=gender_var, value="Nam")
        female_radio = ctk.CTkRadioButton(patient_info_windows, text="Nữ", variable=gender_var, value="Nữ")
        male_radio.grid(row=5, column=1, padx=10, pady=5)
        female_radio.grid(row=6, column=1, padx=10, pady=5)

        # Create and place a submit button
        submit_button = ctk.CTkButton(patient_info_windows, text="Submit", command=update_patient_info)
        submit_button.grid(row=7, column=1, padx=10, pady=10, sticky='e')

        patient_info_windows.focus_set()
        patient_info_windows.grab_set()
        patient_info_windows.transient(self)
        patient_info_windows.wait_window()

    def update_port_list(self):
        while True:
            print("update port list")
            old_options = self.options
            old_ports = self.ports
            self.ports = serial.tools.list_ports.comports()
            if len(old_ports) == len(self.ports):
                pass
            else:
                self.options = [port for port, _, _ in sorted(self.ports)]

                if len(old_options) == len(self.options):
                    pass
                else:
                    self.toolbar_frame.update_options(self.options)
            time.sleep(0.5)

    def combobox_callback(self, choice):
        self.choice = choice

    def stop_plot(self):
        self.message = ""
        self.cond = False
        if self.serial is not None:
            self.serial.close()
        self.toolbar_frame.start_button.configure(text="RUN", fg_color="#1F6AA5",
                                                  hover_color="#355982", text_color="#DCE4EE")

    def plot_start(self):
        self.message = ""
        if self.cond:
            self.cond = False
            if self.serial is not None:
                self.serial.close()
            self.toolbar_frame.start_button.configure(text="RUN", fg_color="#1F6AA5",
                                                      hover_color="#355982", text_color="#DCE4EE")
        else:
            print("starting")
            if self.serial is not None:
                self.serial.close()
            try:
                self.serial = sr.Serial(str(self.choice), 9600, timeout=10)

            except sr.SerialTimeoutException as e:
                self.cond = False
                messagebox.showerror(message="Connection Timeout!")
            except sr.SerialException as e:
                self.cond = False
                messagebox.showerror(message="Cannot connect to serial!")
                print(e)
            else:
                self.cond = True
                self.toolbar_frame.start_button.configure(text="STOP", fg_color="#E2294E",
                                                          hover_color="#AD1634", text_color="#29272A", )
                self.start_plot_data_thread()

    def plot_reset(self):
        self.data = []
        self.data2 = []
        self.figure_frame.update_plots(self.data, self.data2)

    def range_callback(self, event):
        self.focus()
        text = event.widget.get()
        self.range_x = int(text)
        self.figure_frame.update_plots(self.data, self.data2)
        print("Entered text:", text)

    def on_close(self):
        self.stop_plot()
        self.destroy()


if __name__ == "__main__":
    app = SerialMonitorApp()
    app.mainloop()
