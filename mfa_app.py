import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pyotp
import time
import json
import re
import os
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

# ソースコードに埋め込む秘密鍵（実際の使用時は変更してください）
SECRET_KEY = "your_secret_key_here"
# 関連ファイル名の設定
PIN_FILE ='MagicalFlyingAlpaca-Pin.dat'
ACCOUNTS_FILE ='MagicalFlyingAlpaca-Accounts.json'

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

def set_pin():
    """新しいPINを設定し、対応する暗号化キーを生成"""
    while True:
        pin = simpledialog.askstring("Set PIN", "Please set a 4-digit PIN:", show="*")
        if pin and len(pin) == 4 and pin.isdigit():
            salt = os.urandom(16)
            hashed_pin = hash_pin(pin)
            with open(PIN_FILE, 'wb') as f:
                f.write(hashed_pin.encode() + salt)
            return derive_key(pin, salt)
        else:
            messagebox.showerror("Invalid PIN", "Please enter a 4-digit number.")

def verify_pin():
    """ユーザーが入力したPINを検証し、正しい場合は暗号化キーを返す"""
    with open(PIN_FILE, 'rb') as f:
        stored_hash = f.read(64).decode()
        salt = f.read(16)
    
    while True:
        pin = simpledialog.askstring("Verify PIN", "Enter your 4-digit PIN:", show="*")
        if pin and hash_pin(pin) == stored_hash:
            return derive_key(pin, salt)
        else:
            messagebox.showerror("Incorrect PIN", "Please try again.")

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
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as f:
            return json.load(f)
    return {}

# アカウント情報をJSONファイルに保存する関数
def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f)

# PINダイアログクラス
class PinDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.pin = tk.StringVar()
        self.result = None

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20 20 20 20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Enter 4-digit PIN:", font=('Helvetica', 14)).grid(row=0, column=0, pady=10)
        pin_entry = ttk.Entry(frame, textvariable=self.pin, show="*", font=('Helvetica', 14), width=10)
        pin_entry.grid(row=1, column=0, pady=10)
        pin_entry.focus()

        # Enterキーを押したときにもok関数を呼び出す
        pin_entry.bind('<Return>', lambda event: self.ok())

        ok_button = ttk.Button(frame, text="OK", command=self.ok, width=20)
        ok_button.grid(row=2, column=0, pady=10)

        self.geometry("200x200")

    def ok(self):
        pin = self.pin.get()
        if len(pin) == 4 and pin.isdigit():
            self.result = pin
            self.destroy()
        else:
            messagebox.showerror("Invalid PIN", "Please enter a 4-digit number.")
            self.pin.set("")  # PINをクリア

def get_pin(parent, title):
    dialog = PinDialog(parent, title)
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

        self.master.geometry("400x350")

        self.update_code()

    # アカウントが選択されたときのコールバック
    def on_account_select(self, event):
        self.current_account = self.account_combo.get()

    def bind_keys(self):
        # Enterキーを押したときにcopy_codeメソッドを呼び出す
        self.master.bind('<Return>', lambda event: self.copy_code())

    # コードをクリップボードにコピーするメソッド
    def copy_code(self):
        if self.current_code:
            self.master.clipboard_clear()
            self.master.clipboard_append(self.current_code)
            messagebox.showinfo("Copied", "Code copied to clipboard!")
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

    # TOTPコードを更新するメソッド
    def update_code(self):
        if self.current_account:
            try:
                encrypted_secret = self.accounts[self.current_account]
                decrypted_secret = self.decrypt_secret(encrypted_secret)
                self.current_code = generate_totp(decrypted_secret)
                self.code_label.config(text=self.current_code)
                self.copy_button.state(['!disabled'])
            except Exception as e:
                print(f"Error decrypting secret for {self.current_account}: {str(e)}")
                self.code_label.config(text="Error")
                self.copy_button.state(['disabled'])
        else:
            self.code_label.config(text="")
            self.copy_button.state(['disabled'])

        # 残り時間を計算して表示
        current_time = int(time.time())
        seconds_left = 30 - (current_time % 30)
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
    salt = os.urandom(16)
    hashed_pin = hash_pin(pin)
    with open(PIN_FILE, 'wb') as f:
        f.write(hashed_pin.encode() + salt)
    return derive_key(pin, salt)

# PIN検証関数
def verify_pin_with_key(pin):
    with open(PIN_FILE, 'rb') as f:
        stored_hash = f.read(64).decode()
        salt = f.read(16)
    
    if hash_pin(pin) == stored_hash:
        return derive_key(pin, salt)
    else:
        return None

# メイン関数
def main():
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを隠す

    if not os.path.exists(PIN_FILE):
        pin = get_pin(root, "Set PIN")
        if pin and len(pin) == 4 and pin.isdigit():
            encryption_key = set_pin_with_key(pin)
        else:
            messagebox.showerror("Invalid PIN", "Please enter a 4-digit number.")
            return
    else:
        pin = get_pin(root, "Verify PIN")
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