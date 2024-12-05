# MFA (Magical Flying Alpaca) Application

## Overview
This application is a sample app for managing multi-factor authentication (MFA) codes for multiple accounts. It uses the Time-based One-Time Password (TOTP) algorithm to generate authentication codes for each account.

## Main Features
- Store MFA secret keys for multiple accounts
- Display TOTP code for the selected account in real-time
- Copy code to clipboard with one click or the Enter key
- Add and delete accounts
- Encrypt and save secret keys
- Protect the application with a PIN
- Display code expiration time

## Requirements
- Python 3.x
- The following Python libraries:
  - tkinter (usually included with Python by default)
  - pyotp
  - cryptography

## How to Install Libraries

To install the required libraries individually:
`pip install pyotp cryptography`

## Usage
1. Launch the application:
2. Set a 4-digit PIN on the first launch.
3. On subsequent launches, enter the set PIN to access the application.
4. Use the "Add Account" button to add a new account.
5. Enter the account name and secret key.
6. Select an account from the dropdown menu to display its TOTP code.
7. Click the "Copy Code" button or press the Enter key to copy the code to the clipboard.
8. Check the remaining time displayed below the code.

## Security Features
- Account information is encrypted and stored securely.
- Access to the application is protected by a 4-digit PIN.
- An encryption key is generated using the PIN and a salt for enhanced security.

## Important Note
- If you forget the PIN, you will not be able to access the saved account information.

## Converting to Executable File

Before converting this Python script to an executable (exe) file, ensure to perform the following crucial steps:

1. Change the `SECRET_KEY` variable in the source code:
   - Open the `mfa_app.py` file.
   - Find the line:
     ```python
     SECRET_KEY = "your_secret_key_here"
     ```
   - Replace `"your_secret_key_here"` with your own secure and unpredictable string.
   - This step is extremely important. If left with the default value, the application's security will be significantly compromised.

2. Install PyInstaller (if not already installed):
`pip install pyinstaller`

3. Move to the directory containing the script, and run the following command:
`pyinstaller mfa_app.spec`

4. The generated executable file will be created within the `dist` directory.

Note: If you create the executable without changing the SECRET_KEY, the application's security may be at risk. Be sure to change it to your own secure value.

# MFA( Magical Flying Alpaca ) Application

## 概要
このアプリケーションは、複数のアカウントの多要素認証（MFA）コードを管理するためのサンプルアプリです。Time-based One-Time Password（TOTP）アルゴリズムを使用して、各アカウントの認証コードを生成します。

## 主な機能
- 複数のアカウントのMFAシークレットキーを保存
- 選択したアカウントのTOTPコードをリアルタイムで表示
- ワンクリックまたはEnterキーでコードをクリップボードにコピー
- アカウントの追加と削除
- シークレットキーの暗号化保存
- PINによるアプリケーションのセキュリティ保護
- コードの有効期限表示

## 必要条件
- Python 3.x
- 以下のPythonライブラリ:
  - tkinter (通常はPythonに標準で含まれています)
  - pyotp
  - cryptography

## ライブラリのインストール方法

必要なライブラリを個別にインストールする場合：
pip install pyotp cryptography


## 使用方法
1. アプリケーションを起動します：
2. 初回起動時に4桁のPINを設定します。
3. 以降の起動時には設定したPINを入力してアプリケーションにアクセスします。
4. 「Add Account」ボタンを使用して新しいアカウントを追加します。
5. アカウント名とシークレットキーを入力します。
6. ドロップダウンメニューからアカウントを選択すると、そのアカウントのTOTPコードが表示されます。
7. 「Copy Code」ボタンをクリックするか、Enterキーを押してコードをクリップボードにコピーできます。
8. コードの下に表示される残り時間を確認できます。

## セキュリティ機能
- アカウント情報は暗号化されて保存されます。
- アプリケーションへのアクセスは4桁のPINで保護されています。
- PINとソルトを使用して暗号化キーを生成し、より強固なセキュリティを実現しています。

## 注意事項
- PINを忘れた場合、保存されたアカウント情報にアクセスできなくなります。

## exe形式の実行可能ファイルへの変換

このPythonスクリプトをexe形式の実行可能ファイルに変換する前に、以下の重要な手順を必ず実行してください：

1. ソースコード内の `SECRET_KEY` 変数を変更します：
   - `mfa_app.py` ファイルを開きます。
   - 以下の行を探します：
     ```python
     SECRET_KEY = "your_secret_key_here"
     ```
   - `"your_secret_key_here"` を、独自の安全で予測不可能な文字列に置き換えます。
   - この手順は非常に重要です。デフォルトの値のままにすると、アプリケーションのセキュリティが大幅に低下します。

2. PyInstallerをインストールします（まだインストールしていない場合）:
pip install pyinstaller


3. スクリプトのあるディレクトリに移動し、以下のコマンドを実行します:
pyinstaller mfa_app.spec


4. 生成された実行可能ファイルは `dist` ディレクトリ内に作成されます。

注意: SECRET_KEYを変更せずに実行可能ファイルを作成すると、アプリケーションのセキュリティが危険にさらされる可能性があります。必ず独自の安全な値に変更してください。