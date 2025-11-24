import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import pyotp
import time
import json
import re
import os
import sys
import cv2
import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
import platform
import subprocess
import uuid
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    print("ERROR: SECRET_KEY not found in environment variables.")
    print("Please ensure .env file exists with SECRET_KEY defined.")
    sys.exit(1)

# 実行ファイルの場所を取得
if getattr(sys, 'frozen', False):
    # PyInstallerなどでパッケージ化された場合
    application_path = os.path.dirname(sys.executable)
else:
    # 通常のPythonスクリプトの場合
    application_path = os.path.dirname(os.path.abspath(__file__))

# 設定クラス
class Config:
    """アプリケーション設定を管理するクラス"""
    # ファイルパス
    PIN_FILE = os.path.join(application_path, 'MagicalFlyingAlpaca-Pin.dat')
    ACCOUNTS_FILE = os.path.join(application_path, 'MagicalFlyingAlpaca-Accounts.json')
    
    # TOTP設定
    TOTP_PERIOD = 30  # 秒
    
    # 暗号化設定
    PBKDF2_ITERATIONS = 100000
    SALT_LENGTH = 16
    
    # PIN設定
    MIN_PIN_LENGTH = 8
    
    # エクスポートキー設定
    MIN_EXPORT_KEY_LENGTH = 16
    
    # UI設定
    MAIN_WINDOW_SIZE = "400x350"

def get_hardware_id():
    system = platform.system()
    if system == "Windows":
        try:
            result = subprocess.check_output("wmic baseboard get serialnumber").decode().split("\n")[1].strip()
            return result if result else 'FFFFFFFF'
        except:
            pass
    elif system == "Darwin":  # macOS
        try:
            result = subprocess.check_output(["system_profiler", "SPHardwareDataType"]).decode()
            for line in result.split("\n"):
                if "Hardware UUID" in line:
                    return line.split(":")[1].strip()
        except:
            pass
    
    # Windows/macOSで取得できない場合、またはその他のOSの場合
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
        return mac if mac != '00:00:00:00:00:00' else 'FFFFFFFF'
    except:
        return 'FFFFFFFF'

def hash_pin(pin):
    """PINと秘密鍵とハードウェアIDを組み合わせてハッシュ化"""
    hardware_id = get_hardware_id()
    return hashlib.sha256((pin + SECRET_KEY + hardware_id).encode()).hexdigest()

