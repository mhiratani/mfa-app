# MFA (Magical Flying Alpaca) Application

## Overview
This application is a sample app for managing multi-factor authentication (MFA) codes for multiple accounts. It uses the Time-based One-Time Password (TOTP) algorithm to generate authentication codes for each account.

## Main Features
- Save MFA secret keys for multiple accounts
- Optionally add accounts using QR codes
- Display TOTP code for the selected account in real-time
- Copy code to clipboard with one click or by pressing the Enter key
- Add and delete accounts
- Share accounts via data export and import
- Encrypt and save secret keys
- Secure the application with a PIN
- Display expiration time for codes

## Requirements
- Python 3.x
- The following Python libraries:
  - tkinter (usually included with Python)
  - pyotp
  - cryptography
  - opencv-python
  - numpy

## How to Install Libraries

To install the necessary libraries individually:
```
pip install pyotp cryptography opencv-python numpy
```

## Usage Instructions
1. Launch the application.
2. Set an 8-digit or longer PIN on the first launch.
3. For subsequent launches, enter the PIN you set to access the application.
4. Use the "Add Account" button to add a new account.
5. Enter the account name and secret key. You can also read the secret key from a QR code.
6. Select an account from the dropdown menu to display its TOTP code.
7. Click the "Copy Code" button or press the Enter key to copy the code to the clipboard.
8. Check the remaining time displayed below the code.
9. Account information can be backed up or transferred using the export and import functions.

## Security Features
- Account information is saved with encryption.
- Access to the application is protected by an 8-digit or longer PIN.
- An encryption key is generated using the PIN and salt, further enhanced with a hardware-specific ID for added security on each device.

## Important Notes
- If you forget your PIN, you will not be able to access the stored account information.
- When using QR codes, you can read them from the camera or an image file depending on your environment.

## Converting to an Executable File

Before converting this Python script to an executable file, be sure to complete the following crucial steps:

1. Change the `SECRET_KEY` variable in the source code:
   - Open the `mfa_app.py` file.
   - Find the following line:
     ```python
     SECRET_KEY = "your_secret_key_here"
     ```
   - Replace `"your_secret_key_here"` with your own secure and unpredictable string.
   - This step is crucial. Failing to change the default value will significantly weaken the application's security.

2. Install PyInstaller (if it hasn't been installed):
   ```
   pip install pyinstaller
   ```

3. Navigate to the directory containing the script and run the following command:
   ```
   pyinstaller mfa_app.spec
   ```

4. The generated executable file will be created in the `dist` directory.

Note: Failing to change the SECRET_KEY before creating the executable file may jeopardize the application's security. Make sure to change it to a secure, unique value.

# MFA( Magical Flying Alpaca ) Application

## 概要
このアプリケーションは、複数のアカウントの多要素認証（MFA）コードを管理するためのサンプルアプリです。Time-based One-Time Password（TOTP）アルゴリズムを使用して、各アカウントの認証コードを生成します。

## 主な機能
- 複数のアカウントのMFAシークレットキーを保存
- オプションでQRコードを使用してアカウントを追加
- 選択したアカウントのTOTPコードをリアルタイムで表示
- ワンクリックまたはEnterキーでコードをクリップボードにコピー
- アカウントの追加と削除
- データのエクスポートとインポートによるアカウントの共有
- シークレットキーの暗号化保存
- PINによるアプリケーションのセキュリティ保護
- コードの有効期限表示

## 必要条件
- Python 3.x
- 以下のPythonライブラリ:
  - tkinter (通常はPythonに標準で含まれています)
  - pyotp
  - cryptography
  - opencv-python
  - numpy

## ライブラリのインストール方法

必要なライブラリを個別にインストールする場合：
```
pip install pyotp cryptography opencv-python numpy
```

## 使用方法
1. アプリケーションを起動します：
2. 初回起動時に8桁以上のPINを設定します。
3. 以降の起動時には設定したPINを入力してアプリケーションにアクセスします。
4. 「Add Account」ボタンを使用して新しいアカウントを追加します。
5. アカウント名とシークレットキーを入力します。QRコードからシークレットキーを読み取ることもできます。
6. ドロップダウンメニューからアカウントを選択すると、そのアカウントのTOTPコードが表示されます。
7. 「Copy Code」ボタンをクリックするか、Enterキーを押してコードをクリップボードにコピーできます。
8. コードの下に表示される残り時間を確認できます。
9. アカウント情報はエクスポート・インポート機能を使用してバックアップや移行が可能です。

## セキュリティ機能
- アカウント情報は暗号化されて保存されます。
- アプリケーションへのアクセスは8桁以上のPINで保護されています。
- PINとソルトを使用して暗号化キーを生成し、さらに各端末固有のハードウェアIDを使ってセキュリティを強化しています。

## 注意事項
- PINを忘れた場合、保存されたアカウント情報にアクセスできなくなります。
- QRコードを使用する場合、環境に応じてカメラや画像ファイルから読み取ることができます。

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
   ```
   pip install pyinstaller
   ```

3. スクリプトのあるディレクトリに移動し、以下のコマンドを実行します:
   ```
   pyinstaller mfa_app.spec
   ```

4. 生成された実行可能ファイルは `dist` ディレクトリ内に作成されます。

注意: SECRET_KEYを変更せずに実行可能ファイルを作成すると、アプリケーションのセキュリティが危険にさらされる可能性があります。必ず独自の安全な値に変更してください。 