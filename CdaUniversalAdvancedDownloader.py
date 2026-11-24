__author__ = "KryskiPL"
__version__ = "2.0.4"
__license__ = "GNU GPL v3.0"

import os
import sys
import io
import json
import html
import struct
import ctypes
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_TEXT
import yt_dlp
import threading
import queue
import time
from pathlib import Path
import urllib.request
from urllib.parse import urljoin, urlparse, parse_qs
import re
import subprocess
import base64

if os.name == 'nt':
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("KryskiPL.CdaUniversalAdvancedDownloader.2.0.4")
    except Exception:
        pass

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

DOMAIN_TARGET = base64.b64decode(b'cHJvamVjdHMtc2VrYWkucGw=').decode('utf-8')
PREFIX_TARGET = base64.b64decode(b'U2VrYWkgUGxheWVyIC0=').decode('utf-8')
FALLBACK_TITLE = base64.b64decode(b'VmlkZW8=').decode('utf-8')

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

try:
    from Cryptodome.Cipher import AES as MegaAES
    HAS_MEGA_CRYPTO = "pycryptodome"
except ImportError:
    try:
        from Crypto.Cipher import AES as MegaAES
        HAS_MEGA_CRYPTO = "pycryptodome"
    except ImportError:
        try:
            from cryptography.hazmat.primitives.ciphers import (
                Cipher as CryptoCipher,
                algorithms as CryptoAlgorithms,
                modes as CryptoModes,
            )
            HAS_MEGA_CRYPTO = "cryptography"
        except ImportError:
            HAS_MEGA_CRYPTO = "builtin"

# Wbudowana implementacja AES-128 (CBC + CTR) dla Mega.nz bez zewnętrznych bibliotek
_AES_SBOX = (
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
)

_AES_INV_SBOX = [0] * 256
for _idx_sb, _val_sb in enumerate(_AES_SBOX):
    _AES_INV_SBOX[_val_sb] = _idx_sb
_AES_INV_SBOX = tuple(_AES_INV_SBOX)

_AES_RCON = (0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36)

def _aes_xtime(a):
    return ((a << 1) ^ 0x1b) & 0xff if (a & 0x80) else (a << 1)

