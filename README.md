# MFA (Magical Flying Alpaca) Application

## Overview / 概要
This application is a simple tool for managing multi-factor authentication (MFA) codes for multiple accounts. It uses the Time-based One-Time Password (TOTP) algorithm to generate authentication codes for each account.

このアプリケーションは、複数のアカウントの多要素認証（MFA）コードを管理するための簡易アプリです。Time-based One-Time Password（TOTP）アルゴリズムを使用して、各アカウントの認証コードを生成します。

## Main Features / 主な機能
- Store MFA secret keys for multiple accounts / 複数のアカウントのMFAシークレットキーを保存
- Add accounts using QR codes / QRコードを使用してアカウントの追加も可能
- Display TOTP codes in real-time for selected accounts / 選択したアカウントのTOTPコードをリアルタイムで表示
- Copy codes to clipboard with one click or by pressing Enter / ワンクリックまたはEnterキーでコードをクリップボードにコピー
- Add and remove accounts / アカウントの追加と削除
- Export and import data for backup purposes / データのエクスポートとインポートによるバックアップ
- Encrypted storage of secret keys / シークレットキーの暗号化保存
- PIN protection for application security / PINによるアプリケーションのセキュリティ保護
- Code expiration display / コードの有効期限表示

## Installation Instructions / インストール方法

### EXE File Installation Steps / EXEファイルのインストール手順
1. Right-click on the `install.bat` file and select "Run as administrator".
   `install.bat` ファイルを右クリックし、「管理者として実行」を選択します。

2. After installation is complete, a shortcut to the application will be created in the Start menu.
   インストールが完了すると、スタートメニューにアプリケーションのショートカットが作成されます。

3. You can start using the application by launching the installed program.
   インストールされたアプリケーションを起動して使用を開始できます。

### Notes / 注意事項
- During installation, certificate trust settings will be configured. This is necessary to prevent security warnings.
  インストール時に証明書の信頼設定が行われます。これはセキュリティ警告を防ぐために必要です。

- The application is installed per user (in `%LOCALAPPDATA%\MagicalFlyingAlpaca`).
  アプリケーションはユーザーごとにインストールされます（`%LOCALAPPDATA%\MagicalFlyingAlpaca`）。

- Each user will have their own MFA account settings.
  各ユーザーは独自のMFAアカウント設定を持ちます。

## How to Use / 使用方法
1. Launch the application.
   アプリケーションを起動します。

2. Set up a PIN of at least 8 digits on first launch.
   初回起動時に8桁以上のPINを設定します。

3. For subsequent launches, enter your PIN to access the application.
   以降の起動時には設定したPINを入力してアプリケーションにアクセスします。

4. Use the "Add Account" button to add a new account.
   「Add Account」ボタンを使用して新しいアカウントを追加します。

5. Enter the account name and secret key. You can also scan a QR code to read the secret key.
   アカウント名とシークレットキーを入力します。QRコードからシークレットキーを読み取ることもできます。

6. Select an account from the dropdown menu to display its TOTP code.
   ドロップダウンメニューからアカウントを選択すると、そのアカウントのTOTPコードが表示されます。

7. Click the "Copy Code" button or press Enter to copy the code to the clipboard.
   「Copy Code」ボタンをクリックするか、Enterキーを押してコードをクリップボードにコピーできます。

8. Check the remaining time displayed below the code.
   コードの下に表示される残り時間を確認できます。

9. Account information can be backed up or migrated using the export and import functions.
   アカウント情報はエクスポート・インポート機能を使用してバックアップや移行が可能です。

## Security Features / セキュリティ機能
- Account information is stored in encrypted form.
  アカウント情報は暗号化されて保存されます。

- Access to the application is protected by a PIN of at least 8 digits.
  アプリケーションへのアクセスは8桁以上のPINで保護されています。

- The encryption key is generated using the PIN and salt, with additional security provided by device-specific hardware ID.
  PINとソルトを使用して暗号化キーを生成し、さらに各端末固有のハードウェアIDを使ってセキュリティを強化しています。

## Important Notes / 注意事項
- If you forget your PIN, you will not be able to access your stored account information.
  PINを忘れた場合、保存されたアカウント情報にアクセスできなくなります。

- When using QR codes, you can read them from image files.
  QRコードを使用する場合、画像ファイルから読み取ることができます。

## Information for Developers / 開発者向け情報

### Requirements / 必要条件
- Python 3.x
- The following Python libraries / 以下のPythonライブラリ:
  - tkinter (usually included with Python by default / 通常はPythonに標準で含まれています)
  - pyotp
  - cryptography
  - opencv-python
  - numpy

