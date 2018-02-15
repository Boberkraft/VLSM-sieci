from tkinter import *
from tkinter.ttk import *
# leń jestem
from vlsm import validate
from vlsm import calculate_subnets
from tkinter.filedialog import asksaveasfilename
from saving import generate_raport
import os
import sys

print(sys.prefix)


class App:
    button = None  # Button - przycisk zapisz
    error_label = None  # Label - wyświetla błędy
    ip_entry = None  # Entry - pole na adres ip i maskę
    subnets_text = None  # Text - Pole tekstowe na ilości hostów
    save_docx = None  # IntVar - Checkbox na zapis jako dokument Word
    # (NIC NIE ROBI HEHE)
    multiple_tests = None  # IntVar - Checkbox na wiele sprawdzianów

    def __init__(self, root):
        # konfiguracja czerwonego i zielonego tekstu
        Style().configure('good.TLabel', foreground='green')
        Style().configure('error.TLabel', foreground='red')
        Style().configure('comment.TLabel', foreground='grey')

        # --- główne kontenery
        mainframe = Frame(root)
        mainframe.pack(padx=10, pady=10)
        left = Frame(mainframe)
        right = Frame(mainframe)
        left.grid(row=0, column=0, padx=10, sticky=N + W)
        right.grid(row=0, column=1, sticky=N + W)

        # --- ip label
        self.ip_label = Label(left, text='Adres ip/maska:')
        self.ip_label.grid(row=0, column=0)
        # --- ip entry
        self.ip_entry = Entry(left)
        self.ip_entry.grid(row=1, column=0, pady=10)
        # --- checkbutton
        self.save_docx = IntVar()
        save_docx = Checkbutton(left, text='Zapisz w formacie Word', variable=self.save_docx)
        # haha zawsze zapisuje w formacie word! to tylko taka zmyła
        self.multiple_tests = IntVar()
        multiple_tests = Checkbutton(left, text='Wiele testów', variable=self.multiple_tests)

        # zaznaczenie checkboxów
        self.save_docx.set(1)
        self.multiple_tests.set(1)
        save_docx.grid(row=2, column=0, sticky=W)
        multiple_tests.grid(row=3, column=0, sticky=W)

        # --- button
        self.button = Button(left, text="Zapisz", command=self.save)
        self.button.grid(row=4, column=0, pady=10)

        # Prawy kontener
        subnets_label = Label(right, text='Wielkości podsieci:')
        subnets_comment_label = Label(right, text='(Każda podsieć w nowej linii)', style='comment.TLabel')
        subnets_frame = Frame(right)
        subnets_label.grid(row=0, column=0)
        subnets_comment_label.grid(row=2, column=0)
        subnets_frame.grid(row=1, column=0, pady=10)

        # --- scrollbar i Text hosty
        self.subnets_text = Text(subnets_frame, height=5, width=10, wrap=NONE)
        s = Scrollbar(subnets_frame)
        s.config(command=self.subnets_text.yview)
        self.subnets_text.config(yscrollcommand=s.set)
        self.subnets_text.pack(side=LEFT)
        s.pack(side=RIGHT, fill=Y)

        # --- error label
        self.error_label = Label(root, text='...')
        self.error_label.pack(pady=(0, 10))

        # rozpoczęcie autmatycznej walidacji
        root.after(1, self.cyclic_validate)

    def save(self):
        """
        Metoda służąca do zapisu.
        Wywoływana automatycznie co pół sekundy oraz przy próbie wciśnięcia ZAPISZ.
        W przypadku jakichkolwiek błędów blokuje możliwośc zapisu do czasu ich naprawienia .
        """
        # adres
        network = self.ip_entry.get()
        # podsieci
        needed_subnets = self.subnets_text.get("1.0", END)
        error, val = validate(network, needed_subnets)
        if error:
            # Błąd i tak zostanie wychwycony w automatycznej walidacji
            pass
        else:
            network, needed_subnets = val
            subnets = calculate_subnets(network, needed_subnets)
            directory = asksaveasfilename()  # miejsce zapisu w którym utworzy się folder
            head, name = os.path.split(directory)
            if directory:
                print(directory)
                full_page = True if self.multiple_tests.get() == 1 else False
                generate_raport(network, subnets, directory+'-odpowiedzi.docx', True, False)
                generate_raport(network, subnets, directory+'-sprawdzian.docx', False, full_page)
                os.startfile(head)

    def cyclic_validate(self):
        """
        Automatyczna walidacja.
        Wywołuje samą siebie co pół sekundy
        """
        # validate every 0.5 second
        try:
            network = self.ip_entry.get()
            needed_subnets = self.subnets_text.get("1.0", END)
            error, val = validate(network, needed_subnets)
            if error:
                self.button.configure(state='disabled')
                self.error_label.configure(text=val, style="error.TLabel")
            else:
                self.button.configure(state='normal')
                self.error_label.configure(text="Gotowe do zapisu!", style="good.TLabel")
        except Exception as ex:
            print(ex)
            self.error_label.configure(text=ex, style="error.TLabel")
        finally:
            root.after(500, self.cyclic_validate)


# wczytanie ścieżki do ikony
datafile = "ikona.ico"
if not hasattr(sys, "frozen"):  # not packed
    datafile = os.path.join(os.path.dirname(__file__), datafile)
else:
    datafile = os.path.join(sys.prefix, datafile)

if __name__ == '__main__':
    root = Tk()
    root.wm_title('Dzielacz sieci')
    root.iconbitmap(default=datafile)
    app = App(root)

    mainloop()