def _aes_gmul(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xff
        if hi:
            a ^= 0x1b
        b >>= 1
    return p

_AES_T0 = [0] * 256
_AES_T1 = [0] * 256
_AES_T2 = [0] * 256
_AES_T3 = [0] * 256
for _i in range(256):
    _s = _AES_SBOX[_i]
    _s2 = _aes_xtime(_s)
    _s3 = _s2 ^ _s
    _AES_T0[_i] = (_s2 << 24) | (_s << 16) | (_s << 8) | _s3
    _AES_T1[_i] = (_s3 << 24) | (_s2 << 16) | (_s << 8) | _s
    _AES_T2[_i] = (_s << 24) | (_s3 << 16) | (_s2 << 8) | _s
    _AES_T3[_i] = (_s << 24) | (_s << 16) | (_s3 << 8) | _s2

class PurePythonAES128:
    def __init__(self, key):
        w = list(struct.unpack(">4I", key[:16]))
        sbox = _AES_SBOX
        for i in range(4, 44):
            temp = w[i - 1]
            if i % 4 == 0:
                temp = ((temp << 8) & 0xffffffff) | (temp >> 24)
                temp = (
                    (sbox[temp >> 24] << 24)
                    | (sbox[(temp >> 16) & 0xff] << 16)
                    | (sbox[(temp >> 8) & 0xff] << 8)
                    | sbox[temp & 0xff]
                )
                temp ^= (_AES_RCON[i // 4] << 24)
            w.append(w[i - 4] ^ temp)
        self.rk = w

    def encrypt_block(self, block):
        rk = self.rk
        t0, t1, t2, t3 = _AES_T0, _AES_T1, _AES_T2, _AES_T3
        sbox = _AES_SBOX

        w0, w1, w2, w3 = struct.unpack(">4I", block)
        w0 ^= rk[0]
        w1 ^= rk[1]
        w2 ^= rk[2]
        w3 ^= rk[3]

        for r in range(1, 10):
            base = r * 4
            n0 = t0[w0 >> 24] ^ t1[(w1 >> 16) & 0xff] ^ t2[(w2 >> 8) & 0xff] ^ t3[w3 & 0xff] ^ rk[base]
            n1 = t0[w1 >> 24] ^ t1[(w2 >> 16) & 0xff] ^ t2[(w3 >> 8) & 0xff] ^ t3[w0 & 0xff] ^ rk[base + 1]
            n2 = t0[w2 >> 24] ^ t1[(w3 >> 16) & 0xff] ^ t2[(w0 >> 8) & 0xff] ^ t3[w1 & 0xff] ^ rk[base + 2]
            n3 = t0[w3 >> 24] ^ t1[(w0 >> 16) & 0xff] ^ t2[(w1 >> 8) & 0xff] ^ t3[w2 & 0xff] ^ rk[base + 3]
            w0, w1, w2, w3 = n0, n1, n2, n3

        o0 = ((sbox[w0 >> 24] << 24) | (sbox[(w1 >> 16) & 0xff] << 16) | (sbox[(w2 >> 8) & 0xff] << 8) | sbox[w3 & 0xff]) ^ rk[40]
        o1 = ((sbox[w1 >> 24] << 24) | (sbox[(w2 >> 16) & 0xff] << 16) | (sbox[(w3 >> 8) & 0xff] << 8) | sbox[w0 & 0xff]) ^ rk[41]
        o2 = ((sbox[w2 >> 24] << 24) | (sbox[(w3 >> 16) & 0xff] << 16) | (sbox[(w0 >> 8) & 0xff] << 8) | sbox[w1 & 0xff]) ^ rk[42]
        o3 = ((sbox[w3 >> 24] << 24) | (sbox[(w0 >> 16) & 0xff] << 16) | (sbox[(w1 >> 8) & 0xff] << 8) | sbox[w2 & 0xff]) ^ rk[43]
        return struct.pack(">4I", o0, o1, o2, o3)

    def decrypt_block(self, block):
        inv_sbox = _AES_INV_SBOX
        state = list(block)
        for r in range(10, 0, -1):
            rk_bytes = struct.pack(">4I", *self.rk[r * 4:(r + 1) * 4])
            for i in range(16):
                state[i] ^= rk_bytes[i]
            if r < 10:
                for c in range(0, 16, 4):
                    s0, s1, s2, s3 = state[c], state[c + 1], state[c + 2], state[c + 3]
                    state[c] = _aes_gmul(s0, 14) ^ _aes_gmul(s1, 11) ^ _aes_gmul(s2, 13) ^ _aes_gmul(s3, 9)
                    state[c + 1] = _aes_gmul(s0, 9) ^ _aes_gmul(s1, 14) ^ _aes_gmul(s2, 11) ^ _aes_gmul(s3, 13)
                    state[c + 2] = _aes_gmul(s0, 13) ^ _aes_gmul(s1, 9) ^ _aes_gmul(s2, 14) ^ _aes_gmul(s3, 11)
                    state[c + 3] = _aes_gmul(s0, 11) ^ _aes_gmul(s1, 13) ^ _aes_gmul(s2, 9) ^ _aes_gmul(s3, 14)
            state = [
                state[0], state[13], state[10], state[7],
                state[4], state[1], state[14], state[11],
                state[8], state[5], state[2], state[15],
                state[12], state[9], state[6], state[3],
            ]
            state = [inv_sbox[b] for b in state]
        rk0 = struct.pack(">4I", *self.rk[0:4])
        return bytes(state[i] ^ rk0[i] for i in range(16))

    def decrypt_cbc(self, data, iv=b'\x00' * 16):
        out = bytearray()
        prev = iv
        for i in range(0, len(data), 16):
            blk = data[i:i + 16]
            if len(blk) < 16:
                blk = blk.ljust(16, b'\x00')
            dec = self.decrypt_block(blk)
            out.extend(bytes(a ^ b for a, b in zip(dec, prev)))
            prev = blk
        return bytes(out)

class PurePythonMegaCTR:
    def __init__(self, key, nonce):
        self.aes = PurePythonAES128(key)
        self.nonce = nonce[:8]
        self.counter = 0
        self.buf = bytearray()

    def decrypt(self, data):
        n = len(data)
        if n == 0:
            return b""
        while len(self.buf) < n:
            iv = struct.pack(">8sQ", self.nonce, self.counter)
            self.counter += 1
            self.buf.extend(self.aes.encrypt_block(iv))
        ks = bytes(self.buf[:n])
        del self.buf[:n]
        xored = int.from_bytes(data, "big") ^ int.from_bytes(ks, "big")
        return xored.to_bytes(n, "big")

class AnulowanoPrzezUzytkownika(Exception):
    pass

class WstrzymanoPrzezUzytkownika(Exception):
    pass

class YtdlpLogger:
    def __init__(self):
        self.errors = []

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        clean = re.sub(r'^ERROR:\s*', '', str(msg)).strip()
        if clean:
            self.errors.append(clean)

    def last_error(self):
        return self.errors[-1] if self.errors else ""

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    pelna = os.path.join(base_path, relative_path)
    if os.path.exists(pelna):
        return pelna
    return os.path.join(os.path.abspath("."), relative_path)

_referencje_ikon = []

def ustaw_ikone_okna(win):
    def _aplikuj():
        try:
            if not win.winfo_exists():
                return
            sciezka_png = resource_path("ikona.png")
            if os.path.exists(sciezka_png):
                if HAS_PIL:
                    pil_img = Image.open(sciezka_png).convert("RGBA")
                    img_ico = ImageTk.PhotoImage(pil_img)
                else:
                    img_ico = tk.PhotoImage(file=sciezka_png)
                _referencje_ikon.append(img_ico)
                win.iconphoto(True, img_ico)
        except Exception:
            pass

    _aplikuj()
    try:
        win.after(220, _aplikuj)
        win.after(550, _aplikuj)
    except Exception:
        pass

def pobierz_bazowy_katalog_temp():
    baza = os.path.join(tempfile.gettempdir(), "CdaUniversalDownloader_temp")
    os.makedirs(baza, exist_ok=True)
    return baza

def pobierz_katalog_temp_zadania(zadanie_id):
    katalog_t = os.path.join(pobierz_bazowy_katalog_temp(), str(zadanie_id))
    os.makedirs(katalog_t, exist_ok=True)
    return katalog_t

def wyczysc_katalog_temp_zadania(zadanie_id):
    try:
        katalog_t = os.path.join(pobierz_bazowy_katalog_temp(), str(zadanie_id))
        if os.path.exists(katalog_t):
            shutil.rmtree(katalog_t, ignore_errors=True)
    except Exception:
        pass

def wyczysc_stare_katalogi_temp():
    try:
        baza = os.path.join(tempfile.gettempdir(), "CdaUniversalDownloader_temp")
        if os.path.exists(baza):
            shutil.rmtree(baza, ignore_errors=True)
        os.makedirs(baza, exist_ok=True)
    except Exception:
        pass

def pobierz_katalog_konfiguracji():
    appdata = os.environ.get('APPDATA', str(Path.home()))
    katalog_cfg = os.path.join(appdata, "CdaUniversalDownloader")
    os.makedirs(katalog_cfg, exist_ok=True)
    return katalog_cfg

def pobierz_sciezke_ustawien():
    return os.path.join(pobierz_katalog_konfiguracji(), "ustawienia.json")

def pobierz_stara_sciezke_licznika():
    return os.path.join(pobierz_katalog_konfiguracji(), "licznik.txt")

def domyslne_ustawienia():
    return {
        "licznik": 1,
        "ciemny": True,
        "wierzch": False,
        "retro": False,
        "burn_subs": False,
        "napisy_tryb": "Brak",
        "wlasna_nazwa": False,
        "szablon_nazwy": "film nr %N%",
        "format": "Wideo + Audio (MP4)",
        "jakosc": "Najlepsza dostępna",
        "limit": "3",
        "katalog": str(Path.home() / "Downloads")
    }

def wczytaj_ustawienia():
    dane = domyslne_ustawienia()
    sciezka_json = pobierz_sciezke_ustawien()
    stary_licznik = pobierz_stara_sciezke_licznika()

    if os.path.exists(sciezka_json):
        try:
            with open(sciezka_json, "r", encoding="utf-8") as f:
                wczytane = json.load(f)
                if isinstance(wczytane, dict):
                    dane.update(wczytane)
        except Exception:
            pass
    elif os.path.exists(stary_licznik):
        try:
            with open(stary_licznik, "r", encoding="utf-8") as f:
                dane["licznik"] = max(1, int(f.read().strip()))
        except Exception:
            pass

    try:
        dane["licznik"] = max(1, int(dane.get("licznik", 1)))
    except Exception:
        dane["licznik"] = 1

    if not dane.get("katalog") or not os.path.exists(dane["katalog"]):
        dane["katalog"] = str(Path.home() / "Downloads")

    return dane

inicjalizacja_zakonczona = False
lock = threading.RLock()
dialog_lock = threading.Lock()

def zapisz_ustawienia(*args):
    if not inicjalizacja_zakonczona:
        return
    try:
        with lock:
            aktualny_licznik = licznik_filmow
            dane = {
                "licznik": aktualny_licznik,
                "ciemny": bool(var_ciemny.get()),
                "wierzch": bool(var_wierzch.get()),
                "retro": bool(var_retro.get()),
                "burn_subs": bool(var_burn_subs.get()),
                "napisy_tryb": combo_napisy.get(),
                "wlasna_nazwa": bool(var_wlasna_nazwa.get()),
                "szablon_nazwy": var_szablon_nazwy.get(),
                "format": combo_format.get(),
                "jakosc": combo_jakosc.get(),
                "limit": combo_limit.get(),
                "katalog": sciezka_zapisu.get()
            }
            sciezka_doc = pobierz_sciezke_ustawien()
            sciezka_tmp = sciezka_doc + ".tmp"
            with open(sciezka_tmp, "w", encoding="utf-8") as f:
                json.dump(dane, f, ensure_ascii=False, indent=2)
                f.flush()
            os.replace(sciezka_tmp, sciezka_doc)
    except Exception:
        pass

def sprawdz_i_utworz_skrot_start_menu():
    if os.name != 'nt':
        return
    try:
        appdata = os.environ.get('APPDATA', '')
        if not appdata:
            return
        folder_start = os.path.join(appdata, 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        os.makedirs(folder_start, exist_ok=True)
        sciezka_skrotu = os.path.join(folder_start, 'Cda Universal Advanced Downloader.lnk')

        sciezka_png = resource_path("ikona.png")
        wygenerowane_ico = os.path.join(pobierz_katalog_konfiguracji(), "ikona.ico")
        if HAS_PIL and os.path.exists(sciezka_png):
            try:
                img = Image.open(sciezka_png).convert("RGBA")
                img.save(wygenerowane_ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
            except Exception:
                pass

        if getattr(sys, 'frozen', False):
            cel = sys.executable
            katalog_roboczy = os.path.dirname(cel)
            ikona = f"{cel},0"
            argumenty = ""
        else:
            cel = sys.executable
            skrypt = os.path.abspath(__file__)
            katalog_roboczy = os.path.dirname(skrypt)
            ikona = wygenerowane_ico if os.path.exists(wygenerowane_ico) else f"{cel},0"
            argumenty = f'"{skrypt}"'

        ps_cmd = (
            f"$ws = New-Object -ComObject WScript.Shell; "
            f"$s = $ws.CreateShortcut('{sciezka_skrotu}'); "
            f"$s.TargetPath = '{cel}'; "
            f"$s.WorkingDirectory = '{katalog_roboczy}'; "
            f"$s.IconLocation = '{ikona}'; "
        )
        if argumenty:
            ps_cmd += f"$s.Arguments = '{argumenty}'; "
        ps_cmd += "$s.Save()"

        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=0x08000000
        )
    except Exception:
        pass

zapisane_ustawienia = wczytaj_ustawienia()

kolejka_zadan = queue.Queue()
wszystkie_zadania = {}
kolejnosc_zadan = []
karty_zadan_ui = {}

aktywne_pobierania = 0
w_kolejce = 0
aktywne_wypalania = 0
licznik_filmow = zapisane_ustawienia["licznik"]
bazowy_licznik = zapisane_ustawienia["licznik"]
zarezerwowane_numery = set()
zatwierdzone_numery = set()

ostatni_podglad_url = ""
podglad_timer_id = None
cache_info_ytdlp = {}

class ZadaniePobierania:
    def __init__(self, zadanie_id, url, format_wideo, target_height, selected_quality,
                 katalog, typ, retro_mode, burn_subs, sub_mode, sub_langs,
                 custom_name_enabled, assigned_number, assigned_filename,
                 initial_title=None, playlist_url=None):
        self.id = zadanie_id
        self.url = url
        self.format = format_wideo
        self.target_height = target_height
        self.selected_quality = selected_quality
        self.katalog = katalog
        self.typ = typ
        self.retro_mode = retro_mode
        self.burn_subs = burn_subs
        self.sub_mode = sub_mode
        self.sub_langs = list(sub_langs) if sub_langs else []
        self.custom_name_enabled = custom_name_enabled
        self.assigned_number = assigned_number
        self.assigned_filename = assigned_filename
        self.playlist_url = playlist_url

        self.title = assigned_filename or initial_title or url
        self.status = "queued"
        self.status_text = "Oczekuje w kolejce..."
        self.progress = 0.0
        self.output_path = None
        self.version = 1

        self.pause_requested = threading.Event()
        self.cancel_requested = threading.Event()

    def touch(self):
        self.version += 1

def zamknij_okno_modalne(dlg):
    try:
        dlg.grab_release()
    except Exception:
        pass
    try:
        dlg.destroy()
    except Exception:
        pass
    try:
        okno.after(10, okno.focus_force)
    except Exception:
        pass

def pozycjonuj_okno_obok(dlg, dlg_w, dlg_h):
    okno.update_idletasks()
    main_x = okno.winfo_x()
    main_y = okno.winfo_y()
    main_w = okno.winfo_width()
    screen_w = okno.winfo_screenwidth()
    screen_h = okno.winfo_screenheight()
    odstep = 12

    pos_x_prawa = main_x + main_w + odstep
    if pos_x_prawa + dlg_w <= screen_w:
        pos_x = pos_x_prawa
    else:
        pos_x = max(0, main_x - dlg_w - odstep)

    pos_y = max(0, min(main_y, screen_h - dlg_h - 40))
    dlg.geometry(f"{dlg_w}x{dlg_h}+{pos_x}+{pos_y}")

def bazowe_opcje_ytdlp():
    return {
        'quiet': True,
        'no_warnings': True,
        'nocolor': True,
        'socket_timeout': 15,
        'source_address': '0.0.0.0',
        'retries': 3,
    }

def pobierz_z_cache_lub_ytdlp(url, opts_extra=None):
    teraz = time.time()
    with lock:
        wpis = cache_info_ytdlp.get(url)
        if wpis and (teraz - wpis["ts"] < 120):
            return wpis["info"]

    logger = YtdlpLogger()
    opts = bazowe_opcje_ytdlp()
    opts['noplaylist'] = True
    opts['logger'] = logger
    if opts_extra:
        opts.update(opts_extra)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        szczegol = logger.last_error() or str(e)
        raise Exception(szczegol)

    if info and '_type' in info and info['_type'] == 'playlist' and info.get('entries'):
        info = info['entries'][0]

    if info:
        with lock:
            cache_info_ytdlp[url] = {"ts": teraz, "info": info}
    return info

def wyciagnij_url_playlisty(url):
    try:
        parsed = urlparse(url.strip())
        host = parsed.netloc.lower()
        path = parsed.path.lower()
        qs = parse_qs(parsed.query)
        if 'youtube.com' in host or 'youtu.be' in host:
            if 'list' in qs and qs['list']:
                list_id = qs['list'][0].strip()
                if '/playlist' in path:
                    return f"https://www.youtube.com/playlist?list={list_id}"
                if list_id and not list_id.startswith('RD'):
                    return f"https://www.youtube.com/playlist?list={list_id}"
            return None
        if '/sets/' in path or '/playlist' in path or '/album/' in path:
            return url
    except Exception:
        pass
    return None

def wklej_link():
    try:
        zawartosc = okno.clipboard_get().strip()
        if zawartosc:
            obecny = pole_linkow.get("1.0", "end").strip()
            if obecny and not obecny.endswith(","):
                pole_linkow.insert("end", ", " + zawartosc + ", ")
            else:
                pole_linkow.insert("end", zawartosc + ", ")
            zaplanuj_podglad_linku()
    except tk.TclError:
        pass

def wyczysc_linki():
    pole_linkow.delete("1.0", "end")
    wyczysc_podglad_linku()

def obsluga_drop(event):
    wrzucony_tekst = event.data
    if wrzucony_tekst:
        wrzucony_tekst = wrzucony_tekst.strip('{}').strip()
        obecny = pole_linkow.get("1.0", "end").strip()
        if obecny and not obecny.endswith(","):
            pole_linkow.insert("end", ", " + wrzucony_tekst + ", ")
        else:
            pole_linkow.insert("end", wrzucony_tekst + ", ")
        zaplanuj_podglad_linku()

def wybierz_folder():
    folder = filedialog.askdirectory(initialdir=sciezka_zapisu.get(), title="Wybierz folder pobierania")
    if folder:
        sciezka_zapisu.set(folder)
        zapisz_ustawienia()

def otworz_folder(sciezka=None):
    cel = sciezka if sciezka and os.path.exists(sciezka) else sciezka_zapisu.get()
    if os.path.exists(cel):
        if os.path.isfile(cel):
            subprocess.Popen(['explorer', '/select,', os.path.normpath(cel)])
        else:
            os.startfile(cel)
    else:
        pokaz_komunikat("Błąd", "Nie znaleziono folderu", "Wybrany folder nie istnieje na tym komputerze!", typ="blad")

def tylko_cyfry(nowa_wartosc):
    return nowa_wartosc == "" or nowa_wartosc.isdigit()

def odswiez_podglad_licznika():
    with lock:
        aktualny = licznik_filmow
    if var_licznik_input.get() != str(aktualny):
        var_licznik_input.set(str(aktualny))

def on_licznik_zmiana(*args):
    global licznik_filmow, bazowy_licznik
    tekst = var_licznik_input.get().strip()
    if tekst.isdigit():
        val = int(tekst)
        if val >= 1:
            zmieniono = False
            with lock:
                if licznik_filmow != val:
                    licznik_filmow = val
                    bazowy_licznik = val
                    zarezerwowane_numery.clear()
                    zatwierdzone_numery.clear()
                    zmieniono = True
            if zmieniono:
                zapisz_ustawienia()

def on_licznik_focus_out(event):
    tekst = var_licznik_input.get().strip()
    if not tekst.isdigit() or int(tekst) < 1:
        odswiez_podglad_licznika()

def resetuj_licznik():
    global licznik_filmow, bazowy_licznik
    with lock:
        licznik_filmow = 1
        bazowy_licznik = 1
        zarezerwowane_numery.clear()
        zatwierdzone_numery.clear()
    odswiez_podglad_licznika()
    zapisz_ustawienia()

def zarezerwuj_kolejny_numer():
    global licznik_filmow
    with lock:
        nr = licznik_filmow
        zarezerwowane_numery.add(nr)
        licznik_filmow += 1
    return nr

def zwolnij_numer_licznika(numer):
    global licznik_filmow
    if numer is None:
        return False
    zmieniono = False
    with lock:
        zarezerwowane_numery.discard(numer)
        while (
            licznik_filmow > bazowy_licznik
            and (licznik_filmow - 1) not in zarezerwowane_numery
            and (licznik_filmow - 1) not in zatwierdzone_numery
        ):
            licznik_filmow -= 1
            zmieniono = True
    return zmieniono

def zatwierdz_numer_licznika(numer):
    global bazowy_licznik
    if numer is None:
        return
    with lock:
        zarezerwowane_numery.discard(numer)
        zatwierdzone_numery.add(numer)
        if numer + 1 > bazowy_licznik:
            bazowy_licznik = numer + 1

def pokaz_komunikat(tytul, naglowek, tresc, typ="info"):
    okno_komunikatu = ctk.CTkToplevel(okno)
    okno_komunikatu.title(tytul)
    ustaw_ikone_okna(okno_komunikatu)
    pozycjonuj_okno_obok(okno_komunikatu, 440, 240)
    okno_komunikatu.resizable(False, False)
    okno_komunikatu.transient(okno)
    okno_komunikatu.grab_set()
    okno_komunikatu.attributes('-topmost', True)

    kolor_naglowka = ("#1a1a1a", "#ffffff")
    if typ == "blad":
        kolor_naglowka = ("#d32f2f", "#ff5252")
    elif typ == "ostrzezenie":
        kolor_naglowka = ("#ef6c00", "#ffb74d")

    ctk.CTkLabel(
        okno_komunikatu,
        text=naglowek,
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=kolor_naglowka
    ).pack(pady=(16, 8), padx=16)

    txt_tresc = ctk.CTkTextbox(okno_komunikatu, height=105, font=ctk.CTkFont(size=12), wrap="word")
    txt_tresc.insert("1.0", tresc)
    txt_tresc.configure(state="disabled")
    txt_tresc.pack(fill="x", padx=16, pady=(0, 12))

    def zamknij():
        zamknij_okno_modalne(okno_komunikatu)

    okno_komunikatu.protocol("WM_DELETE_WINDOW", zamknij)
    ctk.CTkButton(okno_komunikatu, text="Rozumiem", width=120, command=zamknij).pack(pady=(0, 14))

def formatuj_czas_trwania(sekundy):
    if not sekundy:
        return ""
    try:
        s = int(sekundy)
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        if h > 0:
            return f"{h}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"
    except Exception:
        return ""

def wyciagnij_dostepne_wysokosci(info):
    dostepne = set()
    if not info:
        return dostepne
    for f in info.get('formats') or []:
        if not isinstance(f, dict):
            continue
        vcodec = f.get('vcodec')
        if vcodec == 'none':
            continue
        w = f.get('width')
        h = f.get('height')
        if w and h:
            dostepne.add(int(min(w, h)))
        elif h:
            dostepne.add(int(h))
        else:
            note = str(f.get('format_note') or f.get('format') or '')
            m_res = re.search(r'\b(2160|1440|1080|720|480|360|240|144)p?\b', note)
            if m_res and (vcodec not in (None, 'none') or f.get('acodec') in (None, 'none') or 'p' in m_res.group(0)):
                dostepne.add(int(m_res.group(1)))
    return dostepne

def wyciagnij_dostepne_napisy(info):
    napisy = {}
    if not info:
        return napisy
    for src_key, is_auto in [('subtitles', False), ('automatic_captions', True)]:
        sub_dict = info.get(src_key) or {}
        if not isinstance(sub_dict, dict):
            continue
        for lang_code, tracks in sub_dict.items():
            if not tracks or lang_code == 'live_chat':
                continue
            nazwa = lang_code
            if isinstance(tracks, list) and tracks and isinstance(tracks[0], dict):
                nazwa = tracks[0].get('name') or lang_code
            etykieta = f"{nazwa} ({lang_code})" + (" [auto]" if is_auto else "")
            if lang_code not in napisy:
                napisy[lang_code] = etykieta
    return napisy

def wybierz_alternatywna_wysokosc(dostepne_wysokosci, docelowa_wysokosc):
    posortowane = sorted(dostepne_wysokosci, reverse=True)
    nizsze = [h for h in posortowane if h < docelowa_wysokosc]
    if nizsze:
        return max(nizsze)
    wyzsze = [h for h in posortowane if h > docelowa_wysokosc]
    if wyzsze:
        return min(wyzsze)
    return posortowane[0]

def zapytaj_o_rozdzielczosc_i_nazwe(org_url, tytul_filmu, wybrana_res_str, dostepne_wysokosci,
                                   alternatywna_wysokosc, custom_name_enabled,
                                   domyslnie_licz_do_licznika, aktualna_nazwa):
    with dialog_lock:
        zdarzenie = threading.Event()
        wynik = {
            "kontynuowac": False,
            "wlasna_nazwa_wlaczona": bool(custom_name_enabled),
            "nowa_nazwa": aktualna_nazwa or "",
            "licz_do_licznika": bool(domyslnie_licz_do_licznika)
        }

        def otworz_okno_decyzji():
            try:
                dlg_w = 480
                dlg_h = 385

                okno_dec = ctk.CTkToplevel(okno)
                okno_dec.title("Niedostępna jakość wideo")
                ustaw_ikone_okna(okno_dec)
                pozycjonuj_okno_obok(okno_dec, dlg_w, dlg_h)
                okno_dec.resizable(False, False)
                okno_dec.transient(okno)
                okno_dec.grab_set()
                okno_dec.attributes('-topmost', True)

                ctk.CTkLabel(
                    okno_dec,
                    text=f"Wybrana jakość ({wybrana_res_str}) nie jest dostępna",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("#ef6c00", "#ffb74d")
                ).pack(pady=(14, 6), padx=15)

                lista_dostepnych = ", ".join(f"{h}p" for h in sorted(dostepne_wysokosci, reverse=True))
                opis_filmu = tytul_filmu if tytul_filmu else org_url
                if len(opis_filmu) > 58:
                    opis_filmu = opis_filmu[:55] + "..."

                tresc = (
                    f"Film: {opis_filmu}\n"
                    f"Dostępne rozdzielczości: {lista_dostepnych}\n\n"
                    f"Czy pobierać dalej w dostępnej rozdzielczości {alternatywna_wysokosc}p?"
                )

                txt_info = ctk.CTkTextbox(okno_dec, height=86, font=ctk.CTkFont(size=12), wrap="word")
                txt_info.insert("1.0", tresc)
                txt_info.configure(state="disabled")
                txt_info.pack(fill="x", padx=16, pady=(2, 10))

                wstepna_nazwa = aktualna_nazwa if aktualna_nazwa else var_szablon_nazwy.get()
                var_lokalne_wlasna_nazwa = tk.BooleanVar(value=bool(custom_name_enabled))
                var_lokalna_nazwa = tk.StringVar(value=wstepna_nazwa or "")
                var_lokalny_licznik = tk.BooleanVar(value=bool(domyslnie_licz_do_licznika))

                ramka_lokalna = ctk.CTkFrame(okno_dec, fg_color="transparent")
                ramka_lokalna.pack(fill="x", padx=16, pady=(0, 8))

                entry_lokalna = ctk.CTkEntry(ramka_lokalna, textvariable=var_lokalna_nazwa, height=30)
                chk_lokalny_licznik = ctk.CTkCheckBox(
                    ramka_lokalna,
                    text="Licz do licznika (%N%)",
                    variable=var_lokalny_licznik,
                    font=ctk.CTkFont(size=12, weight="bold")
                )

                def odswiez_stan_pol_dialogu():
                    aktywne = bool(var_lokalne_wlasna_nazwa.get())
                    if aktywne:
                        entry_lokalna.configure(
                            state="normal",
                            fg_color=("#F9F9FA", "#343638"),
                            text_color=("#1a1a1a", "#DCE4EE"),
                            border_color=("#979DA2", "#565B5E")
                        )
                        chk_lokalny_licznik.configure(
                            state="normal",
                            text_color=("#1a1a1a", "#DCE4EE")
                        )
                    else:
                        entry_lokalna.configure(
                            state="disabled",
                            fg_color=("#E0E0E0", "#232323"),
                            text_color=("gray55", "gray45"),
                            border_color=("#CCCCCC", "#383838")
                        )
                        chk_lokalny_licznik.configure(
                            state="disabled",
                            text_color=("gray55", "gray45")
                        )

                ctk.CTkCheckBox(
                    ramka_lokalna,
                    text="Zapisz jako (tylko dla tego pliku):",
                    variable=var_lokalne_wlasna_nazwa,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    command=odswiez_stan_pol_dialogu
                ).pack(anchor="w", pady=(0, 5))

                entry_lokalna.pack(fill="x")
                chk_lokalny_licznik.pack(anchor="w", pady=(8, 0))
                odswiez_stan_pol_dialogu()

                if bool(var_lokalne_wlasna_nazwa.get()):
                    entry_lokalna.focus_set()
                    entry_lokalna.select_range(0, "end")

                def zakoncz_dialog(kontynuowac):
                    if zdarzenie.is_set():
                        return
                    wynik["kontynuowac"] = kontynuowac
                    wynik["wlasna_nazwa_wlaczona"] = bool(var_lokalne_wlasna_nazwa.get())
                    wynik["nowa_nazwa"] = var_lokalna_nazwa.get().strip()
                    wynik["licz_do_licznika"] = bool(var_lokalne_wlasna_nazwa.get()) and bool(var_lokalny_licznik.get())
                    zamknij_okno_modalne(okno_dec)
                    zdarzenie.set()

                okno_dec.protocol("WM_DELETE_WINDOW", lambda: zakoncz_dialog(False))

                ramka_btn = ctk.CTkFrame(okno_dec, fg_color="transparent")
                ramka_btn.pack(pady=(6, 14))

                ctk.CTkButton(
                    ramka_btn,
                    text=f"Pobierz ({alternatywna_wysokosc}p)",
                    fg_color="#2e7d32",
                    hover_color="#1b5e20",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    width=155,
                    command=lambda: zakoncz_dialog(True)
                ).pack(side="left", padx=8)

                ctk.CTkButton(
                    ramka_btn,
                    text="Anuluj",
                    fg_color=("#757575", "#424242"),
                    hover_color=("#616161", "#303030"),
                    font=ctk.CTkFont(size=13, weight="bold"),
                    width=120,
                    command=lambda: zakoncz_dialog(False)
                ).pack(side="left", padx=8)
            except Exception:
                zdarzenie.set()

        okno.after(0, otworz_okno_decyzji)
        zdarzenie.wait()
        return (
            wynik["kontynuowac"],
            wynik["wlasna_nazwa_wlaczona"],
            wynik["nowa_nazwa"],
            wynik["licz_do_licznika"]
        )

def zapytaj_o_odcinki_playlisty(tytul_playlisty, wpisy):
    with dialog_lock:
        zdarzenie = threading.Event()
        wynik = {
            "wybrane_wpisy": [],
            "podfolder": True
        }

        def otworz_okno_playlisty():
            try:
                dlg_w = 560
                dlg_h = 520

                dlg = ctk.CTkToplevel(okno)
                dlg.title("Wybór odcinków z playlisty")
                ustaw_ikone_okna(dlg)
                pozycjonuj_okno_obok(dlg, dlg_w, dlg_h)
                dlg.resizable(False, False)
                dlg.transient(okno)
                dlg.grab_set()
                dlg.attributes('-topmost', True)

                ctk.CTkLabel(
                    dlg,
                    text=f"Playlista: {tytul_playlisty[:55]}",
                    font=ctk.CTkFont(size=14, weight="bold")
                ).pack(anchor="w", padx=16, pady=(14, 2))

                ctk.CTkLabel(
                    dlg,
                    text=f"Znaleziono {len(wpisy)} pozycji. Zaznacz odcinki do pobrania:",
                    font=ctk.CTkFont(size=12),
                    text_color=("gray30", "gray75")
                ).pack(anchor="w", padx=16, pady=(0, 8))

                ramka_narzedzi = ctk.CTkFrame(dlg, fg_color="transparent")
                ramka_narzedzi.pack(fill="x", padx=16, pady=(0, 8))

                zmienne_odcinkow = []

                def ustaw_wszystkie(stan):
                    for v in zmienne_odcinkow:
                        v.set(stan)

                ctk.CTkButton(ramka_narzedzi, text="Zaznacz wszystkie", width=125, height=28, command=lambda: ustaw_wszystkie(True)).pack(side="left", padx=(0, 6))
                ctk.CTkButton(ramka_narzedzi, text="Odznacz wszystkie", width=125, height=28, fg_color=("#757575", "#424242"), command=lambda: ustaw_wszystkie(False)).pack(side="left", padx=(0, 12))

                ctk.CTkLabel(ramka_narzedzi, text="Zakres:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(4, 4))
                ent_od = ctk.CTkEntry(ramka_narzedzi, width=45, height=28, justify="center")
                ent_od.insert(0, "1")
                ent_od.pack(side="left")
                ctk.CTkLabel(ramka_narzedzi, text="-", font=ctk.CTkFont(size=12)).pack(side="left", padx=3)
                ent_do = ctk.CTkEntry(ramka_narzedzi, width=45, height=28, justify="center")
                ent_do.insert(0, str(len(wpisy)))
                ent_do.pack(side="left", padx=(0, 6))

                def zaznacz_zakres():
                    try:
                        a = max(1, int(ent_od.get().strip()))
                        b = min(len(wpisy), int(ent_do.get().strip()))
                        for idx_z, v in enumerate(zmienne_odcinkow, 1):
                            v.set(a <= idx_z <= b)
                    except ValueError:
                        pass

                ctk.CTkButton(ramka_narzedzi, text="Zastosuj", width=70, height=28, command=zaznacz_zakres).pack(side="left")

                lista_scroll = ctk.CTkScrollableFrame(dlg, height=275)
                lista_scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))

                for idx_ep, ep in enumerate(wpisy, 1):
                    var_ep = tk.BooleanVar(value=True)
                    zmienne_odcinkow.append(var_ep)
                    tyt = ep.get('title') or f"Odcinek {idx_ep}"
                    czas = formatuj_czas_trwania(ep.get('duration'))
                    etykieta = f"{idx_ep}. {tyt}" + (f" [{czas}]" if czas else "")
                    if len(etykieta) > 68:
                        etykieta = etykieta[:65] + "..."
                    ctk.CTkCheckBox(lista_scroll, text=etykieta, variable=var_ep, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=3, padx=4)

                var_podfolder = tk.BooleanVar(value=True)
                ctk.CTkCheckBox(
                    dlg,
                    text="Zapisz w podfolderze o nazwie playlisty",
                    variable=var_podfolder,
                    font=ctk.CTkFont(size=12, weight="bold")
                ).pack(anchor="w", padx=16, pady=(0, 10))

                def zakoncz(potwierdz):
                    if zdarzenie.is_set():
                        return
                    if potwierdz:
                        wynik["wybrane_wpisy"] = [ep for ep, v in zip(wpisy, zmienne_odcinkow) if v.get()]
                        wynik["podfolder"] = bool(var_podfolder.get())
                    zamknij_okno_modalne(dlg)
                    zdarzenie.set()

                dlg.protocol("WM_DELETE_WINDOW", lambda: zakoncz(False))

                ramka_dol = ctk.CTkFrame(dlg, fg_color="transparent")
                ramka_dol.pack(pady=(0, 14))

                ctk.CTkButton(
                    ramka_dol,
                    text="Dodaj zaznaczone",
                    fg_color="#2e7d32",
                    hover_color="#1b5e20",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    width=165,
                    command=lambda: zakoncz(True)
                ).pack(side="left", padx=8)

                ctk.CTkButton(
                    ramka_dol,
                    text="Anuluj",
                    fg_color=("#757575", "#424242"),
                    hover_color=("#616161", "#303030"),
                    font=ctk.CTkFont(size=13, weight="bold"),
                    width=120,
                    command=lambda: zakoncz(False)
                ).pack(side="left", padx=8)
            except Exception:
                zdarzenie.set()

        okno.after(0, otworz_okno_playlisty)
        zdarzenie.wait()
        return wynik["wybrane_wpisy"], wynik["podfolder"]

def zapytaj_o_jezyki_napisow(tytul_filmu, dostepne_napisy):
    with dialog_lock:
        zdarzenie = threading.Event()
        wynik = {"wybrane": []}

        def otworz_okno_napisow():
            try:
                dlg = ctk.CTkToplevel(okno)
                dlg.title("Wybór napisów")
                ustaw_ikone_okna(dlg)
                pozycjonuj_okno_obok(dlg, 440, 410)
                dlg.resizable(False, False)
                dlg.transient(okno)
                dlg.grab_set()
                dlg.attributes('-topmost', True)

                ctk.CTkLabel(
                    dlg,
                    text="Wybierz języki napisów do pobrania",
                    font=ctk.CTkFont(size=14, weight="bold")
                ).pack(anchor="w", padx=16, pady=(14, 2))

                ctk.CTkLabel(
                    dlg,
                    text=(tytul_filmu or "")[:55],
                    font=ctk.CTkFont(size=12),
                    text_color=("gray30", "gray75")
                ).pack(anchor="w", padx=16, pady=(0, 8))

                scroll = ctk.CTkScrollableFrame(dlg, height=245)
                scroll.pack(fill="both", expand=True, padx=16, pady=(0, 10))

                zmienne_lang = {}
                for code, label in dostepne_napisy.items():
                    domyslnie = code.startswith('pl') or code.startswith('en')
                    v = tk.BooleanVar(value=domyslnie)
                    zmienne_lang[code] = v
                    ctk.CTkCheckBox(scroll, text=label, variable=v, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=3, padx=4)

                def zakoncz(potwierdz):
                    if zdarzenie.is_set():
                        return
                    if potwierdz:
                        wynik["wybrane"] = [c for c, v in zmienne_lang.items() if v.get()]
                    zamknij_okno_modalne(dlg)
                    zdarzenie.set()

                dlg.protocol("WM_DELETE_WINDOW", lambda: zakoncz(False))

                ramka_btn = ctk.CTkFrame(dlg, fg_color="transparent")
                ramka_btn.pack(pady=(0, 14))

                ctk.CTkButton(ramka_btn, text="Zatwierdź", fg_color="#2e7d32", hover_color="#1b5e20", width=130, command=lambda: zakoncz(True)).pack(side="left", padx=8)
                ctk.CTkButton(ramka_btn, text="Pomiń napisy", fg_color=("#757575", "#424242"), width=130, command=lambda: zakoncz(False)).pack(side="left", padx=8)
            except Exception:
                zdarzenie.set()

        okno.after(0, otworz_okno_napisow)
        zdarzenie.wait()
        return wynik["wybrane"]

def zbuduj_bezpieczna_nazwe_pliku(szablon, numer=None, sufiks_duplikatu=0):
    tekst_szablonu = szablon.strip() if szablon and szablon.strip() else "film nr %N%"
    if numer is not None and "%N%" in tekst_szablonu:
        nazwa = tekst_szablonu.replace("%N%", str(numer))
    else:
        nazwa = tekst_szablonu.replace("%N%", "").strip()
    nazwa = re.sub(r'[\\/*?:"<>|]', "", nazwa).strip()
    if not nazwa:
        nazwa = f"film_{numer}" if numer is not None else "film"
    if sufiks_duplikatu > 0:
        nazwa = f"{nazwa} ({sufiks_duplikatu + 1})"
    return nazwa

def buduj_format_ytdlp(typ_pobierania, docelowa_wysokosc):
    a_qual = 'bestaudio/best'
    if "Tylko Audio" in typ_pobierania:
        return a_qual

    if docelowa_wysokosc:
        v_qual = f"bestvideo[height<={docelowa_wysokosc}]"
        b_qual = f"best[height<={docelowa_wysokosc}]"
        if "Tylko Wideo" in typ_pobierania:
            return f"{v_qual}[ext=mp4]/{v_qual}/{b_qual}[ext=mp4]/{b_qual}/bestvideo"
        return f"{v_qual}[ext=mp4]+{a_qual}[ext=m4a]/{v_qual}+{a_qual}/{b_qual}[ext=mp4]/{b_qual}/best[ext=mp4]/best"
    else:
        if "Tylko Wideo" in typ_pobierania:
            return "bestvideo[ext=mp4]/bestvideo/best[ext=mp4]/best"
        return f"bestvideo[ext=mp4]+{a_qual}[ext=m4a]/bestvideo+{a_qual}/best[ext=mp4]/best"

def pobierz_jezyki_z_ustawienia(tryb_napisow):
    if tryb_napisow == "Polski (pl)":
        return ["pl"]
    if tryb_napisow == "Angielski (en)":
        return ["en"]
    if tryb_napisow == "Polski + Angielski (pl, en)":
        return ["pl", "en"]
    return []

def zarejestruj_i_kolejkuj_zadanie(zadanie_obj):
    global w_kolejce
    with lock:
        wszystkie_zadania[zadanie_obj.id] = zadanie_obj
        if zadanie_obj.id not in kolejnosc_zadan:
            kolejnosc_zadan.append(zadanie_obj.id)
        w_kolejce += 1
        kolejka_zadan.put(zadanie_obj)

def dodaj_do_kolejki():
    tekst = pole_linkow.get("1.0", "end").strip()
    urls = [url.strip() for url in tekst.replace('\n', ',').split(',') if url.strip()]

    if not urls:
        pokaz_komunikat("Brak linku", "Uwaga!", "Pole z linkami jest puste.\nWklej co najmniej jeden link do filmu lub utworu.", typ="ostrzezenie")
        return

    typ_pobierania = combo_format.get()
    wybrana_jakosc = combo_jakosc.get()
    tryb_retro = var_retro.get()
    tryb_burn = var_burn_subs.get()
    tryb_napisow = combo_napisy.get()
    uzyj_wlasnej_nazwy = var_wlasna_nazwa.get()
    szablon_nazwy = var_szablon_nazwy.get()
    katalog_docelowy = sciezka_zapisu.get()

    docelowa_wysokosc = None
    m_wys = re.search(r'(\d+)p', wybrana_jakosc)
    if m_wys:
        docelowa_wysokosc = int(m_wys.group(1))

    format_wideo = buduj_format_ytdlp(typ_pobierania, docelowa_wysokosc)
    baza_czasu = time.time_ns()
    sufiks_bez_licznika = 0
    ma_znacznik_licznika = uzyj_wlasnej_nazwy and ("%N%" in szablon_nazwy)

    for idx, url in enumerate(urls):
        przypisany_numer = None
        przypisana_nazwa = None

        if uzyj_wlasnej_nazwy:
            if ma_znacznik_licznika:
                przypisany_numer = zarezerwuj_kolejny_numer()
                przypisana_nazwa = zbuduj_bezpieczna_nazwe_pliku(szablon_nazwy, przypisany_numer, 0)
            else:
                przypisana_nazwa = zbuduj_bezpieczna_nazwe_pliku(szablon_nazwy, None, sufiks_bez_licznika)
                sufiks_bez_licznika += 1

        wstepny_tytul = None
        with lock:
            cached = cache_info_ytdlp.get(url)
            if cached and isinstance(cached.get("info"), dict):
                wstepny_tytul = cached["info"].get("title")

        zad = ZadaniePobierania(
            zadanie_id=f"{baza_czasu}_{idx}",
            url=url,
            format_wideo=format_wideo,
            target_height=docelowa_wysokosc,
            selected_quality=wybrana_jakosc,
            katalog=katalog_docelowy,
            typ=typ_pobierania,
            retro_mode=tryb_retro,
            burn_subs=tryb_burn,
            sub_mode=tryb_napisow,
            sub_langs=pobierz_jezyki_z_ustawienia(tryb_napisow),
            custom_name_enabled=uzyj_wlasnej_nazwy,
            assigned_number=przypisany_numer,
            assigned_filename=przypisana_nazwa,
            initial_title=wstepny_tytul,
            playlist_url=wyciagnij_url_playlisty(url)
        )
        zarejestruj_i_kolejkuj_zadanie(zad)

    if ma_znacznik_licznika:
        odswiez_podglad_licznika()
        zapisz_ustawienia()

    pole_linkow.delete("1.0", "end")
    wyczysc_podglad_linku()

def zarzadca_kolejki():
    global aktywne_pobierania, w_kolejce, aktywne_wypalania
    while True:
        with lock:
            if not kolejka_zadan.empty():
                try:
                    limit = int(combo_limit.get())
                except ValueError:
                    limit = 1

                nastepne = kolejka_zadan.queue[0]
                if nastepne.cancel_requested.is_set():
                    kolejka_zadan.get()
                    w_kolejce = max(0, w_kolejce - 1)
                    nastepne.status = "cancelled"
                    nastepne.status_text = "Anulowano"
                    nastepne.touch()
                    wyczysc_katalog_temp_zadania(nastepne.id)
                    if nastepne.assigned_number is not None:
                        if zwolnij_numer_licznika(nastepne.assigned_number):
                            okno.after(0, odswiez_podglad_licznika)
                            zapisz_ustawienia()
                    continue

                if nastepne.pause_requested.is_set():
                    kolejka_zadan.get()
                    w_kolejce = max(0, w_kolejce - 1)
                    nastepne.status = "paused"
                    nastepne.status_text = "Wstrzymano"
                    nastepne.touch()
                    continue

                is_next_burn = nastepne.burn_subs
                if is_next_burn or aktywne_wypalania > 0:
                    limit = 1

                if aktywne_pobierania < limit:
                    zadanie = kolejka_zadan.get()
                    aktywne_pobierania += 1
                    w_kolejce = max(0, w_kolejce - 1)
                    if zadanie.burn_subs:
                        aktywne_wypalania += 1

                    threading.Thread(target=proces_pobierania, args=(zadanie,), daemon=True).start()

        time.sleep(0.3)

def pobierz_dane_okru(url):
    norm_url = re.sub(r'https?://m\.(ok\.ru|odnoklassniki\.ru)', r'https://\1', url.strip(), flags=re.IGNORECASE)
    req = urllib.request.Request(norm_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
        "Referer": "https://ok.ru/"
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        strona = resp.read().decode("utf-8", errors="replace")

    opcje_matches = re.findall(r'data-options="([^"]+)"', strona)
    metadata = None
    for raw_opt in opcje_matches:
        unescaped = html.unescape(raw_opt)
        if "flashvars" not in unescaped:
            continue
        try:
            opt_json = json.loads(unescaped)
            fv = opt_json.get("flashvars")
            if isinstance(fv, str):
                fv = json.loads(fv)
            if isinstance(fv, dict) and "metadata" in fv:
                md = fv["metadata"]
                if isinstance(md, str):
                    md = json.loads(md)
                if isinstance(md, dict):
                    metadata = md
                    break
        except Exception:
            continue

    if not metadata:
        raise Exception("Nie udało się odczytać metadanych filmu z OK.ru (film może być prywatny lub usunięty).")

    mapa_jakosci = {
        "ultra": 2160,
        "quad": 1440,
        "full": 1080,
        "hd": 720,
        "sd": 480,
        "low": 360,
        "lowest": 240,
        "mobile": 144,
    }

    strumienie = {}
    for item in metadata.get("videos") or []:
        if not isinstance(item, dict):
            continue
        nazwa_jakosci = str(item.get("name") or "").lower().strip()
        stream_url = item.get("url")
        if stream_url and nazwa_jakosci in mapa_jakosci:
            strumienie[mapa_jakosci[nazwa_jakosci]] = stream_url

    movie_info = metadata.get("movie") if isinstance(metadata.get("movie"), dict) else {}
    tytul = movie_info.get("title") or "OK_Video"
    tytul = re.sub(r'[\\/*?:"<>|]', "", str(tytul)).strip() or "OK_Video"
    poster = movie_info.get("poster")
    duration = movie_info.get("duration")
    hls_url = metadata.get("hlsManifestUrl") or metadata.get("ondemandHls")

    if not strumienie and not hls_url:
        raise Exception("Brak dostępnych strumieni wideo na stronie OK.ru.")

    return {
        "title": tytul,
        "thumbnail": poster,
        "duration": duration,
        "streams_by_height": strumienie,
        "hls_url": hls_url
    }

def mega_base64_decode(data):
    data += '=' * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data)

def odszyfruj_atrybuty_mega(enc_attr, k):
    attr_bytes = mega_base64_decode(enc_attr)
    if HAS_MEGA_CRYPTO == "pycryptodome":
        cipher = MegaAES.new(k, MegaAES.MODE_CBC, iv=b'\x00' * 16)
        dec = cipher.decrypt(attr_bytes)
    elif HAS_MEGA_CRYPTO == "cryptography":
        cipher = CryptoCipher(CryptoAlgorithms.AES(k), CryptoModes.CBC(b'\x00' * 16))
        decryptor = cipher.decryptor()
        dec = decryptor.update(attr_bytes) + decryptor.finalize()
    else:
        aes = PurePythonAES128(k)
        dec = aes.decrypt_cbc(attr_bytes, iv=b'\x00' * 16)

    dec = dec.rstrip(b'\x00')
    if dec.startswith(b'MEGA'):
        meta = json.loads(dec[4:].decode('utf-8', errors='replace'))
        return meta.get('n', 'mega_plik')
    return 'mega_plik'

def pobierz_metadane_mega(org_url):
    if re.search(r'mega\.(?:co\.)?nz/(?:folder/|#F!)', org_url, re.IGNORECASE):
        raise Exception("Linki do całych folderów Mega.nz nie są obsługiwane.")
    m = re.search(r'mega\.(?:co\.)?nz/(?:file/|#!)([a-zA-Z0-9_-]+)[#!]([a-zA-Z0-9_-]+)', org_url)
    if not m:
        raise Exception("Nieprawidłowy format linku Mega.nz.")

    file_id, file_key = m.group(1), m.group(2)
    key_bytes = mega_base64_decode(file_key)
    if len(key_bytes) < 32:
        raise Exception("Nieprawidłowy klucz pliku Mega.nz.")

    k = bytes(a ^ b for a, b in zip(key_bytes[0:16], key_bytes[16:32]))
    nonce = key_bytes[16:24]

    api_url = "https://g.api.mega.co.nz/cs?id=0"
    payload = json.dumps([{"a": "g", "g": 1, "p": file_id}]).encode("utf-8")
    req_api = urllib.request.Request(api_url, data=payload, headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req_api, timeout=15) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))

    first = res_data[0]
    if isinstance(first, int) or (isinstance(first, dict) and 'e' in first):
        kod = first if isinstance(first, int) else first.get('e')
        raise Exception(f"Błąd Mega.nz (kod: {kod}).")

    enc_attr = first.get('at', '')
    orig_name = odszyfruj_atrybuty_mega(enc_attr, k) if enc_attr else "mega_plik.mp4"
    return {
        "dl_url": first.get('g'),
        "file_size": int(first.get('s', 0)),
        "orig_name": orig_name,
        "k": k,
        "nonce": nonce
    }

def pobierz_z_mega(zadanie, exe_ffmpeg, katalog_temp):
    org_url = zadanie.url
    katalog = zadanie.katalog
    typ_pobierania = zadanie.typ
    assigned_filename = zadanie.assigned_filename

    with lock:
        zadanie.status = "checking"
        zadanie.status_text = "Łączenie z Mega.nz..."
        zadanie.touch()

    meta = pobierz_metadane_mega(org_url)
    dl_url = meta["dl_url"]
    file_size = meta["file_size"]
    k = meta["k"]
    nonce = meta["nonce"]
    if not dl_url:
        raise Exception("Nie udało się uzyskać bezpośredniego adresu pobierania z Mega.nz.")

    orig_name = re.sub(r'[\\/*?:"<>|]', "", meta["orig_name"]).strip() or "mega_plik.mp4"
    orig_base, orig_ext = os.path.splitext(orig_name)
    if not orig_ext:
        orig_ext = ".mp4"

    tylko_audio = "Tylko Audio" in typ_pobierania
    docelowa_baza = assigned_filename if assigned_filename else orig_base

    if tylko_audio and orig_ext.lower() != ".mp3":
        tymczasowy_plik = os.path.join(katalog_temp, f"mega_tmp_{zadanie.id}{orig_ext}")
        koncowy_plik = os.path.join(katalog, f"{docelowa_baza}.mp3")
        zapis_sciezka = tymczasowy_plik
    else:
        tymczasowy_plik = os.path.join(katalog_temp, f"mega_part_{zadanie.id}{orig_ext}")
        koncowy_plik = os.path.join(katalog, f"{docelowa_baza}{orig_ext}")
        zapis_sciezka = tymczasowy_plik

    with lock:
        zadanie.title = os.path.basename(koncowy_plik)
        zadanie.status = "downloading"
        zadanie.touch()

    if HAS_MEGA_CRYPTO == "pycryptodome":
        ctr_cipher = MegaAES.new(k, MegaAES.MODE_CTR, nonce=nonce, initial_value=0)
        decrypt_chunk = ctr_cipher.decrypt
    elif HAS_MEGA_CRYPTO == "cryptography":
        ctr_cipher = CryptoCipher(CryptoAlgorithms.AES(k), CryptoModes.CTR(nonce + b'\x00' * 8))
        ctr_dec = ctr_cipher.decryptor()
        decrypt_chunk = ctr_dec.update
    else:
        ctr_cipher = PurePythonMegaCTR(k, nonce)
        decrypt_chunk = ctr_cipher.decrypt

    req_dl = urllib.request.Request(dl_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    pobrano = 0
    start_ts = time.time()
    ostatnia_aktualizacja = 0

    try:
        with urllib.request.urlopen(req_dl, timeout=30) as stream, open(zapis_sciezka, "wb") as out_f:
            while True:
                if zadanie.cancel_requested.is_set():
                    raise AnulowanoPrzezUzytkownika()
                if zadanie.pause_requested.is_set():
                    raise WstrzymanoPrzezUzytkownika()

                chunk = stream.read(65536)
                if not chunk:
                    break
                out_f.write(decrypt_chunk(chunk))
                pobrano += len(chunk)

                teraz = time.time()
                if teraz - ostatnia_aktualizacja >= 0.25:
                    ostatnia_aktualizacja = teraz
                    elapsed = max(0.01, teraz - start_ts)
                    speed = pobrano / elapsed
                    speed_str = f"{speed / (1024 * 1024):.2f} MiB/s" if speed >= 1024 * 1024 else f"{speed / 1024:.1f} KiB/s"

                    if file_size > 0:
                        proc = min(1.0, pobrano / file_size)
                        pozostalo = int((file_size - pobrano) / max(1.0, speed))
                        eta_str = f"{pozostalo // 60:02d}:{pozostalo % 60:02d}"
                        stat_line = f"{proc * 100:.1f}% • {speed_str} • Pozostało: {eta_str}"
                    else:
                        proc = 0.0
                        stat_line = f"{pobrano / (1024 * 1024):.1f} MB • {speed_str}"

                    with lock:
                        zadanie.progress = proc
                        zadanie.status_text = stat_line
                        zadanie.touch()

        if tylko_audio and orig_ext.lower() != ".mp3" and os.path.exists(zapis_sciezka):
            with lock:
                zadanie.status = "processing"
                zadanie.status_text = "Konwersja do MP3 i przenoszenie..."
                zadanie.touch()
            c_flags = 0x08000000 if os.name == 'nt' else 0
            cmd = [exe_ffmpeg, '-y', '-i', zapis_sciezka, '-vn', '-ab', '192k', koncowy_plik]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=c_flags)
            if os.path.exists(zapis_sciezka):
                os.remove(zapis_sciezka)
        elif os.path.exists(zapis_sciezka):
            with lock:
                zadanie.status = "processing"
                zadanie.status_text = "Przenoszenie do folderu zapisu..."
                zadanie.touch()
            shutil.move(zapis_sciezka, koncowy_plik)

        with lock:
            zadanie.output_path = koncowy_plik
            zadanie.progress = 1.0
            zadanie.touch()

    except (AnulowanoPrzezUzytkownika, WstrzymanoPrzezUzytkownika):
        if os.path.exists(zapis_sciezka):
            try:
                os.remove(zapis_sciezka)
            except Exception:
                pass
        raise
    except Exception:
        if os.path.exists(zapis_sciezka):
            try:
                os.remove(zapis_sciezka)
            except Exception:
                pass
        raise

def proces_pobierania(zadanie):
    global aktywne_pobierania, aktywne_wypalania
    org_url = zadanie.url
    format_wideo = zadanie.format
    docelowa_wysokosc = zadanie.target_height
    wybrana_jakosc = zadanie.selected_quality
    katalog = zadanie.katalog
    typ_pobierania = zadanie.typ
    is_retro = zadanie.retro_mode
    is_burn = zadanie.burn_subs
    sub_mode = zadanie.sub_mode
    sub_langs = list(zadanie.sub_langs)
    custom_name_enabled = zadanie.custom_name_enabled
    assigned_number = zadanie.assigned_number
    assigned_filename = zadanie.assigned_filename

    os.makedirs(katalog, exist_ok=True)
    katalog_temp = pobierz_katalog_temp_zadania(zadanie.id)

    sciezka_ffmpeg = resource_path(".")
    exe_ffmpeg = os.path.join(sciezka_ffmpeg, 'ffmpeg.exe')
    if not os.path.exists(exe_ffmpeg):
        exe_ffmpeg = 'ffmpeg'

    if assigned_filename:
        szablon_wyjsciowy = f"{assigned_filename}.%(ext)s"
    else:
        szablon_wyjsciowy = '%(title)s.%(ext)s'

    aktualny_url = org_url
    special_sub_url = None
    special_temp_video = None
    special_temp_sub = None
    special_final_video = None
    sub_ext = 'vtt'
    pobieranie_zakonczone_sukcesem = False
    wstrzymano_zadanie = False
    rozwinieto_playliste = False
    ostatni_plik_wyjsciowy = None

    try:
        if zadanie.cancel_requested.is_set():
            raise AnulowanoPrzezUzytkownika()
        if zadanie.pause_requested.is_set():
            raise WstrzymanoPrzezUzytkownika()

        jest_mega = bool(re.search(r'mega\.(?:co\.)?nz/', org_url, re.IGNORECASE))
        jest_okru = bool(re.search(r'(?:ok\.ru|odnoklassniki\.ru)/', org_url, re.IGNORECASE))
        jest_domena_retro = is_retro and DOMAIN_TARGET in org_url

        if zadanie.playlist_url and not jest_mega and not jest_okru and not jest_domena_retro:
            with lock:
                zadanie.status = "checking"
                zadanie.status_text = "Pobieranie listy odcinków z playlisty..."
                zadanie.touch()

            opts_pl = bazowe_opcje_ytdlp()
            opts_pl['extract_flat'] = 'in_playlist'
            opts_pl['noplaylist'] = False
            opts_pl['playlistend'] = 300
            with yt_dlp.YoutubeDL(opts_pl) as ydl_pl:
                info_pl = ydl_pl.extract_info(zadanie.playlist_url, download=False)

            if info_pl and info_pl.get('entries'):
                wpisy = [
                    e for e in info_pl['entries']
                    if isinstance(e, dict) and (e.get('id') or e.get('url') or e.get('webpage_url'))
                ]
                if len(wpisy) > 1:
                    tytul_pl = info_pl.get('title') or "Playlista"
                    wybrane, czy_podfolder = zapytaj_o_odcinki_playlisty(tytul_pl, wpisy)
                    if not wybrane:
                        raise AnulowanoPrzezUzytkownika()

                    if assigned_number is not None:
                        zwolnij_numer_licznika(assigned_number)
                        assigned_number = None
                        zadanie.assigned_number = None

                    katalog_pl = katalog
                    if czy_podfolder:
                        bezpieczny_folder = re.sub(r'[\\/*?:"<>|]', "", tytul_pl).strip() or "Playlista"
                        katalog_pl = os.path.join(katalog, bezpieczny_folder)
                        os.makedirs(katalog_pl, exist_ok=True)

                    baza_czasu = time.time_ns()
                    szablon_akt = var_szablon_nazwy.get()
                    ma_n = custom_name_enabled and ("%N%" in szablon_akt)
                    for idx_ep, ep in enumerate(wybrane):
                        ep_url = ep.get('webpage_url') or ep.get('url')
                        if ep_url and not ep_url.startswith('http') and ep.get('id'):
                            ep_url = f"https://www.youtube.com/watch?v={ep['id']}"
                        elif not ep_url and ep.get('id'):
                            ep_url = f"https://www.youtube.com/watch?v={ep['id']}"
                        if not ep_url:
                            continue

                        ep_num = None
                        ep_name = None
                        if custom_name_enabled:
                            if ma_n:
                                ep_num = zarezerwuj_kolejny_numer()
                                ep_name = zbuduj_bezpieczna_nazwe_pliku(szablon_akt, ep_num, 0)
                            else:
                                ep_name = zbuduj_bezpieczna_nazwe_pliku(szablon_akt, None, idx_ep)

                        nowe_zad = ZadaniePobierania(
                            zadanie_id=f"{baza_czasu}_pl_{idx_ep}",
                            url=ep_url,
                            format_wideo=format_wideo,
                            target_height=docelowa_wysokosc,
                            selected_quality=wybrana_jakosc,
                            katalog=katalog_pl,
                            typ=typ_pobierania,
                            retro_mode=is_retro,
                            burn_subs=is_burn,
                            sub_mode=sub_mode,
                            sub_langs=sub_langs,
                            custom_name_enabled=custom_name_enabled,
                            assigned_number=ep_num,
                            assigned_filename=ep_name,
                            initial_title=ep.get('title'),
                            playlist_url=None
                        )
                        zarejestruj_i_kolejkuj_zadanie(nowe_zad)

                    okno.after(0, odswiez_podglad_licznika)
                    zapisz_ustawienia()
                    rozwinieto_playliste = True
                    return

        if jest_mega:
            pobierz_z_mega(zadanie, exe_ffmpeg, katalog_temp)
            pobieranie_zakonczone_sukcesem = True
            return

        sciezki_ytdlp = {
            'home': katalog,
            'temp': katalog_temp
        }

        if jest_domena_retro:
            if not HAS_SELENIUM:
                raise Exception("Brakuje biblioteki Selenium! Wpisz w konsoli: pip install selenium")

            with lock:
                zadanie.status = "checking"
                zadanie.status_text = "Ładowanie strony..."
                zadanie.touch()

            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--mute-audio")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

            service = Service()
            if os.name == 'nt':
                service.creation_flags = 0x08000000

            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(org_url)

            timeout = 15
            start_time = time.time()
            js_video_url = None
            js_sub_url = None

            while time.time() - start_time < timeout:
                if zadanie.cancel_requested.is_set():
                    driver.quit()
                    raise AnulowanoPrzezUzytkownika()
                if zadanie.pause_requested.is_set():
                    driver.quit()
                    raise WstrzymanoPrzezUzytkownika()

                html_src = driver.page_source
                if not js_video_url:
                    v_match = re.search(r'VIDEO_SOURCES\s*=\s*\[(.*?)\]', html_src, re.DOTALL)
                    if v_match:
                        srcs = re.findall(r'''src\s*:\s*['"]([^'"]+)['"]''', v_match.group(1))
                        if srcs:
                            js_video_url = srcs[0]

                if not js_sub_url:
                    s_match = re.search(r'SUBTITLE_TRACKS\s*=\s*\[(.*?)\]', html_src, re.DOTALL)
                    if s_match:
                        for block in s_match.group(1).split('{'):
                            if re.search(r"['\"]pl['\"]|['\"]Polski['\"]|['\"]pl-PL['\"]", block, re.IGNORECASE):
                                src_m = re.search(r'''src\s*:\s*['"]([^'"]+)['"]''', block)
                                if src_m:
                                    js_sub_url = src_m.group(1)

                if not js_sub_url:
                    sub_links = re.findall(r'["\']([^"\']+\.(?:vtt|srt|ass)(?:[?#][^"\']*)?)["\']', html_src, re.IGNORECASE)
                    if sub_links:
                        for link in sub_links:
                            if 'pl' in link.lower() or 'polski' in link.lower():
                                js_sub_url = link
                                break
                        if not js_sub_url:
                            js_sub_url = sub_links[0]

                if js_video_url and js_sub_url:
                    break
                elif js_video_url and (time.time() - start_time > 8):
                    break
                time.sleep(1)

            if assigned_filename:
                vid_title = assigned_filename
            else:
                vid_title = driver.title.replace(PREFIX_TARGET, "").strip()
                vid_title = re.sub(r'[\\/*?:"<>|%,\'=]', "", vid_title).strip() or FALLBACK_TITLE

            driver.quit()

            if not js_video_url:
                raise Exception("Przekroczono limit czasu. Źródło strumienia nie pojawiło się w kodzie strony.")

            with lock:
                zadanie.title = vid_title
                zadanie.touch()

            aktualny_url = urljoin(org_url, js_video_url)
            if js_sub_url:
                special_sub_url = urljoin(org_url, js_sub_url)

            if special_sub_url:
                parsed_sub = special_sub_url.lower()
                if '.ass' in parsed_sub: sub_ext = 'ass'
                elif '.srt' in parsed_sub: sub_ext = 'srt'
                else: sub_ext = 'vtt'

                temp_timestamp = f"{int(time.time() * 1000)}_{zadanie.id.split('_')[-1]}"
                special_temp_video = os.path.join(katalog_temp, f"vid_{temp_timestamp}.mp4")
                special_temp_sub = os.path.join(katalog_temp, f"sub_{temp_timestamp}.{sub_ext}")
                special_final_video = os.path.join(katalog, f"{vid_title}.mp4" if is_burn else f"{vid_title}.mkv")
                sciezki_ytdlp = {'home': katalog_temp, 'temp': katalog_temp}
                szablon_wyjsciowy = os.path.basename(special_temp_video)
            else:
                szablon_wyjsciowy = f"{vid_title}.mp4"

        def progress_hook(d):
            nonlocal ostatni_plik_wyjsciowy
            if zadanie.cancel_requested.is_set():
                raise AnulowanoPrzezUzytkownika()
            if zadanie.pause_requested.is_set():
                raise WstrzymanoPrzezUzytkownika()

            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes') or 0
                if total_bytes > 0:
                    prog = min(1.0, downloaded / total_bytes)
                else:
                    p_raw = re.sub(r'[^0-9.]', '', d.get('_percent_str', '0'))
                    prog = min(1.0, float(p_raw) / 100.0) if p_raw else 0.0

                p_str = d.get('_percent_str', f'{prog * 100:.1f}%').strip()
                speed = d.get('_speed_str', '---').strip()
                eta = d.get('_eta_str', '---').strip()

                fn = d.get('filename')
                if fn:
                    ostatni_plik_wyjsciowy = fn
                    if not assigned_filename:
                        baza = os.path.splitext(os.path.basename(fn))[0]
                        baza = re.sub(r'\.f\d+$', '', baza)
                        if baza:
                            zadanie.title = baza

                with lock:
                    zadanie.status = "downloading"
                    zadanie.progress = prog
                    zadanie.status_text = f"{p_str} • {speed} • Pozostało: {eta}"
                    zadanie.touch()

            elif d['status'] == 'finished':
                fn = d.get('filename')
                if fn:
                    ostatni_plik_wyjsciowy = fn
                with lock:
                    zadanie.status = "processing"
                    zadanie.progress = 1.0
                    zadanie.status_text = "Scalanie i przenoszenie z folderu temp..."
                    zadanie.touch()

        def postprocessor_hook(d):
            nonlocal ostatni_plik_wyjsciowy
            if d.get('status') == 'finished':
                info_dict = d.get('info_dict') or {}
                fp = info_dict.get('filepath')
                if fp:
                    ostatni_plik_wyjsciowy = fp

        ydl_logger = YtdlpLogger()
        ydl_opts = bazowe_opcje_ytdlp()
        ydl_opts.update({
            'format': format_wideo if not jest_domena_retro else 'best',
            'paths': sciezki_ytdlp,
            'outtmpl': szablon_wyjsciowy,
            'noplaylist': True,
            'continuedl': True,
            'overwrites': bool(assigned_filename),
            'retries': 5,
            'fragment_retries': 5,
            'concurrent_fragment_downloads': 4,
            'ffmpeg_location': sciezka_ffmpeg,
            'progress_hooks': [progress_hook],
            'postprocessor_hooks': [postprocessor_hook],
            'logger': ydl_logger
        })

        if jest_domena_retro:
            ydl_opts['http_headers'] = {
                'Referer': org_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        else:
            postprocessors = []
            if "Tylko Audio" in typ_pobierania:
                postprocessors.append({'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'})
            else:
                ydl_opts['merge_output_format'] = 'mp4'
            if postprocessors:
                ydl_opts['postprocessors'] = postprocessors

        def zastosuj_wybor_uzytkownika(kontynuowac, wlasna_nazwa_wlaczona, nowa_nazwa_uzytkownika, licz_do_licznika_lokalnie, domyslny_tytul):
            nonlocal assigned_filename, assigned_number, custom_name_enabled, szablon_wyjsciowy
            if not kontynuowac:
                raise AnulowanoPrzezUzytkownika()

            licznik_zmieniony_lokalnie = False
            custom_name_enabled = bool(wlasna_nazwa_wlaczona)
            zadanie.custom_name_enabled = custom_name_enabled

            if not custom_name_enabled:
                if assigned_number is not None:
                    if zwolnij_numer_licznika(assigned_number):
                        licznik_zmieniony_lokalnie = True
                    assigned_number = None
                    zadanie.assigned_number = None
                assigned_filename = None
                zadanie.assigned_filename = None
                if domyslny_tytul:
                    zadanie.title = domyslny_tytul
                szablon_wyjsciowy = '%(title)s.%(ext)s'
                ydl_opts['outtmpl'] = szablon_wyjsciowy
                ydl_opts['overwrites'] = False
            else:
                if not licz_do_licznika_lokalnie and assigned_number is not None:
                    if zwolnij_numer_licznika(assigned_number):
                        licznik_zmieniony_lokalnie = True
                    assigned_number = None
                    zadanie.assigned_number = None
                elif licz_do_licznika_lokalnie and assigned_number is None:
                    assigned_number = zarezerwuj_kolejny_numer()
                    zadanie.assigned_number = assigned_number
                    licznik_zmieniony_lokalnie = True

                surowa = nowa_nazwa_uzytkownika or var_szablon_nazwy.get()
                if "%N%" in surowa:
                    if licz_do_licznika_lokalnie and assigned_number is not None:
                        surowa = surowa.replace("%N%", str(assigned_number))
                    else:
                        surowa = surowa.replace("%N%", "").strip()
                oczyszczona = re.sub(r'[\\/*?:"<>|]', "", surowa).strip()
                if oczyszczona:
                    assigned_filename = oczyszczona
                    zadanie.assigned_filename = oczyszczona
                    zadanie.title = oczyszczona
                    szablon_wyjsciowy = f"{assigned_filename}.%(ext)s"
                    ydl_opts['outtmpl'] = szablon_wyjsciowy
                    ydl_opts['overwrites'] = True

            if licznik_zmieniony_lokalnie:
                okno.after(0, odswiez_podglad_licznika)
                zapisz_ustawienia()

        def przygotuj_fallback_okru(wybrana_wys):
            nonlocal aktualny_url, szablon_wyjsciowy
            with lock:
                zadanie.status = "checking"
                zadanie.status_text = "Pobieranie informacji z OK.ru..."
                zadanie.touch()

            ok_info = pobierz_dane_okru(org_url)
            strumienie = ok_info["streams_by_height"]
            tytul_ok = ok_info["title"]
            docelowa_wys_ok = wybrana_wys

            if not assigned_filename:
                zadanie.title = tytul_ok

            if "Tylko Audio" not in typ_pobierania and docelowa_wys_ok is not None and strumienie:
                if docelowa_wys_ok not in strumienie:
                    alternatywa = wybierz_alternatywna_wysokosc(strumienie.keys(), docelowa_wys_ok)
                    with lock:
                        zadanie.status = "checking"
                        zadanie.status_text = f"Oczekuje na wybór jakości (brak {wybrana_jakosc})..."
                        zadanie.touch()

                    kontynuowac, wlasna_wl, nowa_nazwa_uzytkownika, licz_lokalnie = zapytaj_o_rozdzielczosc_i_nazwe(
                        org_url=org_url,
                        tytul_filmu=tytul_ok,
                        wybrana_res_str=wybrana_jakosc,
                        dostepne_wysokosci=set(strumienie.keys()),
                        alternatywna_wysokosc=alternatywa,
                        custom_name_enabled=custom_name_enabled,
                        domyslnie_licz_do_licznika=(assigned_number is not None),
                        aktualna_nazwa=assigned_filename
                    )
                    zastosuj_wybor_uzytkownika(kontynuowac, wlasna_wl, nowa_nazwa_uzytkownika, licz_lokalnie, tytul_ok)
                    docelowa_wys_ok = alternatywa

            if not assigned_filename:
                szablon_wyjsciowy = f"{tytul_ok}.%(ext)s"
                ydl_opts['outtmpl'] = szablon_wyjsciowy

            if strumienie:
                if docelowa_wys_ok and docelowa_wys_ok in strumienie:
                    aktualny_url = strumienie[docelowa_wys_ok]
                elif docelowa_wys_ok:
                    dost = sorted(strumienie.keys(), reverse=True)
                    niz = [h for h in dost if h <= docelowa_wys_ok]
                    wyb = max(niz) if niz else min(dost)
                    aktualny_url = strumienie[wyb]
                else:
                    aktualny_url = strumienie[max(strumienie.keys())]
                ydl_opts['format'] = 'best'
            elif ok_info["hls_url"]:
                aktualny_url = ok_info["hls_url"]
                ydl_opts['format'] = buduj_format_ytdlp(typ_pobierania, docelowa_wys_ok)

            ydl_opts['http_headers'] = {
                'Referer': 'https://ok.ru/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            }

        okru_przelaczono_na_fallback = False
        sprawdz_info = (
            not jest_domena_retro
            and "Tylko Audio" not in typ_pobierania
            and (docelowa_wysokosc is not None or sub_mode != "Brak")
        )

        if sprawdz_info:
            with lock:
                zadanie.status = "checking"
                zadanie.status_text = "Sprawdzanie dostępnych jakości i napisów..."
                zadanie.touch()

            try:
                info = pobierz_z_cache_lub_ytdlp(aktualny_url)
            except Exception as check_err:
                if jest_okru and "JSON object must be" in str(check_err):
                    przygotuj_fallback_okru(docelowa_wysokosc)
                    okru_przelaczono_na_fallback = True
                    info = None
                else:
                    raise

            if not okru_przelaczono_na_fallback and info:
                tytul_do_okna = info.get('title') or ""
                if tytul_do_okna and not assigned_filename:
                    zadanie.title = tytul_do_okna
                    zadanie.touch()

                if docelowa_wysokosc is not None:
                    dostepne_wysokosci = wyciagnij_dostepne_wysokosci(info)
                    if dostepne_wysokosci and docelowa_wysokosc not in dostepne_wysokosci:
                        alternatywna_wysokosc = wybierz_alternatywna_wysokosc(dostepne_wysokosci, docelowa_wysokosc)
                        with lock:
                            zadanie.status = "checking"
                            zadanie.status_text = f"Oczekuje na wybór jakości (brak {wybrana_jakosc})..."
                            zadanie.touch()

                        kontynuowac, wlasna_wl, nowa_nazwa_uzytkownika, licz_lokalnie = zapytaj_o_rozdzielczosc_i_nazwe(
                            org_url=org_url,
                            tytul_filmu=tytul_do_okna,
                            wybrana_res_str=wybrana_jakosc,
                            dostepne_wysokosci=dostepne_wysokosci,
                            alternatywna_wysokosc=alternatywna_wysokosc,
                            custom_name_enabled=custom_name_enabled,
                            domyslnie_licz_do_licznika=(assigned_number is not None),
                            aktualna_nazwa=assigned_filename
                        )
                        zastosuj_wybor_uzytkownika(kontynuowac, wlasna_wl, nowa_nazwa_uzytkownika, licz_lokalnie, tytul_do_okna)
                        ydl_opts['format'] = buduj_format_ytdlp(typ_pobierania, alternatywna_wysokosc)

                if sub_mode != "Brak":
                    dostepne_sub = wyciagnij_dostepne_napisy(info)
                    if dostepne_sub:
                        if sub_mode == "Wybierz z listy...":
                            with lock:
                                zadanie.status = "checking"
                                zadanie.status_text = "Oczekuje na wybór języków napisów..."
                                zadanie.touch()
                            sub_langs = zapytaj_o_jezyki_napisow(tytul_do_okna, dostepne_sub)
                        if sub_langs:
                            ydl_opts['writesubtitles'] = True
                            ydl_opts['writeautomaticsub'] = True
                            ydl_opts['subtitleslangs'] = sub_langs
                            ydl_opts['subtitlesformat'] = 'srt/vtt/best'
                            if not is_burn:
                                ydl_opts.setdefault('postprocessors', []).append({
                                    'key': 'FFmpegEmbedSubtitle',
                                    'already_have_subtitle': False
                                })

        with lock:
            zadanie.status = "downloading"
            zadanie.status_text = "Pobieranie części do folderu temp..."
            zadanie.touch()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([aktualny_url])
        except Exception as dl_err:
            if jest_okru and not okru_przelaczono_na_fallback and "JSON object must be" in str(dl_err):
                przygotuj_fallback_okru(docelowa_wysokosc)
                with lock:
                    zadanie.status = "downloading"
                    zadanie.status_text = "Pobieranie z OK.ru do folderu temp..."
                    zadanie.touch()
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([aktualny_url])
            else:
                szczegol = ydl_logger.last_error() or str(dl_err)
                raise Exception(szczegol)

        if special_sub_url and os.path.exists(special_temp_video):
            with lock:
                zadanie.status = "processing"
                zadanie.status_text = "Pobieranie napisów do temp..."
                zadanie.touch()

            try:
                req_sub = urllib.request.Request(special_sub_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Referer': org_url
                })
                sub_data = urllib.request.urlopen(req_sub, timeout=10).read()
                with open(special_temp_sub, 'wb') as f:
                    f.write(sub_data)

                with lock:
                    zadanie.status_text = "Wypalanie napisów (.mp4)..." if is_burn else "Wklejanie napisów i zapisywanie..."
                    zadanie.touch()

                c_flags = 0x08000000 if os.name == 'nt' else 0
                vid_base = os.path.basename(special_temp_video)
                sub_base = os.path.basename(special_temp_sub)
                temp_out_name = f"merged_{os.path.basename(special_final_video)}"

                if is_burn:
                    cmd = [exe_ffmpeg, '-y', '-i', vid_base, '-vf', f"subtitles={sub_base}", '-c:a', 'copy', temp_out_name]
                else:
                    sub_codec = 'ass' if sub_ext == 'ass' else 'srt'
                    cmd = [
                        exe_ffmpeg, '-y', '-i', vid_base, '-i', sub_base,
                        '-c', 'copy', '-c:s', sub_codec, '-metadata:s:s:0', 'language=pl', temp_out_name
                    ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=c_flags, cwd=katalog_temp)
                temp_out_full = os.path.join(katalog_temp, temp_out_name)
                if os.path.exists(temp_out_full):
                    shutil.move(temp_out_full, special_final_video)
                elif os.path.exists(special_temp_video) and not os.path.exists(special_final_video):
                    shutil.move(special_temp_video, special_final_video)
                ostatni_plik_wyjsciowy = special_final_video
            except Exception:
                if os.path.exists(special_temp_video) and not os.path.exists(special_final_video):
                    shutil.move(special_temp_video, special_final_video)
                ostatni_plik_wyjsciowy = special_final_video
        elif ostatni_plik_wyjsciowy:
            norm_temp = os.path.normcase(os.path.abspath(katalog_temp))
            norm_plik = os.path.normcase(os.path.abspath(ostatni_plik_wyjsciowy))
            if norm_plik.startswith(norm_temp + os.sep):
                docelowy_w_katalogu = os.path.join(katalog, os.path.basename(ostatni_plik_wyjsciowy))
                if os.path.exists(ostatni_plik_wyjsciowy) and not os.path.exists(docelowy_w_katalogu):
                    shutil.move(ostatni_plik_wyjsciowy, docelowy_w_katalogu)
                if os.path.exists(docelowy_w_katalogu):
                    ostatni_plik_wyjsciowy = docelowy_w_katalogu

        if is_burn and not jest_domena_retro and sub_langs and ostatni_plik_wyjsciowy:
            baza_bez_ext = os.path.splitext(ostatni_plik_wyjsciowy)[0]
            znalezione_srt = None
            for lang in sub_langs:
                kandydat = f"{baza_bez_ext}.{lang}.srt"
                if os.path.exists(kandydat):
                    znalezione_srt = kandydat
                    break
            if znalezione_srt and os.path.exists(f"{baza_bez_ext}.mp4"):
                with lock:
                    zadanie.status = "processing"
                    zadanie.status_text = "Wypalanie napisów w wideo (.mp4)..."
                    zadanie.touch()
                mp4_src = f"{baza_bez_ext}.mp4"
                temp_srt = os.path.join(katalog_temp, "burn_sub.srt")
                mp4_tmp = os.path.join(katalog_temp, "burn_out.mp4")
                shutil.copy2(znalezione_srt, temp_srt)
                c_flags = 0x08000000 if os.name == 'nt' else 0
                cmd = [
                    exe_ffmpeg, '-y', '-i', mp4_src,
                    '-vf', "subtitles=burn_sub.srt",
                    '-c:a', 'copy', mp4_tmp
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=c_flags, cwd=katalog_temp)
                if os.path.exists(mp4_tmp):
                    shutil.move(mp4_tmp, mp4_src)

        pobieranie_zakonczone_sukcesem = True

    except WstrzymanoPrzezUzytkownika:
        wstrzymano_zadanie = True
    except AnulowanoPrzezUzytkownika:
        pobieranie_zakonczone_sukcesem = False
    except Exception as e:
        pobieranie_zakonczone_sukcesem = False
        with lock:
            zadanie.status = "error"
            zadanie.status_text = f"Błąd: {str(e)[:95]}"
            zadanie.touch()
    finally:
        licznik_zmieniony = False
        with lock:
            aktywne_pobierania = max(0, aktywne_pobierania - 1)
            if is_burn:
                aktywne_wypalania = max(0, aktywne_wypalania - 1)

            if rozwinieto_playliste:
                wszystkie_zadania.pop(zadanie.id, None)
                if zadanie.id in kolejnosc_zadan:
                    kolejnosc_zadan.remove(zadanie.id)
                if assigned_number is not None:
                    licznik_zmieniony = zwolnij_numer_licznika(assigned_number)
                wyczysc_katalog_temp_zadania(zadanie.id)
                okno.after(0, lambda zid=zadanie.id: usun_karte_ui_bez_blokady(zid))
            elif wstrzymano_zadanie:
                zadanie.status = "paused"
                zadanie.status_text = "Wstrzymano (części zachowane w temp)"
                zadanie.touch()
            elif pobieranie_zakonczone_sukcesem:
                zadanie.status = "completed"
                zadanie.progress = 1.0
                zadanie.status_text = "Pobieranie zakończone pomyślnie"
                if ostatni_plik_wyjsciowy and not zadanie.output_path:
                    zadanie.output_path = ostatni_plik_wyjsciowy
                zadanie.touch()
                wyczysc_katalog_temp_zadania(zadanie.id)
                if assigned_number is not None:
                    zatwierdz_numer_licznika(assigned_number)
            else:
                if zadanie.status != "error":
                    zadanie.status = "cancelled"
                    zadanie.status_text = "Anulowano"
                    zadanie.touch()
                    wyczysc_katalog_temp_zadania(zadanie.id)
                if assigned_number is not None:
                    licznik_zmieniony = zwolnij_numer_licznika(assigned_number)

        if licznik_zmieniony:
            okno.after(0, odswiez_podglad_licznika)
            zapisz_ustawienia()

def usun_karte_ui_bez_blokady(zadanie_id):
    karta = karty_zadan_ui.pop(zadanie_id, None)
    if karta:
        try:
            karta["frame"].destroy()
        except Exception:
            pass

def akcja_wstrzymaj_wznow(zadanie_id):
    global w_kolejce
    with lock:
        zad = wszystkie_zadania.get(zadanie_id)
        if not zad:
            return
        if zad.status in ("queued", "checking", "downloading"):
            zad.pause_requested.set()
            if zad.status == "queued":
                zad.status = "paused"
                zad.status_text = "Wstrzymano"
            else:
                zad.status_text = "Wstrzymywanie..."
            zad.touch()
        elif zad.status == "paused":
            zad.pause_requested.clear()
            zad.cancel_requested.clear()
            zad.status = "queued"
            zad.status_text = "Oczekuje na wznowienie..."
            zad.touch()
            w_kolejce += 1
            kolejka_zadan.put(zad)

def akcja_anuluj_zadanie(zadanie_id):
    with lock:
        zad = wszystkie_zadania.get(zadanie_id)
        if not zad:
            return
        if zad.status in ("completed", "cancelled", "error"):
            return
        zad.cancel_requested.set()
        if zad.status == "paused":
            zad.status = "cancelled"
            zad.status_text = "Anulowano"
            zad.touch()
            wyczysc_katalog_temp_zadania(zadanie_id)
            if zad.assigned_number is not None:
                if zwolnij_numer_licznika(zad.assigned_number):
                    okno.after(0, odswiez_podglad_licznika)
                    zapisz_ustawienia()
        else:
            zad.status_text = "Anulowanie..."
            zad.touch()

def akcja_ponow_zadanie(zadanie_id):
    global w_kolejce
    with lock:
        zad = wszystkie_zadania.get(zadanie_id)
        if not zad or zad.status not in ("error", "cancelled"):
            return
        zad.cancel_requested.clear()
        zad.pause_requested.clear()
        zad.progress = 0.0
        zad.status = "queued"
        zad.status_text = "Oczekuje w kolejce (ponowiono)..."
        if zad.custom_name_enabled and "%N%" in var_szablon_nazwy.get() and zad.assigned_number is None:
            zad.assigned_number = zarezerwuj_kolejny_numer()
            zad.assigned_filename = zbuduj_bezpieczna_nazwe_pliku(var_szablon_nazwy.get(), zad.assigned_number, 0)
            zad.title = zad.assigned_filename
            okno.after(0, odswiez_podglad_licznika)
            zapisz_ustawienia()
        zad.touch()
        w_kolejce += 1
        kolejka_zadan.put(zad)

def akcja_usun_zadanie(zadanie_id):
    with lock:
        zad = wszystkie_zadania.get(zadanie_id)
        if not zad or zad.status in ("checking", "downloading", "processing"):
            return
        if zad.status == "queued":
            zad.cancel_requested.set()
        wszystkie_zadania.pop(zadanie_id, None)
        if zadanie_id in kolejnosc_zadan:
            kolejnosc_zadan.remove(zadanie_id)
    wyczysc_katalog_temp_zadania(zadanie_id)
    usun_karte_ui_bez_blokady(zadanie_id)

def wyczysc_zakonczone_zadania():
    do_usuniecia = []
    with lock:
        for z_id in list(kolejnosc_zadan):
            zad = wszystkie_zadania.get(z_id)
            if zad and zad.status in ("completed", "cancelled", "error"):
                do_usuniecia.append(z_id)
    for z_id in do_usuniecia:
        akcja_usun_zadanie(z_id)

def wyczysc_podglad_linku():
    global ostatni_podglad_url
    ostatni_podglad_url = ""
    lbl_podglad_miniatura.configure(image=None, text="Brak\nminiatury")
    lbl_podglad_miniatura.image = None
    lbl_podglad_tytul.configure(text="Wklej link powyżej, aby zobaczyć tytuł, miniaturę i dostępne jakości.")
    lbl_podglad_szczegoly.configure(text="")
    for w in ramka_chipow_jakosci.winfo_children():
        w.destroy()

def zaplanuj_podglad_linku(event=None):
    global podglad_timer_id
    if podglad_timer_id is not None:
        try:
            okno.after_cancel(podglad_timer_id)
        except Exception:
            pass
    podglad_timer_id = okno.after(550, uruchom_podglad_linku)

def uruchom_podglad_linku():
    global ostatni_podglad_url
    tekst = pole_linkow.get("1.0", "end").strip()
    urls = [u.strip() for u in tekst.replace('\n', ',').split(',') if u.strip()]
    pierwszy = urls[0] if urls else ""
    if not pierwszy or not re.match(r'^https?://', pierwszy, re.IGNORECASE):
        if not pierwszy:
            wyczysc_podglad_linku()
        return
    if pierwszy == ostatni_podglad_url:
        return

    ostatni_podglad_url = pierwszy
    lbl_podglad_tytul.configure(text="Pobieranie podglądu linku...")
    lbl_podglad_szczegoly.configure(text=pierwszy[:75])
    for w in ramka_chipow_jakosci.winfo_children():
        w.destroy()

    threading.Thread(target=pobierz_podglad_w_tle, args=(pierwszy,), daemon=True).start()

def wybierz_jakosc_z_podgladu(wysokosc):
    etykieta = f"{wysokosc}p"
    if etykieta in opcje_jakosci:
        combo_jakosc.set(etykieta)
        zapisz_ustawienia()

def pobierz_podglad_w_tle(url):
    try:
        tytul = ""
        opis_meta = ""
        thumb_url = None
        wysokosci = set()
        napisy_info = {}
        pl_url = wyciagnij_url_playlisty(url)

        if re.search(r'mega\.(?:co\.)?nz/', url, re.IGNORECASE):
            meta = pobierz_metadane_mega(url)
            tytul = meta["orig_name"]
            rozmiar_mb = meta["file_size"] / (1024 * 1024)
            opis_meta = f"Mega.nz • Rozmiar: {rozmiar_mb:.1f} MB"
        elif re.search(r'(?:ok\.ru|odnoklassniki\.ru)/', url, re.IGNORECASE):
            ok_data = pobierz_dane_okru(url)
            tytul = ok_data["title"]
            thumb_url = ok_data.get("thumbnail")
            wysokosci = set(ok_data.get("streams_by_height", {}).keys())
            czas = formatuj_czas_trwania(ok_data.get("duration"))
            opis_meta = "OK.ru" + (f" • Czas: {czas}" if czas else "")
        elif pl_url:
            opts = bazowe_opcje_ytdlp()
            opts['extract_flat'] = 'in_playlist'
            opts['noplaylist'] = False
            opts['playlistend'] = 300
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(pl_url, download=False)
            if info and info.get('entries'):
                wpisy = [e for e in info['entries'] if isinstance(e, dict)]
                tytul = info.get('title') or "Playlista"
                opis_meta = f"Playlista • Liczba odcinków: {len(wpisy)}"
                if wpisy and wpisy[0].get('thumbnails'):
                    thumb_url = wpisy[0]['thumbnails'][-1].get('url')
        else:
            info = pobierz_z_cache_lub_ytdlp(url)
            if info:
                tytul = info.get('title') or url
                thumb_url = info.get('thumbnail')
                wysokosci = wyciagnij_dostepne_wysokosci(info)
                napisy_info = wyciagnij_dostepne_napisy(info)
                czas = formatuj_czas_trwania(info.get('duration'))
                autor = info.get('uploader') or info.get('extractor_key') or ""
                czesci = [p for p in [autor, f"Czas: {czas}" if czas else ""] if p]
                if napisy_info:
                    czesci.append(f"Napisy: {', '.join(list(napisy_info.keys())[:5])}")
                opis_meta = " • ".join(czesci)

        ctk_img = None
        if thumb_url and HAS_PIL:
            try:
                req_img = urllib.request.Request(thumb_url, headers={"User-Agent": "Mozilla/5.0"})
                img_bytes = urllib.request.urlopen(req_img, timeout=8).read()
                pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(128, 72))
            except Exception:
                ctk_img = None

        def zastosuj_w_gui():
            if ostatni_podglad_url != url:
                return
            if ctk_img:
                lbl_podglad_miniatura.configure(image=ctk_img, text="")
                lbl_podglad_miniatura.image = ctk_img
            else:
                lbl_podglad_miniatura.configure(image=None, text="Podgląd")
                lbl_podglad_miniatura.image = None

            skrocony_tytul = tytul if len(tytul) <= 68 else tytul[:65] + "..."
            lbl_podglad_tytul.configure(text=skrocony_tytul or "Gotowy do pobrania")
            lbl_podglad_szczegoly.configure(text=opis_meta)

            for w in ramka_chipow_jakosci.winfo_children():
                w.destroy()

            if wysokosci:
                ctk.CTkLabel(
                    ramka_chipow_jakosci,
                    text="Dostępne:",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=("gray30", "gray75")
                ).pack(side="left", padx=(0, 6))

                for h in sorted(wysokosci, reverse=True):
                    ctk.CTkButton(
                        ramka_chipow_jakosci,
                        text=f"{h}p",
                        width=48,
                        height=22,
                        font=ctk.CTkFont(size=11, weight="bold"),
                        fg_color=("#2b7de9", "#1f538d"),
                        command=lambda wys=h: wybierz_jakosc_z_podgladu(wys)
                    ).pack(side="left", padx=2)

        okno.after(0, zastosuj_w_gui)
    except Exception:
        def blad_podgladu():
            if ostatni_podglad_url == url:
                lbl_podglad_tytul.configure(text="Gotowy do dodania do kolejki")
                lbl_podglad_szczegoly.configure(text=url[:75])
        okno.after(0, blad_podgladu)

def aktualizuj_wyglad_sekcji_nazwy():
    aktywne = bool(var_wlasna_nazwa.get())
    if aktywne:
        pole_wlasnej_nazwy.configure(
            state="normal",
            fg_color=("#F9F9FA", "#343638"),
            text_color=("#1a1a1a", "#DCE4EE"),
            border_color=("#979DA2", "#565B5E")
        )
        lbl_licznik_n.configure(text_color=("#1a1a1a", "#DCE4EE"))
        entry_licznik.configure(
            state="normal",
            fg_color=("#F9F9FA", "#343638"),
            text_color=("#1a1a1a", "#DCE4EE"),
            border_color=("#979DA2", "#565B5E")
        )
        btn_reset_licznik.configure(state="normal")
    else:
        pole_wlasnej_nazwy.configure(
            state="disabled",
            fg_color=("#E0E0E0", "#232323"),
            text_color=("gray55", "gray45"),
            border_color=("#CCCCCC", "#383838")
        )
        lbl_licznik_n.configure(text_color=("gray55", "gray45"))
        entry_licznik.configure(
            state="disabled",
            fg_color=("#E0E0E0", "#232323"),
            text_color=("gray55", "gray45"),
            border_color=("#CCCCCC", "#383838")
        )
        btn_reset_licznik.configure(state="disabled")

def przelacz_wlasna_nazwe():
    aktualizuj_wyglad_sekcji_nazwy()
    zapisz_ustawienia()

def przelacz_zawsze_na_wierzchu():
    okno.attributes('-topmost', bool(var_wierzch.get()))
    zapisz_ustawienia()

def przelacz_tryb_ciemny():
    ctk.set_appearance_mode("dark" if var_ciemny.get() else "light")
    aktualizuj_wyglad_sekcji_nazwy()
    zapisz_ustawienia()

def toggle_burn_checkbox():
    zapisz_ustawienia()

def zbuduj_lub_odswiez_karte_zadania(zad):
    kolory_statusu = {
        "queued": ("#546e7a", "#78909c"),
        "checking": ("#0277bd", "#29b6f6"),
        "downloading": ("#1565c0", "#42a5f5"),
        "processing": ("#ef6c00", "#ffa726"),
        "paused": ("#8e24aa", "#ba68c8"),
        "completed": ("#2e7d32", "#66bb6a"),
        "cancelled": ("#616161", "#9e9e9e"),
        "error": ("#c62828", "#ef5350")
    }
    nazwy_statusu = {
        "queued": "W KOLEJCE",
        "checking": "SPRAWDZANIE",
        "downloading": "POBIERANIE",
        "processing": "PRZETWARZANIE",
        "paused": "WSTRZYMANO",
        "completed": "UKOŃCZONO",
        "cancelled": "ANULOWANO",
        "error": "BŁĄD"
    }

    if zad.id not in karty_zadan_ui:
        karta = ctk.CTkFrame(lista_kolejki_scroll, corner_radius=8)
        karta.pack(fill="x", pady=4, padx=4)

        gora = ctk.CTkFrame(karta, fg_color="transparent")
        gora.pack(fill="x", padx=10, pady=(8, 2))

        badge = ctk.CTkLabel(
            gora,
            text="",
            font=ctk.CTkFont(size=10, weight="bold"),
            corner_radius=5,
            padx=6,
            pady=1,
            text_color="white"
        )
        badge.pack(side="left", padx=(0, 8))

        lbl_tytul = ctk.CTkLabel(gora, text="", font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
        lbl_tytul.pack(side="left", fill="x", expand=True)

        ramka_akcji = ctk.CTkFrame(gora, fg_color="transparent")
        ramka_akcji.pack(side="right")

        btn_pauza = ctk.CTkButton(ramka_akcji, text="⏸", width=30, height=24, font=ctk.CTkFont(size=12))
        btn_anuluj = ctk.CTkButton(ramka_akcji, text="✕", width=30, height=24, fg_color=("#c62828", "#8e0000"), hover_color="#b71c1c", font=ctk.CTkFont(size=12))
        btn_ponow = ctk.CTkButton(ramka_akcji, text="↻ Ponów", width=68, height=24, fg_color=("#1565c0", "#1976d2"), font=ctk.CTkFont(size=11, weight="bold"))
        btn_otworz = ctk.CTkButton(ramka_akcji, text="📂 Folder", width=72, height=24, fg_color=("#2e7d32", "#388e3c"), font=ctk.CTkFont(size=11, weight="bold"))
        btn_usun = ctk.CTkButton(ramka_akcji, text="🗑", width=30, height=24, fg_color=("#616161", "#424242"), font=ctk.CTkFont(size=12))

        pasek = ctk.CTkProgressBar(karta, height=8)
        pasek.pack(fill="x", padx=10, pady=(4, 4))
        pasek.set(0)

        lbl_info = ctk.CTkLabel(
            karta,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray75"),
            anchor="w"
        )
        lbl_info.pack(fill="x", padx=10, pady=(0, 8))

        karty_zadan_ui[zad.id] = {
            "frame": karta,
            "badge": badge,
            "lbl_tytul": lbl_tytul,
            "btn_pauza": btn_pauza,
            "btn_anuluj": btn_anuluj,
            "btn_ponow": btn_ponow,
            "btn_otworz": btn_otworz,
            "btn_usun": btn_usun,
            "pasek": pasek,
            "lbl_info": lbl_info,
            "last_version": -1
        }

    ui = karty_zadan_ui[zad.id]
    if ui["last_version"] == zad.version:
        return
    ui["last_version"] = zad.version

    ui["badge"].configure(
        text=nazwy_statusu.get(zad.status, zad.status.upper()),
        fg_color=kolory_statusu.get(zad.status, ("#546e7a", "#78909c"))
    )
    wyswietlany_tytul = zad.title if len(zad.title) <= 56 else zad.title[:53] + "..."
    ui["lbl_tytul"].configure(text=wyswietlany_tytul)
    ui["pasek"].set(max(0.0, min(1.0, zad.progress)))
    ui["lbl_info"].configure(text=zad.status_text)

    for b in (ui["btn_pauza"], ui["btn_anuluj"], ui["btn_ponow"], ui["btn_otworz"], ui["btn_usun"]):
        b.pack_forget()

    if zad.status in ("queued", "checking", "downloading"):
        ui["btn_pauza"].configure(text="⏸", command=lambda zid=zad.id: akcja_wstrzymaj_wznow(zid))
        ui["btn_pauza"].pack(side="left", padx=2)
        ui["btn_anuluj"].configure(command=lambda zid=zad.id: akcja_anuluj_zadanie(zid))
        ui["btn_anuluj"].pack(side="left", padx=2)
    elif zad.status == "paused":
        ui["btn_pauza"].configure(text="▶", command=lambda zid=zad.id: akcja_wstrzymaj_wznow(zid))
        ui["btn_pauza"].pack(side="left", padx=2)
        ui["btn_anuluj"].configure(command=lambda zid=zad.id: akcja_anuluj_zadanie(zid))
        ui["btn_anuluj"].pack(side="left", padx=2)
    elif zad.status in ("error", "cancelled"):
        ui["btn_ponow"].configure(command=lambda zid=zad.id: akcja_ponow_zadanie(zid))
        ui["btn_ponow"].pack(side="left", padx=2)
        ui["btn_usun"].configure(command=lambda zid=zad.id: akcja_usun_zadanie(zid))
        ui["btn_usun"].pack(side="left", padx=2)
    elif zad.status == "completed":
        ui["btn_otworz"].configure(command=lambda p=zad.output_path, k=zad.katalog: otworz_folder(p or k))
        ui["btn_otworz"].pack(side="left", padx=2)
        ui["btn_usun"].configure(command=lambda zid=zad.id: akcja_usun_zadanie(zid))
        ui["btn_usun"].pack(side="left", padx=2)

def aktualizuj_gui():
    with lock:
        akt = aktywne_pobierania
        kol = w_kolejce
        kopia_zadan = [wszystkie_zadania[zid] for zid in kolejnosc_zadan if zid in wszystkie_zadania]

    if akt == 0 and kol == 0:
        status_ogolny.configure(
            text="Gotowe do pracy • Brak aktywnych zadań",
            text_color=("#2e7d32", "#66bb6a")
        )
    else:
        status_ogolny.configure(
            text=f"Aktywne pobierania: {akt}  |  W kolejce: {kol}",
            text_color=("#1565c0", "#42a5f5")
        )

    for zad in kopia_zadan:
        zbuduj_lub_odswiez_karte_zadania(zad)

    okno.after(250, aktualizuj_gui)

# --- INICJALIZACJA GŁÓWNEGO OKNA CUSTOMTKINTER + DND ---
ctk.set_appearance_mode("dark" if zapisane_ustawienia["ciemny"] else "light")
ctk.set_default_color_theme("blue")

try:
    ctk.CTkToplevel._windows_set_titlebar_icon = lambda self: ustaw_ikone_okna(self)
except Exception:
    pass

class CdaDownloaderApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.TkdndVersion = TkinterDnD._require(self)
            self.has_dnd = True
        except Exception:
            self.has_dnd = False

    def _windows_set_titlebar_icon(self):
        ustaw_ikone_okna(self)

okno = CdaDownloaderApp()
okno.title(f"Cda Universal Advanced Downloader v{__version__}")
okno.geometry("760x820")
okno.minsize(720, 720)
ustaw_ikone_okna(okno)

# --- NAGŁÓWEK ---
ramka_naglowek = ctk.CTkFrame(okno, fg_color="transparent")
ramka_naglowek.pack(fill="x", padx=16, pady=(10, 4))

ctk.CTkLabel(
    ramka_naglowek,
    text=f"Cda Universal Downloader v{__version__}",
    font=ctk.CTkFont(size=18, weight="bold")
).pack(side="left")

var_wierzch = tk.BooleanVar(value=zapisane_ustawienia["wierzch"])
ctk.CTkSwitch(
    ramka_naglowek,
    text="Na wierzchu",
    variable=var_wierzch,
    command=przelacz_zawsze_na_wierzchu,
    font=ctk.CTkFont(size=12, weight="bold")
).pack(side="right", padx=(12, 0))

var_ciemny = tk.BooleanVar(value=zapisane_ustawienia["ciemny"])
ctk.CTkSwitch(
    ramka_naglowek,
    text="Tryb ciemny",
    variable=var_ciemny,
    command=przelacz_tryb_ciemny,
    font=ctk.CTkFont(size=12, weight="bold")
).pack(side="right")

# --- KARTA 1: LINKI I PODGLĄD ---
karta_linki = ctk.CTkFrame(okno, corner_radius=12)
karta_linki.pack(fill="x", padx=16, pady=5)

gora_linkow = ctk.CTkFrame(karta_linki, fg_color="transparent")
gora_linkow.pack(fill="x", padx=14, pady=(8, 4))

ctk.CTkLabel(
    gora_linkow,
    text="Wklej lub przeciągnij linki (CDA, YouTube, Mega.nz, OK.ru, TikTok, playlisty):",
    font=ctk.CTkFont(size=13, weight="bold")
).pack(side="left")

ctk.CTkButton(gora_linkow, text="Wyczyść", width=75, height=26, fg_color=("#757575", "#424242"), command=wyczysc_linki).pack(side="right", padx=(6, 0))
ctk.CTkButton(gora_linkow, text="Wklej", width=75, height=26, command=wklej_link).pack(side="right")

pole_linkow = ctk.CTkTextbox(karta_linki, height=62, font=ctk.CTkFont(size=12), corner_radius=8)
pole_linkow.pack(fill="x", padx=14, pady=(2, 8))
pole_linkow.bind("<KeyRelease>", zaplanuj_podglad_linku)
pole_linkow.bind("<<Paste>>", zaplanuj_podglad_linku)
if okno.has_dnd:
    try:
        pole_linkow._textbox.drop_target_register(DND_TEXT)
        pole_linkow._textbox.dnd_bind('<<Drop>>', obsluga_drop)
    except Exception:
        pass

# Karta podglądu miniatury i jakości
ramka_podgladu = ctk.CTkFrame(karta_linki, corner_radius=8)
ramka_podgladu.pack(fill="x", padx=14, pady=(0, 10))

lbl_podglad_miniatura = ctk.CTkLabel(
    ramka_podgladu,
    text="Brak\nminiatury",
    width=128,
    height=72,
    fg_color=("gray82", "gray20"),
    corner_radius=6,
    font=ctk.CTkFont(size=11)
)
lbl_podglad_miniatura.pack(side="left", padx=8, pady=8)

ramka_podglad_tekst = ctk.CTkFrame(ramka_podgladu, fg_color="transparent")
ramka_podglad_tekst.pack(side="left", fill="both", expand=True, padx=(4, 10), pady=8)

lbl_podglad_tytul = ctk.CTkLabel(
    ramka_podglad_tekst,
    text="Wklej link powyżej, aby zobaczyć tytuł, miniaturę i dostępne jakości.",
    font=ctk.CTkFont(size=12, weight="bold"),
    anchor="w"
)
lbl_podglad_tytul.pack(fill="x")

lbl_podglad_szczegoly = ctk.CTkLabel(
    ramka_podglad_tekst,
    text="",
    font=ctk.CTkFont(size=11),
    text_color=("gray35", "gray70"),
    anchor="w"
)
lbl_podglad_szczegoly.pack(fill="x", pady=(2, 4))

ramka_chipow_jakosci = ctk.CTkFrame(ramka_podglad_tekst, fg_color="transparent", height=24)
ramka_chipow_jakosci.pack(fill="x")

# --- KARTA 2: USTAWIENIA POBIERANIA I ZAPISU ---
karta_opcje = ctk.CTkFrame(okno, corner_radius=12)
karta_opcje.pack(fill="x", padx=16, pady=5)

siatka_opcji = ctk.CTkFrame(karta_opcje, fg_color="transparent")
siatka_opcji.pack(fill="x", padx=14, pady=(10, 4))
siatka_opcji.grid_columnconfigure(1, weight=1)
siatka_opcji.grid_columnconfigure(3, weight=1)

ctk.CTkLabel(siatka_opcji, text="Format:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=4)
opcje_formatu = ["Wideo + Audio (MP4)", "Tylko Audio (MP3)", "Tylko Wideo (bez dźwięku)"]
combo_format = ctk.CTkComboBox(siatka_opcji, values=opcje_formatu, state="readonly", width=215, command=zapisz_ustawienia)
combo_format.set(zapisane_ustawienia["format"] if zapisane_ustawienia["format"] in opcje_formatu else opcje_formatu[0])
combo_format.grid(row=0, column=1, sticky="w", padx=(8, 16), pady=4)

ctk.CTkLabel(siatka_opcji, text="Maksymalnie naraz:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, sticky="w", pady=4)
opcje_limitu = ["1", "2", "3", "4", "5"]
combo_limit = ctk.CTkComboBox(siatka_opcji, values=opcje_limitu, state="readonly", width=90, command=zapisz_ustawienia)
combo_limit.set(str(zapisane_ustawienia["limit"]) if str(zapisane_ustawienia["limit"]) in opcje_limitu else "3")
combo_limit.grid(row=0, column=3, sticky="w", padx=(8, 0), pady=4)

ctk.CTkLabel(siatka_opcji, text="Jakość wideo:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, sticky="w", pady=4)
opcje_jakosci = ["Najlepsza dostępna", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
combo_jakosc = ctk.CTkComboBox(siatka_opcji, values=opcje_jakosci, state="readonly", width=215, command=zapisz_ustawienia)
combo_jakosc.set(zapisane_ustawienia["jakosc"] if zapisane_ustawienia["jakosc"] in opcje_jakosci else opcje_jakosci[0])
combo_jakosc.grid(row=1, column=1, sticky="w", padx=(8, 16), pady=4)

var_retro = tk.BooleanVar(value=zapisane_ustawienia["retro"])
ctk.CTkCheckBox(
    siatka_opcji,
    text="Wideo + Napisy (Retro xd)",
    variable=var_retro,
    font=ctk.CTkFont(size=12, weight="bold"),
    command=toggle_burn_checkbox
).grid(row=1, column=2, columnspan=2, sticky="w", pady=4)

ctk.CTkLabel(siatka_opcji, text="Napisy (YT / inne):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", pady=4)
opcje_napisow = ["Brak", "Polski (pl)", "Angielski (en)", "Polski + Angielski (pl, en)", "Wybierz z listy..."]
combo_napisy = ctk.CTkComboBox(siatka_opcji, values=opcje_napisow, state="readonly", width=215, command=zapisz_ustawienia)
combo_napisy.set(zapisane_ustawienia["napisy_tryb"] if zapisane_ustawienia["napisy_tryb"] in opcje_napisow else "Brak")
combo_napisy.grid(row=2, column=1, sticky="w", padx=(8, 16), pady=4)

var_burn_subs = tk.BooleanVar(value=zapisane_ustawienia["burn_subs"])
ctk.CTkCheckBox(
    siatka_opcji,
    text="Wypal napisy na stałe (.mp4)",
    variable=var_burn_subs,
    font=ctk.CTkFont(size=12),
    command=zapisz_ustawienia
).grid(row=2, column=2, columnspan=2, sticky="w", pady=4)

# Sekcja "Zapisz jako:"
ramka_nazwy = ctk.CTkFrame(karta_opcje, fg_color="transparent")
ramka_nazwy.pack(fill="x", padx=14, pady=(4, 6))

var_wlasna_nazwa = tk.BooleanVar(value=zapisane_ustawienia["wlasna_nazwa"])
ctk.CTkCheckBox(
    ramka_nazwy,
    text="Zapisz jako:",
    variable=var_wlasna_nazwa,
    font=ctk.CTkFont(size=12, weight="bold"),
    command=przelacz_wlasna_nazwe
).pack(side="left")

var_szablon_nazwy = tk.StringVar(value=zapisane_ustawienia["szablon_nazwy"])
var_szablon_nazwy.trace_add("write", zapisz_ustawienia)
pole_wlasnej_nazwy = ctk.CTkEntry(ramka_nazwy, textvariable=var_szablon_nazwy, height=28)
pole_wlasnej_nazwy.pack(side="left", fill="x", expand=True, padx=(8, 10))

lbl_licznik_n = ctk.CTkLabel(ramka_nazwy, text="%N%:", font=ctk.CTkFont(size=12, weight="bold"))
lbl_licznik_n.pack(side="left")

var_licznik_input = tk.StringVar(value=str(licznik_filmow))
var_licznik_input.trace_add("write", on_licznik_zmiana)
vcmd_cyfry = (okno.register(tylko_cyfry), '%P')
entry_licznik = ctk.CTkEntry(
    ramka_nazwy,
    textvariable=var_licznik_input,
    width=52,
    height=28,
    justify="center",
    font=ctk.CTkFont(size=12, weight="bold"),
    validate="key",
    validatecommand=vcmd_cyfry
)
entry_licznik.pack(side="left", padx=(4, 6))
entry_licznik.bind("<FocusOut>", on_licznik_focus_out)
entry_licznik.bind("<Return>", lambda e: okno.focus())

btn_reset_licznik = ctk.CTkButton(ramka_nazwy, text="Resetuj", width=65, height=28, fg_color=("#757575", "#424242"), command=resetuj_licznik)
btn_reset_licznik.pack(side="left")

# Sekcja Folder zapisu
ramka_sciezki = ctk.CTkFrame(karta_opcje, fg_color="transparent")
ramka_sciezki.pack(fill="x", padx=14, pady=(2, 8))

ctk.CTkLabel(ramka_sciezki, text="Folder zapisu:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
sciezka_zapisu = tk.StringVar(value=zapisane_ustawienia["katalog"])
pole_sciezki = ctk.CTkEntry(ramka_sciezki, textvariable=sciezka_zapisu, state="readonly", height=28)
pole_sciezki.pack(side="left", fill="x", expand=True, padx=(8, 8))

ctk.CTkButton(ramka_sciezki, text="Zmień", width=70, height=28, command=wybierz_folder).pack(side="left", padx=(0, 6))
ctk.CTkButton(ramka_sciezki, text="Otwórz", width=70, height=28, fg_color=("#757575", "#424242"), command=otworz_folder).pack(side="left")

przycisk_pobierz = ctk.CTkButton(
    karta_opcje,
    text="+ Dodaj do kolejki",
    font=ctk.CTkFont(size=14, weight="bold"),
    fg_color="#2e7d32",
    hover_color="#1b5e20",
    height=36,
    command=dodaj_do_kolejki
)
przycisk_pobierz.pack(fill="x", padx=14, pady=(0, 10))

# --- KARTA 3: INTERAKTYWNA KOLEJKA ZADAŃ ---
karta_kolejka = ctk.CTkFrame(okno, corner_radius=12)
karta_kolejka.pack(fill="both", expand=True, padx=16, pady=(5, 12))

naglowek_kolejki = ctk.CTkFrame(karta_kolejka, fg_color="transparent")
naglowek_kolejki.pack(fill="x", padx=14, pady=(8, 4))

status_ogolny = ctk.CTkLabel(
    naglowek_kolejki,
    text="Gotowe do pracy • Brak aktywnych zadań",
    font=ctk.CTkFont(size=13, weight="bold"),
    text_color=("#2e7d32", "#66bb6a")
)
status_ogolny.pack(side="left")

ctk.CTkButton(
    naglowek_kolejki,
    text="Wyczyść zakończone",
    width=135,
    height=26,
    fg_color=("#757575", "#424242"),
    font=ctk.CTkFont(size=11, weight="bold"),
    command=wyczysc_zakonczone_zadania
).pack(side="right")

lista_kolejki_scroll = ctk.CTkScrollableFrame(karta_kolejka, corner_radius=8)
lista_kolejki_scroll.pack(fill="both", expand=True, padx=12, pady=(4, 10))

wyczysc_stare_katalogi_temp()
aktualizuj_wyglad_sekcji_nazwy()
przelacz_zawsze_na_wierzchu()
inicjalizacja_zakonczona = True
zapisz_ustawienia()

def przy_zamknieciu():
    zapisz_ustawienia()
    okno.destroy()

okno.protocol("WM_DELETE_WINDOW", przy_zamknieciu)
okno.after(250, aktualizuj_gui)

threading.Thread(target=sprawdz_i_utworz_skrot_start_menu, daemon=True).start()
threading.Thread(target=zarzadca_kolejki, daemon=True).start()

okno.mainloop()