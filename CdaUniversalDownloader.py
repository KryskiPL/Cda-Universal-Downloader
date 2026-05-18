__author__ = "KryskiPL"
__version__ = "1.0.0"
__license__ = "GNU GPL v3.0"

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import TkinterDnD, DND_TEXT
import yt_dlp
import threading
import queue
import time
from pathlib import Path

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def pobierz_katalog_roboczy():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

kolejka_zadan = queue.Queue()
aktywne_pobierania = 0
w_kolejce = 0

lock = threading.RLock() 
statusy_pobierania = {} 

def wklej_link():
    try:
        zawartosc = okno.clipboard_get()
        pole_linkow.insert(tk.END, zawartosc.strip() + ", ")
    except tk.TclError:
        pass

def obsluga_drop(event):
    wrzucony_tekst = event.data
    if wrzucony_tekst:
        wrzucony_tekst = wrzucony_tekst.strip('{}')
        pole_linkow.insert(tk.END, wrzucony_tekst.strip() + ", ")

def wybierz_folder():
    folder = filedialog.askdirectory(initialdir=sciezka_zapisu.get(), title="Wybierz folder pobierania")
    if folder:
        sciezka_zapisu.set(folder)

def pokaz_komunikat(tytul, naglowek, tresc, typ="info"):
    ciemny = var_ciemny.get()
    bg_kolor = "#1e1e1e" if ciemny else "#f0f0f0"
    fg_kolor = "#ffffff" if ciemny else "#000000"
    input_bg = "#2b2b2b" if ciemny else "#ffffff"
    btn_bg = "#333333" if ciemny else "#e0e0e0"

    okno_komunikatu = tk.Toplevel(okno)
    okno_komunikatu.title(tytul)
    okno_komunikatu.geometry("450x230")
    okno_komunikatu.configure(bg=bg_kolor)
    okno_komunikatu.resizable(False, False)
    okno_komunikatu.grab_set()

    kolor_naglowka = fg_kolor
    if typ == "blad": kolor_naglowka = "#ff4d4d"
    elif typ == "ostrzezenie": kolor_naglowka = "#ffb84d"

    tk.Label(okno_komunikatu, text=naglowek, font=("Arial", 11, "bold"), bg=bg_kolor, fg=kolor_naglowka).pack(pady=(15, 5))

    txt_tresc = tk.Text(okno_komunikatu, height=5, width=50, font=("Arial", 10), bg=input_bg, fg=fg_kolor, relief="flat", wrap="word")
    txt_tresc.insert(tk.END, tresc)
    txt_tresc.configure(state=tk.DISABLED)
    txt_tresc.pack(pady=10, padx=15)

    btn_zamknij = tk.Button(okno_komunikatu, text="Rozumiem", font=("Arial", 10, "bold"), bg=btn_bg, fg=fg_kolor, activebackground="#444444", activeforeground=fg_kolor, relief="flat", command=okno_komunikatu.destroy, padx=15)
    btn_zamknij.pack(pady=(5, 15))

def otworz_folder():
    katalog = sciezka_zapisu.get()
    if os.path.exists(katalog):
        os.startfile(katalog)
    else:
        pokaz_komunikat("Błąd", "❌ Nie znaleziono folderu", "Wybrany folder nie istnieje na tym komputerze!", typ="blad")

def przelacz_zawsze_na_wierzchu():
    czy_na_wierzchu = var_wierzch.get()
    okno.attributes('-topmost', czy_na_wierzchu)