def derive_key(pin, salt):
    """PINとソルトから暗号化キーを導出"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    hardware_id = get_hardware_id()
    key = base64.urlsafe_b64encode(kdf.derive((pin + SECRET_KEY + hardware_id).encode()))
    return key

# TOTPコードを生成する関数
def generate_totp(secret_key):
    totp = pyotp.TOTP(secret_key)
    return totp.now()

# アカウント情報をJSONファイルからロードする関数
def load_accounts():
    if os.path.exists(Config.ACCOUNTS_FILE):
        with open(Config.ACCOUNTS_FILE, 'r') as f:
            return json.load(f)
    return {}

# アカウント情報をJSONファイルに保存する関数
def save_accounts(accounts):
    with open(Config.ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f)

# PINダイアログクラス
class PinDialog(tk.Toplevel):
    def __init__(self, parent, title, initial):
        super().__init__(parent)
        self.title(title)
        self.pin = tk.StringVar()
        self.result = None
        self.initial = initial

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20 20 20 20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Enter PIN:", font=('Helvetica', 14)).grid(row=0, column=0, pady=10)
        if self.initial == True:    # 初回のPIN設定要件表示用
            ttk.Label(frame, text="Choose a memorable 8+ digit PIN.", font=('Helvetica', 14)).grid(row=1, column=0, pady=10)
            self.geometry("350x280")
        else:
            ttk.Label(frame, text="こんにちは", font=('Helvetica', 14)).grid(row=1, column=0, pady=10)
            self.geometry("270x260")

        pin_entry = ttk.Entry(frame, textvariable=self.pin, show="*", font=('Helvetica', 20), width=15)
        pin_entry.grid(row=2, column=0, pady=10)
        pin_entry.focus()

        # Enterキーを押したときにもok関数を呼び出す
        pin_entry.bind('<Return>', lambda event: self.ok())

        ok_button = ttk.Button(frame, text="OK", command=self.ok, width=20, )
        ok_button.grid(row=3, column=0, pady=10)

    def ok(self):
        pin = self.pin.get()
        if len(pin) >= Config.MIN_PIN_LENGTH and pin.isdigit():
            self.result = pin
            self.destroy()
        else:
            messagebox.showerror("Invalid PIN", f"Please enter at least {Config.MIN_PIN_LENGTH} number.")
            self.pin.set("")  # PINをクリア

def get_pin(parent, title, initial):
    dialog = PinDialog(parent, title,initial)
    dialog.wait_window()
    return dialog.result

# 新しいアカウント追加ダイアログクラス
class AddAccountDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Account")
        self.account_name = tk.StringVar()
        self.secret_key = tk.StringVar()
        self.result = None

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20 20 20 20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Account Name:", font=('Helvetica', 12)).grid(row=0, column=0, pady=5, sticky="w")
        ttk.Entry(frame, textvariable=self.account_name, font=('Helvetica', 12), width=30).grid(row=1, column=0, pady=5)

        ttk.Label(frame, text="Secret Key:", font=('Helvetica', 12)).grid(row=2, column=0, pady=5, sticky="w")
        secret_key_entry = ttk.Entry(frame, textvariable=self.secret_key, font=('Helvetica', 12), width=30)
        secret_key_entry.grid(row=3, column=0, pady=5)

        ttk.Button(frame, text="Select QR Code", command=self.scan_qr_code).grid(row=4, column=0, pady=5)
        ttk.Button(frame, text="Add", command=self.ok, width=20).grid(row=5, column=0, pady=10)

        self.geometry("315x270")

    def scan_qr_code(self):
        initial_dir = os.path.expanduser("~/Downloads")  # ダウンロードフォルダを初期ディレクトリとして設定
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select QR Code Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if file_path:
            result = self.read_qr_code(file_path)
            if result['success']:
                self.secret_key.set(result['secret_key'])
                if 'issuer' in result:
                    self.account_name.set(result['issuer'])
                # ダイアログを最前面に持ってくる
                self.lift()
                self.focus_force()
            else:
                tk.messagebox.showerror("Error", result['message'])
                # エラーダイアログの後にもダイアログを最前面に
                self.after(100, self.lift)
                self.after(100, self.focus_force)

    def read_qr_code(self, image_path):
        try:
            # ファイルパスをバイト列として読み込む
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # NumPy配列に変換
            nparr = np.frombuffer(image_data, np.uint8)

            # cv2.imdecodを使用して画像をデコード
            img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

            if img is None:
                return {'success': False, 'message': f"Failed to read image file: {os.path.basename(image_path)}"}

            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)
            if bbox is not None:
                secret_match = re.search(r'secret=([A-Z2-7]+)', data)
                issuer_match = re.search(r'issuer=([^&]+)', data)
                if secret_match:
                    result = {'success': True, 'secret_key': secret_match.group(1)}
                    if issuer_match:
                        result['issuer'] = issuer_match.group(1)
                    return result
            return {'success': False, 'message': "Failed to extract information from QR code."}
        except Exception as e:
            return {'success': False, 'message': f"Error occurred while reading QR code: {str(e)}"}

    def ok(self):
        self.result = (self.account_name.get(), self.secret_key.get())
        self.destroy()

class ImportKeyDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Enter Import Key")
        self.password = tk.StringVar()
        self.result = None

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20 20 20 20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Enter your export key", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, pady=5)
        ttk.Label(frame, text="Enter the key you used when exporting your data.", 
                 font=('Helvetica', 10)).grid(row=1, column=0, pady=5)
        
        password_entry = ttk.Entry(frame, textvariable=self.password, show="*", font=('Helvetica', 12), width=20)
        password_entry.grid(row=2, column=0, pady=15)
        password_entry.focus()

        # ヒント
        ttk.Label(frame, text="The key should be at least 16 characters long and include\nletters, numbers, and special characters.", 
                 font=('Helvetica', 9), foreground='gray').grid(row=3, column=0, pady=5)

        ok_button = ttk.Button(frame, text="Unlock Data", command=self.ok)
        ok_button.grid(row=4, column=0, pady=10)
        
        # Enterキーを押したときにもok関数を呼び出す
        password_entry.bind('<Return>', lambda event: self.ok())
        
        # ダイアログサイズ調整
        self.geometry("350x250")

    def ok(self):
        key = self.password.get()
        if len(key) > 0:  # 最低限の検証
            self.result = key
            self.destroy()
        else:
            messagebox.showerror("Invalid Key", "Please enter your export key.")
            self.password.set("")  # Reset the input
            # エラーダイアログの後にもダイアログを最前面に
            self.after(100, self.lift)
            self.after(100, self.focus_force)

# エクスポート用キーを取得するダイアログ
class ExportKeyDialog(tk.Toplevel):
    # クラスレベルで正規表現パターンをコンパイル（再利用のため）
    LETTER_PATTERN = re.compile(r'[a-zA-Z]')
    NUMBER_PATTERN = re.compile(r'\d')
    SPECIAL_PATTERN = re.compile(r'[!@#$%^&*(),.?":{}|<>]')
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Enter Export Key")
        self.password = tk.StringVar()
        self.password.trace_add("write", self.check_password_strength)
        self.result = None

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20 20 20 20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Enter Export Key (16+ characters)", font=('Helvetica', 12)).grid(row=0, column=0, pady=5)
        ttk.Label(frame, text="Must include letters, numbers, and special characters", font=('Helvetica', 10)).grid(row=1, column=0, pady=5)
        
        password_entry = ttk.Entry(frame, textvariable=self.password, show="*", font=('Helvetica', 12), width=20)
        password_entry.grid(row=2, column=0, pady=5)
        password_entry.focus()

        # パスワード強度表示用のプログレスバーとラベル
        self.strength_var = tk.StringVar(value="Password strength: Weak")
        self.strength_label = ttk.Label(frame, textvariable=self.strength_var, font=('Helvetica', 10))
        self.strength_label.grid(row=3, column=0, pady=5, sticky="w")
        
        self.strength_bar = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate")
        self.strength_bar.grid(row=4, column=0, pady=5)
        
        # 要件チェックリスト
        self.requirements_frame = ttk.Frame(frame)
        self.requirements_frame.grid(row=5, column=0, pady=5, sticky="w")
        
        self.length_var = tk.StringVar(value="❌ 16+ characters")
        self.letters_var = tk.StringVar(value="❌ Contains letters")
        self.numbers_var = tk.StringVar(value="❌ Contains numbers")
        self.special_var = tk.StringVar(value="❌ Contains special characters")
        
        ttk.Label(self.requirements_frame, textvariable=self.length_var).grid(row=0, column=0, sticky="w")
        ttk.Label(self.requirements_frame, textvariable=self.letters_var).grid(row=1, column=0, sticky="w")
        ttk.Label(self.requirements_frame, textvariable=self.numbers_var).grid(row=2, column=0, sticky="w")
        ttk.Label(self.requirements_frame, textvariable=self.special_var).grid(row=3, column=0, sticky="w")

        self.ok_button = ttk.Button(frame, text="OK", command=self.ok)
        self.ok_button.grid(row=6, column=0, pady=10)
        self.ok_button["state"] = "disabled"  # 初期状態では無効化
        
        # Enterキーを押したときにもok関数を呼び出す
        password_entry.bind('<Return>', lambda event: self.try_ok())
        
        # ダイアログサイズ調整
        self.geometry("350x350")

    def check_password_strength(self, *args):
        """パスワードの強度をリアルタイムでチェックする"""
        password = self.password.get()
        
        # 各要件のチェック
        has_length = len(password) >= Config.MIN_EXPORT_KEY_LENGTH
        has_letters = bool(self.LETTER_PATTERN.search(password))
        has_numbers = bool(self.NUMBER_PATTERN.search(password))
        has_special = bool(self.SPECIAL_PATTERN.search(password))
        
        # 要件表示の更新
        self.length_var.set(f"{'✅' if has_length else '❌'} 16+ characters")
        self.letters_var.set(f"{'✅' if has_letters else '❌'} Contains letters")
        self.numbers_var.set(f"{'✅' if has_numbers else '❌'} Contains numbers")
        self.special_var.set(f"{'✅' if has_special else '❌'} Contains special characters")
        
        # 強度計算 (0-100)
        strength = 0
        if has_length: strength += 25
        if has_letters: strength += 25
        if has_numbers: strength += 25
        if has_special: strength += 25
        
        # 強度バーとラベルの更新
        self.strength_bar["value"] = strength
        
        if strength < 50:
            strength_text = "Weak"
            self.strength_label.config(foreground="red")
        elif strength < 100:
            strength_text = "Medium"
            self.strength_label.config(foreground="orange")
        else:
            strength_text = "Strong"
            self.strength_label.config(foreground="green")
            
        self.strength_var.set(f"Password strength: {strength_text}")
        
        # OKボタンの有効/無効を設定
        if has_length and has_letters and has_numbers and has_special:
            self.ok_button["state"] = "normal"
        else:
            self.ok_button["state"] = "disabled"

    def try_ok(self):
        """Enterキーが押されたときに、要件を満たしていればOKを実行"""
        if self.ok_button["state"] == "normal":
            self.ok()

    def ok(self):
        self.result = self.password.get()
        self.destroy()

# メインアプリケーションクラス
class MFAApp:
    def __init__(self, master, encryption_key):
        self.master = master
        self.master.title("Magical Flying Alpaca")
        self.master.configure(bg='#f0f0f0')  # 背景色を設定
        self.encryption_key = encryption_key
        self.accounts = load_accounts()
        self.current_account = None
        self.current_code = ""
        self.last_totp_period = -1  # 最後に更新したTOTP周期を追跡

        self.create_widgets()
        self.bind_keys()

    def create_widgets(self):
        # メインフレームを作成
        main_frame = ttk.Frame(self.master, padding="20 20 20 20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # スタイルを設定
        style = ttk.Style()
        style.theme_use('clam')  # または 'alt', 'default', 'classic' などおこのみで
        style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 12))
        style.configure('TButton', font=('Helvetica', 12))
        style.configure('TCombobox', font=('Helvetica', 12))

        # ここにカスタムスタイルを追加
        style.layout('Custom.TCombobox', [
            ('Combobox.downarrow', {'side': 'right', 'sticky': 'ns'}),
            ('Combobox.field', {'side': 'left', 'sticky': 'nswe'})
        ])
        style.configure('Custom.TCombobox', arrowsize=200)  # 矢印サイズを大きくする

        # アカウント選択用のコンボボックスを作成
        ttk.Label(main_frame, text="Select Account:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.account_combo = ttk.Combobox(main_frame, values=list(self.accounts.keys()), width=30, height=25)
        self.account_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.account_combo.bind("<<ComboboxSelected>>", self.on_account_select)
        
        if self.accounts:
            self.account_combo.set(list(self.accounts.keys())[0])
            self.current_account = self.account_combo.get()

        # TOTPコード表示用のラベルを作成
        self.code_label = ttk.Label(main_frame, text="", font=("Helvetica", 40))
        self.code_label.grid(row=1, column=0, columnspan=2, padx=5, pady=20)

        # 残り時間表示用のラベルを作成
        self.time_label = ttk.Label(main_frame, text="")
        self.time_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # コードをコピーするボタンを作成
        self.copy_button = ttk.Button(main_frame, text="Copy Code ( Click or Press Enter Key )", command=self.copy_code)
        self.copy_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # アカウントの追加・削除ボタンを作成
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Add Account", command=self.add_account).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Remove Account", command=self.remove_account).grid(row=0, column=1, padx=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Export", command=self.data_export).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Import", command=self.data_inport).grid(row=0, column=1, padx=5)

        self.master.geometry(Config.MAIN_WINDOW_SIZE)

        self.update_code()

    # アカウントが選択されたときのコールバック
    def on_account_select(self, event):
        self.current_account = self.account_combo.get()
        self.last_totp_period = -1  # 更新

    def bind_keys(self):
        # Enterキーを押したときにcopy_codeメソッドを呼び出す
        self.master.bind('<Return>', lambda event: self.copy_code())

    # コードをクリップボードにコピーするメソッド
    def copy_code(self):
        if self.current_code:
            self.master.clipboard_clear()
            self.master.clipboard_append(self.current_code)
            self.code_label.config(text="Copied!")
        else:
            messagebox.showwarning("No Code", "No code available to copy.")

    # 新しいアカウントを追加するメソッド
    def add_account(self):
        dialog = AddAccountDialog(self.master)
        dialog.wait_window()
        if dialog.result:
            account_name, secret_key = dialog.result
            if account_name and account_name not in self.accounts and secret_key:
                encrypted_secret = self.encrypt_secret(secret_key)
                self.accounts[account_name] = encrypted_secret
                save_accounts(self.accounts)
                self.account_combo['values'] = list(self.accounts.keys())
                self.account_combo.set(account_name)
                self.current_account = account_name

    # アカウントを削除するメソッド
    def remove_account(self):
        if self.current_account:
            if messagebox.askyesno("Remove Account", f"Are you sure you want to remove {self.current_account}?"):
                del self.accounts[self.current_account]
                save_accounts(self.accounts)
                self.account_combo['values'] = list(self.accounts.keys())
                if self.accounts:
                    self.account_combo.set(list(self.accounts.keys())[0])
                    self.current_account = self.account_combo.get()
                else:
                    self.account_combo.set('')
                    self.current_account = None

    # エクスポートメソッド用アカウント群の値のディクリプト
    def decrypt_accounts(self):
        decrypted_accounts = {}
        for key, value in self.accounts.items():
            decrypted_value = self.decrypt_secret(value)
            decrypted_accounts[key] = decrypted_value
        return decrypted_accounts

    # インポートメソッド用アカウント群の値のエンクリプト
    def process_imported_accounts(self, imported_accounts):
        encrypted_accounts = {}
        for key, value in imported_accounts.items():
            encrypted_value = self.encrypt_secret(value)
            encrypted_accounts[key] = encrypted_value
        return encrypted_accounts

    # エクスポートメソッド
    def data_export(self):
        dialog = ExportKeyDialog(self.master)
        dialog.wait_window()

        if not dialog.result:
            return

        export_key = hashlib.sha256(dialog.result.encode()).digest()  # Generate a key
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save as"
            )
            if file_path:
                fernet = Fernet(base64.urlsafe_b64encode(export_key))
                decrypted_accounts = self.decrypt_accounts()
                encrypted_data = fernet.encrypt(json.dumps(decrypted_accounts).encode())  # Encrypt data

                with open(file_path, 'wb') as f:
                    f.write(encrypted_data)
                messagebox.showinfo("Export Successful", "Accounts were successfully exported.")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred while exporting: {str(e)}")

    # インポートメソッド
    def data_inport(self):
        dialog = ImportKeyDialog(self.master)
        dialog.wait_window()

        if not dialog.result:
            return

        import_key = hashlib.sha256(dialog.result.encode()).digest()
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Open"
            )
            if not file_path:
                return
            
            fernet = Fernet(base64.urlsafe_b64encode(import_key))
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            try:
                decrypted_data = fernet.decrypt(encrypted_data).decode()
                imported_accounts = json.loads(decrypted_data)
            except Exception:
                messagebox.showerror("Import Failed", "Invalid key or corrupted data file.")
                return

            if messagebox.askyesno("Import Accounts", "Do you want to overwrite your existing accounts with the imported data?"):
                # 現在のPIN暗号化キーで再暗号化
                encrypted_accounts = self.process_imported_accounts(imported_accounts)
                save_accounts(encrypted_accounts)
                self.accounts = encrypted_accounts
                
                # UIを更新
                self.account_combo['values'] = list(self.accounts.keys())
                if self.accounts:
                    self.account_combo.set(list(self.accounts.keys())[0])
                    self.current_account = self.account_combo.get()
                    self.last_totp_period = -1  # TOTPコードを強制的に更新
                else:
                    self.account_combo.set('')
                    self.current_account = None
                    self.last_totp_period = -1
                
                messagebox.showinfo("Import Successful", "Accounts were successfully imported.")
        except Exception as e:
            messagebox.showerror("Import Failed", f"An error occurred while importing: {str(e)}")

    # TOTPコードを更新するメソッド
    def update_code(self):
        current_time = int(time.time())
        current_period = current_time // Config.TOTP_PERIOD
        
        # TOTPコードが変わる時のみ更新
        if self.current_account and current_period != self.last_totp_period:
            try:
                encrypted_secret = self.accounts[self.current_account]
                decrypted_secret = self.decrypt_secret(encrypted_secret)
                self.current_code = generate_totp(decrypted_secret)
                self.code_label.config(text=self.current_code)
                self.copy_button.state(['!disabled'])
                self.last_totp_period = current_period
            except Exception as e:
                print(f"Error decrypting secret: {str(e)}")
                self.code_label.config(text="Error")
                self.copy_button.state(['disabled'])
                self.current_code = ""
        elif not self.current_account:
            self.code_label.config(text="")
            self.copy_button.state(['disabled'])
            self.current_code = ""
            self.last_totp_period = -1

        # 残り時間を計算して表示（毎秒更新）
        seconds_left = Config.TOTP_PERIOD - (current_time % Config.TOTP_PERIOD)
        self.time_label.config(text=f"Refreshing in {seconds_left} seconds")

        # 1秒後に再度update_codeを呼び出す
        self.master.after(1000, self.update_code)

    # シークレットを暗号化する関数
    def encrypt_secret(self, secret):
        f = Fernet(self.encryption_key)
        return f.encrypt(secret.encode()).decode()

    # 暗号化されたシークレットを復号化する関数
    def decrypt_secret(self, encrypted_secret):
        f = Fernet(self.encryption_key)
        return f.decrypt(encrypted_secret.encode()).decode()


# PIN設定関数
def set_pin_with_key(pin):
    salt = os.urandom(Config.SALT_LENGTH)
    hashed_pin = hash_pin(pin)
    with open(Config.PIN_FILE, 'wb') as f:
        f.write(hashed_pin.encode() + salt)
    return derive_key(pin, salt)

# PIN検証関数
def verify_pin_with_key(pin):
    with open(Config.PIN_FILE, 'rb') as f:
        stored_hash = f.read(64).decode()
        salt = f.read(Config.SALT_LENGTH)
    
    if hash_pin(pin) == stored_hash:
        return derive_key(pin, salt)
    else:
        return None

# メイン関数
def main():
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを隠す

    if not os.path.exists(Config.PIN_FILE):
        pin = get_pin(root, "Set New PIN", True)
        if pin and len(pin) >= Config.MIN_PIN_LENGTH and pin.isdigit():
            encryption_key = set_pin_with_key(pin)
        else:
            return
    else:
        pin = get_pin(root, "Verify PIN", False)
        if pin:
            encryption_key = verify_pin_with_key(pin)
            if encryption_key is None:
                messagebox.showerror("Incorrect PIN", "Please try again.")
                return
        else:
            return

    root.deiconify()  # メインウィンドウを表示
    root.configure(bg='#f0f0f0')
    app = MFAApp(root, encryption_key)
    root.mainloop()

if __name__ == "__main__":
    main()
