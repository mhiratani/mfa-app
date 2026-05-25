# ビルドノート

## SSL証明書エラーが出る場合

企業プロキシ環境などで `SEC_E_CERT_EXPIRED` エラーが出る場合、以下を試してください：

### 方法1: 証明書チェックをスキップ（一時的）
```powershell
$env:CARGO_HTTP_CHECK_REVOKE = "false"
cargo check
```

### 方法2: Git設定でSSL検証を無効化（一時的）
```powershell
git config --global http.sslVerify false
$env:CARGO_HTTP_CHECK_REVOKE = "false"
cargo check
```

### 方法3: 企業のルート証明書を追加
IT部門に連絡して、プロキシのCA証明書を取得し、以下に設定：
```powershell
$env:CARGO_HTTP_CAINFO = "C:\path\to\corporate-ca-bundle.crt"
cargo check
```

### 方法4: VPNなしのネットワークで実行
社外ネットワーク（自宅、テザリング等）で `cargo check` を最初に実行すると、
クレートがローカルにキャッシュされ、以降はオフラインでもビルド可能です。

## 通常のビルド手順

```powershell
# 開発モード
cd tauri-app
npm run tauri dev

# プロダクションビルド（インストーラー生成）
npm run tauri build
```

## プロダクションビルドの成果物

- `src-tauri/target/release/MagicalFlyingAlpaca.exe` - スタンドアロンEXE
- `src-tauri/target/release/bundle/msi/` - MSIインストーラー
- `src-tauri/target/release/bundle/nsis/` - NSISインストーラー