def przelacz_tryb_ciemny():
    ciemny = var_ciemny.get()
    
    bg_kolor = "#121212" if ciemny else "#f0f0f0"       
    ramka_bg = "#1e1e1e" if ciemny else "#f0f0f0"       
    fg_kolor = "#ffffff" if ciemny else "#000000"       
    input_bg = "#2b2b2b" if ciemny else "#ffffff"       
    btn_bg = "#333333" if ciemny else "#e0e0e0"         
    
    def zmien_kolory_elementu(element):
        typ = element.winfo_class()
        try:
            if typ in ("Label", "Frame", "Checkbutton", "Labelframe"):
                if element == okno or typ == "Frame" and element.master == okno:
                    element.configure(bg=bg_kolor)
                else:
                    element.configure(bg=ramka_bg)
                
                if typ != "Frame":
                    element.configure(fg=fg_kolor)
                if typ == "Checkbutton":
                    element.configure(selectcolor=input_bg, activebackground=ramka_bg, activeforeground=fg_kolor)
                    
            elif typ in ("Text", "Entry"):
                element.configure(bg=input_bg, fg=fg_kolor, insertbackground=fg_kolor)
                if typ == "Entry":
                    element.configure(readonlybackground=input_bg)
            elif typ == "Button":
                if element != przycisk_pobierz:
                    element.configure(bg=btn_bg, fg=fg_kolor, activebackground="#444444", activeforeground=fg_kolor)
        except tk.TclError:
            pass
            
        for dziecko in element.winfo_children():
            zmien_kolory_elementu(dziecko)

    okno.configure(bg=bg_kolor)
    zmien_kolory_elementu(okno)
    
    if ciemny:
        style.configure("TCombobox", fieldbackground=input_bg, background=btn_bg, foreground=fg_kolor, arrowcolor=fg_kolor)
        style.map('TCombobox',
                  fieldbackground=[('readonly', input_bg)], selectbackground=[('readonly', input_bg)],
                  selectforeground=[('readonly', fg_kolor)], foreground=[('readonly', fg_kolor)])
        okno.option_add('*TCombobox*Listbox.background', input_bg)
        okno.option_add('*TCombobox*Listbox.foreground', fg_kolor)
        okno.option_add('*TCombobox*Listbox.selectBackground', btn_bg)
    else:
        style.configure("TCombobox", fieldbackground="#ffffff", background="#e0e0e0", foreground="#000000", arrowcolor="#000000")
        style.map('TCombobox',
                  fieldbackground=[('readonly', '#ffffff')], selectbackground=[('readonly', '#ffffff')],
                  selectforeground=[('readonly', '#000000')], foreground=[('readonly', '#000000')])
        okno.option_add('*TCombobox*Listbox.background', '#ffffff')
        okno.option_add('*TCombobox*Listbox.foreground', '#000000')
        okno.option_add('*TCombobox*Listbox.selectBackground', '#cce5ff')

def aktualizuj_gui():
    with lock:
        akt = aktywne_pobierania
        kol = w_kolejce
        kopia_statusow = statusy_pobierania.copy()

    ciemny = var_ciemny.get()
    kolor_glowny = "#4ba3e3" if ciemny else "#1a73e8"
    kolor_tekstu = "#ffffff" if ciemny else "#000000"

    if akt == 0 and kol == 0:
        tekst_ogolny = "✅ Gotowe do pracy. Wszystkie zadania zakończone."
        kolor_glowny = "#4CAF50"
        tekst_szczegoly = ""
    else:
        tekst_ogolny = f"Aktywne pobierania: {akt} | W kolejce: {kol}"
        
        linie = []
        for i, (url, stat) in enumerate(kopia_statusow.items(), 1):
            linie.append(f"{i}. {stat}")
        
        tekst_szczegoly = "\n\n".join(linie)
        
    status_ogolny.config(text=tekst_ogolny, fg=kolor_glowny)
    status_szczegoly.config(text=tekst_szczegoly, fg=kolor_tekstu)
    
    okno.after(500, aktualizuj_gui)

def dodaj_do_kolejki():
    global w_kolejce
    tekst = pole_linkow.get("1.0", tk.END).strip()
    urls = [url.strip() for url in tekst.replace('\n', ',').split(',') if url.strip()]

    if not urls:
        pokaz_komunikat("Brak linku", "⚠️ Uwaga!", "Pole z linkami jest puste.\nWklej co najmniej jeden link do filmu lub utworu.", typ="ostrzezenie")
        return

    typ_pobierania = combo_format.get()
    wybrana_jakosc = combo_jakosc.get()
    
    v_qual = 'bestvideo'
    if "1080p" in wybrana_jakosc: v_qual = 'bestvideo[height<=1080]'
    elif "720p" in wybrana_jakosc: v_qual = 'bestvideo[height<=720]'
    elif "480p" in wybrana_jakosc: v_qual = 'bestvideo[height<=480]'
    elif "360p" in wybrana_jakosc: v_qual = 'bestvideo[height<=360]'
    a_qual = 'bestaudio/best'

    if "Tylko Audio" in typ_pobierania: format_wideo = a_qual
    elif "Tylko Wideo" in typ_pobierania: format_wideo = v_qual
    else: format_wideo = f"{v_qual}+{a_qual}/best"

    katalog_docelowy = sciezka_zapisu.get()

    with lock:
        for url in urls:
            kolejka_zadan.put({
                'url': url, 
                'format': format_wideo, 
                'katalog': katalog_docelowy,
                'typ': typ_pobierania 
            })
            w_kolejce += 1
            statusy_pobierania[url] = f"Oczekuje w kolejce...\n    └ {url[:45]}..."
            
    pole_linkow.delete("1.0", tk.END)

