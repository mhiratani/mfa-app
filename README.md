# MFA (Magical Flying Alpaca) Application

## Overview / 概要
This application is a simple desktop tool for managing multi-factor authentication (MFA) codes for multiple accounts. It uses the Time-based One-Time Password (TOTP) algorithm to generate authentication codes for each account.

このアプリケーションは、複数のアカウントの多要素認証（MFA）コードを管理するためのデスクトップアプリです。Time-based One-Time Password（TOTP）アルゴリズムを使用して、各アカウントの認証コードを生成します。

Built with **Tauri + React + TypeScript + Rust**, distributed as a native binary.

**Tauri + React + TypeScript + Rust** で構築されており、ネイティブバイナリとして動作します。

## Main Features / 主な機能
- Store MFA secret keys for multiple accounts / 複数のアカウントのMFAシークレットキーを保存
- Add accounts using QR codes / QRコードを使用してアカウントの追加も可能
- Display TOTP codes in real-time for selected accounts / 選択したアカウントのTOTPコードをリアルタイムで表示
- Copy codes to clipboard with one click or by pressing Enter / ワンクリックまたはEnterキーでコードをクリップボードにコピー
- Add and remove accounts / アカウントの追加と削除
- Encrypted export and import for backup purposes / 暗号化されたエクスポートとインポートによるバックアップ
- Encrypted storage of secret keys / シークレットキーの暗号化保存
- PIN protection (8+ digits) for application security / 8桁以上のPINによるアプリケーションのセキュリティ保護
- Code expiration countdown display / コードの有効期限カウントダウン表示

## How to Use / 使用方法
1. Launch the application.
   アプリケーションを起動します。

2. Set up a PIN of at least 8 digits on first launch.
   初回起動時に8桁以上のPINを設定します。

3. For subsequent launches, enter your PIN to access the application.
   以降の起動時には設定したPINを入力してアプリケーションにアクセスします。

4. Use the "Add Account" button to add a new account.
   「Add Account」ボタンを使用して新しいアカウントを追加します。

5. Enter the account name and secret key. You can also scan a QR code from an image file to read the secret key.
   アカウント名とシークレットキーを入力します。画像ファイルのQRコードからシークレットキーを読み取ることもできます。

6. Select an account from the dropdown menu to display its TOTP code.
   ドロップダウンメニューからアカウントを選択すると、そのアカウントのTOTPコードが表示されます。

7. Click the "Copy Code" button or press Enter to copy the code to the clipboard.
   「Copy Code」ボタンをクリックするか、Enterキーを押してコードをクリップボードにコピーできます。

8. Check the remaining time displayed below the code.
   コードの下に表示される残り時間を確認できます。

9. Account information can be backed up or migrated using the export and import functions.
   アカウント情報はエクスポート・インポート機能を使用してバックアップや移行が可能です。

## Security Features / セキュリティ機能
- **PIN protection**: The application is locked with a PIN of at least 8 digits.
  **PIN保護**: 8桁以上の数字PINでアプリケーションをロックします。

- **AES-256-GCM encryption**: Account secret keys are stored encrypted with AES-256-GCM.
  **AES-256-GCM暗号化**: アカウントのシークレットキーは AES-256-GCM で暗号化して保存されます。

- **Argon2 key derivation**: The encryption key is derived from the PIN using Argon2.
  **Argon2鍵導出**: PINからの暗号化キー生成にArgon2を使用します。

- **Hardware-bound encryption**: A device-specific hardware ID is incorporated into the encryption key.
  **ハードウェアバインド**: 端末固有のハードウェアIDを暗号化キーに組み込んでいます。

- **Encrypted export**: Backup data is also protected with its own encryption key.
  **エクスポート暗号化**: バックアップデータも独自の暗号化キーで保護されます。

## Data Storage Location / データ保存場所
- **User data (Windows)**: `%APPDATA%\MagicalFlyingAlpaca\`
  **ユーザーデータ（Windows）**: `%APPDATA%\MagicalFlyingAlpaca\`
  - `pin.dat` - PIN hash and salt / PINハッシュとソルト
  - `accounts.json` - Encrypted account information / 暗号化されたアカウント情報

## Important Notes / 注意事項
- If you forget your PIN, you will not be able to access your stored account information.
  PINを忘れた場合、保存されたアカウント情報にアクセスできなくなります。

- When using QR codes, you can read them from image files.
  QRコードを使用する場合、画像ファイルから読み取ることができます。

- If the hardware ID changes (e.g., major hardware replacement), existing data may become inaccessible. Use export/import to migrate to a new machine.
  ハードウェアIDが変わると（例: 大幅なハードウェア交換）既存のデータにアクセスできなくなる場合があります。別のPCに移動する場合は、エクスポート/インポート機能を使用してください。

## For Developers / 開発者向け情報

### Tech Stack / 技術スタック

| Layer / 層 | Technology / 技術 |
|------------|-------------------|
| Frontend / フロントエンド | React 18 + TypeScript |
| Styling / スタイリング | Tailwind CSS |
| Build tool / ビルドツール | Vite |
| Desktop framework / デスクトップフレームワーク | Tauri v2 |
| Backend / バックエンド | Rust |
| TOTP generation / TOTP生成 | `totp-rs` crate |
| Encryption / 暗号化 | AES-256-GCM + Argon2 key derivation |

### Requirements / 必要条件
- [Node.js](https://nodejs.org/) (v18+)
- [Rust](https://www.rust-lang.org/tools/install) (latest stable / 最新stable)
- [Tauri CLI](https://v2.tauri.app/start/prerequisites/)
- Windows: Visual Studio Build Tools (with C++ workload / C++ ワークロード)

### Setup & Build / セットアップとビルド

```bash
# Install dependencies / 依存関係のインストール
npm install

# Run in development mode / 開発モードで起動
npm run tauri dev

# Production build / プロダクションビルド
npm run tauri build
```

### Build Artifacts / ビルド成果物
After building, installers are generated in the following directories:
ビルド後、以下のディレクトリにインストーラーが生成されます：

- `src-tauri/target/release/MagicalFlyingAlpaca.exe` - Standalone EXE / スタンドアロンEXE
- `src-tauri/target/release/bundle/msi/` - MSI installer / MSIインストーラー
- `src-tauri/target/release/bundle/nsis/` - NSIS installer / NSISインストーラー
