# MFA (Magical Flying Alpaca) Application

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

## インストール方法

### チームメンバー向けインストール手順
1. `install.bat` ファイルを右クリックし、「管理者として実行」を選択します。
2. インストールが完了すると、スタートメニューにアプリケーションのショートカットが作成されます。
3. インストールされたアプリケーションを起動して使用を開始できます。

### 注意事項
- インストール時に証明書の信頼設定が行われます。これはセキュリティ警告を防ぐために必要です。
- アプリケーションはユーザーごとにインストールされます（`%LOCALAPPDATA%\MagicalFlyingAlpaca`）。
- 各ユーザーは独自のMFAアカウント設定を持ちます。

## 使用方法
1. アプリケーションを起動します。
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

## 開発者向け情報

### 必要条件
- Python 3.x
- 以下のPythonライブラリ:
  - tkinter (通常はPythonに標準で含まれています)
  - pyotp
  - cryptography
  - opencv-python
  - numpy

### ライブラリのインストール方法
```
pip install pyotp cryptography opencv-python numpy
```

### 自己署名証明書の作成方法

EXEファイルとインストールスクリプトに署名するための自己署名証明書を作成するには、管理者権限でPowerShellを開き、以下のコマンドを実行します：

```powershell
# 自己署名証明書の作成
$cert = New-SelfSignedCertificate -Subject "CN=Your Name Code Signing" `
    -Type CodeSigningCert `
    -KeyUsage DigitalSignature `
    -KeyAlgorithm RSA `
    -KeyLength 2048 `
    -CertStoreLocation Cert:\CurrentUser\My

# 証明書のサムプリントを表示（後で使用するために記録しておく）
$cert.Thumbprint

# 証明書のバックアップ（推奨）
$pwd = ConvertTo-SecureString -String "YourSecurePassword" -Force -AsPlainText
Export-PfxCertificate -Cert "Cert:\CurrentUser\My\$($cert.Thumbprint)" `
    -FilePath "C:\path\to\YourCodeSigningCert.pfx" `
    -Password $pwd

# 公開鍵部分をエクスポート（他のPCで信頼設定する場合に使用）
Export-Certificate -Cert "Cert:\CurrentUser\My\$($cert.Thumbprint)" `
    -FilePath "C:\path\to\YourCodeSigningCert.cer"
```

証明書を作成する際は、以下の点に注意してください：
- `"CN=Your Name Code Signing"` の部分を適切な名前に変更してください
- パスワードは安全な文字列に変更してください
- エクスポート先のパスは適切なディレクトリに変更してください
- 証明書のバックアップ（.pfxファイル）は安全な場所に保管してください
- 秘密鍵を含む.pfxファイルは決して共有しないでください

### exe形式の実行可能ファイルへの変換

このPythonスクリプトをexe形式の実行可能ファイルに変換する前に、以下の重要な手順を必ず実行してください：

1. ソースコード内の `SECRET_KEY` 変数を変更します：
   - `mfa_app.py` ファイルを開きます。
   - 以下の行を探します：
     ```python
     SECRET_KEY = "your_secret_key_here"
     ```
   - `"your_secret_key_here"` を、独自の安全で予測不可能な文字列に置き換えます。
   - この手順は非常に重要です。デフォルトの値のままにすると、アプリケーションのセキュリティが大幅に低下します。

2. ビルドと署名の手順：
   - `build_temp.ps1` を実行して一時的な名前でアプリケーションをビルドします。
   - `copy_and_sign.ps1` を実行して最終的なEXEファイルを作成し、署名します。
   - または、`build_and_sign_all.bat` を実行して両方の手順を自動的に実行します。

3. 生成されたファイルは `dist` ディレクトリ内に作成されます：
   - `MagicalFlyingAlpaca.exe` - 署名済みアプリケーション
   - `install.ps1` - PowerShellインストールスクリプト
   - `install.bat` - バッチファイルラッパー
   - `MagicalFlyingAlpaca-CodeSigningCert.cer` - 証明書の公開部分
   - `build_info.txt` - ビルド情報

注意: SECRET_KEYを変更せずに実行可能ファイルを作成すると、アプリケーションのセキュリティが危険にさらされる可能性があります。必ず独自の安全な値に変更してください。