def zarzadca_kolejki():
    global aktywne_pobierania, w_kolejce
    while True:
        try: limit = int(combo_limit.get())
        except ValueError: limit = 1
            
        with lock:
            if aktywne_pobierania < limit and not kolejka_zadan.empty():
                zadanie = kolejka_zadan.get()
                aktywne_pobierania += 1
                w_kolejce -= 1
                
                watek_pracownika = threading.Thread(target=proces_pobierania, args=(zadanie,), daemon=True)
                watek_pracownika.start()
                
        time.sleep(0.5)

def proces_pobierania(zadanie):
    global aktywne_pobierania
    url = zadanie['url']
    format_wideo = zadanie['format']
    katalog = zadanie['katalog']
    typ_pobierania = zadanie['typ']
    
    sciezka_ffmpeg = resource_path(".")
    wzor_wyjsciowy = os.path.join(katalog, '%(title)s.%(ext)s')

    with lock:
        statusy_pobierania[url] = f"Inicjowanie pobierania...\n    └ {url[:45]}..."

    def progress_hook(d):
        if d['status'] == 'downloading':
            p_str = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', '---').strip()
            eta = d.get('_eta_str', '---').strip()
            
            nazwa = d.get('filename', url)
            if nazwa:
                nazwa = os.path.basename(nazwa)
            else:
                nazwa = url
            if len(nazwa) > 50: 
                nazwa = nazwa[:47] + "..."

            with lock:
                statusy_pobierania[url] = f"{nazwa}\n    └ Postęp: {p_str}  |  Prędkość: {speed}  |  Pozostało: {eta}"
                
        elif d['status'] == 'finished':
            with lock:
                statusy_pobierania[url] = f"Zakończono pobieranie. Trwa przetwarzanie...\n    └ {url[:45]}..."

    ydl_opts = {
        'format': format_wideo,
        'outtmpl': wzor_wyjsciowy,
        'quiet': True,
        'no_warnings': True,
        'nocolor': True, 
        'ffmpeg_location': sciezka_ffmpeg,
        'progress_hooks': [progress_hook]
    }

    if "Tylko Audio" in typ_pobierania:
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    elif "Tylko Wideo" in typ_pobierania:
        ydl_opts['merge_output_format'] = 'mp4'
    else:
        ydl_opts['merge_output_format'] = 'mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        blad_wiadomosc = str(e)
        krotki_url = url if len(url) < 55 else url[:52] + "..."
        tresc = f"Link: {krotki_url}\n\nSzczegóły:\n{blad_wiadomosc}"
        okno.after(0, lambda: pokaz_komunikat("Błąd pobierania", "❌ Nie udało się pobrać pliku!", tresc, typ="blad"))
    finally:
        with lock:
            aktywne_pobierania -= 1
            if url in statusy_pobierania:
                del statusy_pobierania[url]

okno = TkinterDnD.Tk() 
okno.title(f"Cda Universal Downloader v{__version__}")
okno.geometry("600x630")
okno.resizable(False, False)

style = ttk.Style(okno)
style.theme_use('clam')

try:
    ikona = tk.PhotoImage(file=resource_path("ikona.png"))
    okno.iconphoto(False, ikona)
except Exception:
    pass 

ramka_glowna = tk.LabelFrame(okno, text="", font=("Arial", 10, "bold"), padx=15, pady=10, relief="flat", bd=2)
ramka_glowna.pack(fill="both", expand=False, padx=15, pady=(15, 5))

instrukcja_label = tk.Label(ramka_glowna, text="Wklej lub przeciągnij linki (np. CDA, YouTube, TikTok, Vimeo itp.):", font=("Arial", 10, "bold"))
instrukcja_label.pack(anchor="w", pady=(0, 5))

ramka_linkow = tk.Frame(ramka_glowna)
ramka_linkow.pack(fill="x", pady=5)