### How to Install Libraries / ライブラリのインストール方法
```
pip install -r requirements.txt
```

### How to Create a Self-Signed Certificate / 自己署名証明書の作成方法

To create a self-signed certificate for signing the EXE file and installation script, open PowerShell with administrator privileges and run the following commands:

EXEファイルとインストールスクリプトに署名するための自己署名証明書を作成するには、管理者権限でPowerShellを開き、以下のコマンドを実行します：

```powershell
# Create a self-signed certificate / 自己署名証明書の作成
$cert = New-SelfSignedCertificate -Subject "CN=Your Name Code Signing" `
    -Type CodeSigningCert `
    -KeyUsage DigitalSignature `
    -KeyAlgorithm RSA `
    -KeyLength 2048 `
    -CertStoreLocation Cert:\CurrentUser\My

# Display the certificate thumbprint (record this for later use) / 証明書のサムプリントを表示（後で使用するために記録しておく）
$cert.Thumbprint

# Backup the certificate (recommended) / 証明書のバックアップ（推奨）
$pwd = ConvertTo-SecureString -String "YourSecurePassword" -Force -AsPlainText
Export-PfxCertificate -Cert "Cert:\CurrentUser\My\$($cert.Thumbprint)" `
    -FilePath "C:\path\to\YourCodeSigningCert.pfx" `
    -Password $pwd

# Export the public key portion (for trust settings on other PCs) / 公開鍵部分をエクスポート（他のPCで信頼設定する場合に使用）
Export-Certificate -Cert "Cert:\CurrentUser\My\$($cert.Thumbprint)" `
    -FilePath "C:\path\to\YourCodeSigningCert.cer"
```

When creating a certificate, please note the following:
証明書を作成する際は、以下の点に注意してください：

- Change `"CN=Your Name Code Signing"` to an appropriate name / `"CN=Your Name Code Signing"` の部分を適切な名前に変更してください
- Change the password to a secure string / パスワードは安全な文字列に変更してください
- Change the export path to an appropriate directory / エクスポート先のパスは適切なディレクトリに変更してください
- Store the certificate backup (.pfx file) in a secure location / 証明書のバックアップ（.pfxファイル）は安全な場所に保管してください
- Never share the .pfx file that contains the private key / 秘密鍵を含む.pfxファイルは決して共有しないでください

### Converting to an Executable (.exe) File / exe形式の実行可能ファイルへの変換

Before converting this Python script to an executable file, please make sure to follow these important steps:

このPythonスクリプトをexe形式の実行可能ファイルに変換する前に、以下の重要な手順を必ず実行してください：

1. Change the `SECRET_KEY` variable in the source code:
   .envファイル内の `SECRET_KEY` 変数を変更します
    - `.env_sample` file rename for `.env` .
    `.env_sample` ファイルを`.env`にリネームします。
   - Open the `.env` file.
     `.env` ファイルを開きます。
   - Replace `"your_secret_key_here"` with your own secure and unpredictable string.
     `"your_secret_key_here"` を、独自の安全で予測不可能な文字列に置き換えます。
   - This step is very important. Leaving the default value will significantly reduce the security of the application.
     この手順は非常に重要です。デフォルトの値のままにすると、アプリケーションのセキュリティが大幅に低下します。

2. Build and signing steps:
   ビルドと署名の手順：
   - Run `build_temp.ps1` to build the application with a temporary name.
     `build_temp.ps1` を実行して一時的な名前でアプリケーションをビルドします。
   - Run `copy_and_sign.ps1` to create and sign the final EXE file.
     `copy_and_sign.ps1` を実行して最終的なEXEファイルを作成し、署名します。
   - Or, run `build_and_sign_all.bat` to automatically execute both steps.
     または、`build_and_sign_all.bat` を実行して両方の手順を自動的に実行します。

3. The generated files will be created in the `dist` directory:
   生成されたファイルは `dist` ディレクトリ内に作成されます：
   - `MagicalFlyingAlpaca.exe` - Signed application / 署名済みアプリケーション
   - `install.ps1` - PowerShell installation script / PowerShellインストールスクリプト
   - `install.bat` - Batch file wrapper / バッチファイルラッパー
   - `MagicalFlyingAlpaca-CodeSigningCert.cer` - Public portion of the certificate / 証明書の公開部分
   - `build_info.txt` - Build information / ビルド情報

Note: Creating an executable file without changing the SECRET_KEY may compromise the security of the application. Always change it to your own secure value.

注意: SECRET_KEYを変更せずに実行可能ファイルを作成すると、アプリケーションのセキュリティが危険にさらされる可能性があります。必ず独自の安全な値に変更してください。