pole_linkow = tk.Text(ramka_linkow, height=4, width=45, font=("Arial", 10), relief="flat", bd=1)
pole_linkow.pack(side="left", fill="x", expand=True)
pole_linkow.drop_target_register(DND_TEXT)
pole_linkow.dnd_bind('<<Drop>>', obsluga_drop)

przycisk_wklej = tk.Button(ramka_linkow, text="Wklej", width=10, height=3, font=("Arial", 9, "bold"), command=wklej_link, relief="flat")
przycisk_wklej.pack(side="right", padx=(10, 0))

ramka_opcji = tk.Frame(ramka_glowna)
ramka_opcji.pack(fill="x", pady=15)

tk.Label(ramka_opcji, text="Format pobierania:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
combo_format = ttk.Combobox(ramka_opcji, values=["Wideo + Audio (MP4)", "Tylko Audio (MP3)", "Tylko Wideo (bez dźwięku)"], state="readonly", width=25)
combo_format.current(0)
combo_format.grid(row=0, column=1, padx=(15, 0), pady=5)

var_ciemny = tk.BooleanVar(value=True) 
chk_ciemny = tk.Checkbutton(ramka_opcji, text="Tryb Ciemny 🌙", variable=var_ciemny, command=przelacz_tryb_ciemny, font=("Arial", 9, "bold"))
chk_ciemny.grid(row=0, column=2, padx=(15, 0), sticky="w")

tk.Label(ramka_opcji, text="Jakość wideo:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
combo_jakosc = ttk.Combobox(ramka_opcji, values=["Najlepsza dostępna", "1080p", "720p", "480p", "360p"], state="readonly", width=25)
combo_jakosc.current(0)
combo_jakosc.grid(row=1, column=1, padx=(15, 0), pady=5)

var_wierzch = tk.BooleanVar(value=False)
chk_wierzch = tk.Checkbutton(ramka_opcji, text="Zawsze na wierzchu 📌", variable=var_wierzch, command=przelacz_zawsze_na_wierzchu, font=("Arial", 9, "bold"))
chk_wierzch.grid(row=1, column=2, padx=(15, 0), sticky="w")

tk.Label(ramka_opcji, text="Maksymalnie naraz:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
combo_limit = ttk.Combobox(ramka_opcji, values=["1", "2", "3", "4", "5"], state="readonly", width=6)
combo_limit.current(2)
combo_limit.grid(row=2, column=1, sticky="w", padx=(15, 0), pady=5)

ramka_zapisu = tk.Frame(ramka_glowna)
ramka_zapisu.pack(fill="x", pady=(5, 10))

tk.Label(ramka_zapisu, text="Zapisz w:", font=("Arial", 10, "bold")).pack(anchor="w")

ramka_sciezki = tk.Frame(ramka_zapisu)
ramka_sciezki.pack(fill="x", pady=5)

sciezka_zapisu = tk.StringVar(value=pobierz_katalog_roboczy())
pole_sciezki = tk.Entry(ramka_sciezki, textvariable=sciezka_zapisu, font=("Arial", 9), state="readonly", relief="flat")
pole_sciezki.pack(side="left", fill="x", expand=True)

przycisk_folder = tk.Button(ramka_sciezki, text="Zmień folder", command=wybierz_folder, relief="flat", padx=10)
przycisk_folder.pack(side="left", padx=5)

przycisk_otworz = tk.Button(ramka_sciezki, text="Otwórz folder 📂", command=otworz_folder, relief="flat", padx=10)
przycisk_otworz.pack(side="left")

przycisk_pobierz = tk.Button(ramka_glowna, text="Dodaj do kolejki", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049", activeforeground="white", command=dodaj_do_kolejki, height=2, relief="flat")
przycisk_pobierz.pack(fill="x", pady=(0, 0))

ramka_statusu = tk.Frame(okno, padx=15, pady=5)
ramka_statusu.pack(fill="both", expand=True)

status_ogolny = tk.Label(ramka_statusu, text="Gotowe do pracy", font=("Arial", 11, "bold"))
status_ogolny.pack(anchor="w", pady=(0, 5))

status_szczegoly = tk.Label(ramka_statusu, text="", font=("Courier New", 9), justify="left", anchor="nw")
status_szczegoly.pack(fill="both", expand=True)

przelacz_tryb_ciemny()
okno.after(500, aktualizuj_gui)

watek_zarzadcy = threading.Thread(target=zarzadca_kolejki, daemon=True)
watek_zarzadcy.start()

okno.mainloop()