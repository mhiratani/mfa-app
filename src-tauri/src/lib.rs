mod crypto;
mod hwid;
mod qr;
mod storage;
mod totp;

use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use storage::AccountEntry;
use tauri::{AppHandle, State};

// Application state
struct AppState {
    encryption_key: Mutex<Option<Vec<u8>>>,
    pin_verified: Mutex<bool>,
}

#[derive(Serialize, Deserialize)]
struct TotpResult {
    code: String,
    seconds_remaining: u64,
}

#[derive(Serialize, Deserialize)]
struct ExportData {
    accounts: Vec<ExportAccount>,
}

#[derive(Serialize, Deserialize, Clone)]
struct ExportAccount {
    name: String,
    secret: String,
}

// Check if PIN exists
#[tauri::command]
fn pin_exists(app: AppHandle) -> Result<bool, String> {
    storage::pin_exists(&app)
}

// Set initial PIN
#[tauri::command]
fn set_pin(app: AppHandle, state: State<AppState>, pin: String) -> Result<bool, String> {
    if pin.len() < 8 || !pin.chars().all(|c| c.is_ascii_digit()) {
        return Err("PIN must be at least 8 digits".to_string());
    }

    // 既存 PIN がある場合は誤って上書きしないよう拒否
    if storage::pin_exists(&app)? {
        return Err("PIN already exists. Use verify_pin instead.".to_string());
    }

    let hardware_id = hwid::get_hardware_id();
    let key = crypto::set_pin(&app, &pin, &hardware_id).map_err(|e| e.to_string())?;

    let mut enc_key = state.encryption_key.lock().unwrap();
    *enc_key = Some(key);
    let mut verified = state.pin_verified.lock().unwrap();
    *verified = true;

    Ok(true)
}

// Verify PIN
#[tauri::command]
fn verify_pin(app: AppHandle, state: State<AppState>, pin: String) -> Result<bool, String> {
    let hardware_id = hwid::get_hardware_id();
    match crypto::verify_pin(&app, &pin, &hardware_id) {
        Ok(Some(key)) => {
            let mut enc_key = state.encryption_key.lock().unwrap();
            *enc_key = Some(key);
            let mut verified = state.pin_verified.lock().unwrap();
            *verified = true;
            Ok(true)
        }
        Ok(None) => Ok(false),
        Err(e) => Err(e.to_string()),
    }
}

// Get accounts list (ordered)
#[tauri::command]
fn get_accounts(app: AppHandle, state: State<AppState>) -> Result<Vec<String>, String> {
    let verified = state.pin_verified.lock().unwrap();
    if !*verified {
        return Err("PIN not verified".to_string());
    }

    let accounts = storage::load_accounts(&app)?;
    Ok(accounts.iter().map(|a| a.name.clone()).collect())
}

// Generate TOTP code
#[tauri::command]
fn generate_totp_code(app: AppHandle, state: State<AppState>, account_name: String) -> Result<TotpResult, String> {
    let verified = state.pin_verified.lock().unwrap();
    if !*verified {
        return Err("PIN not verified".to_string());
    }

    let enc_key = state.encryption_key.lock().unwrap();
    let key = enc_key.as_ref().ok_or("No encryption key")?;

    let accounts = storage::load_accounts(&app)?;
    let account = accounts
        .iter()
        .find(|a| a.name == account_name)
        .ok_or("Account not found")?;

    let secret = crypto::decrypt_secret(&account.secret, key).map_err(|e| e.to_string())?;
    let result = totp::generate_totp(&secret).map_err(|e| e.to_string())?;

    Ok(TotpResult {
        code: result.0,
        seconds_remaining: result.1,
    })
}

// Add account
#[tauri::command]
fn add_account(
    app: AppHandle,
    state: State<AppState>,
    account_name: String,
    secret_key: String,
) -> Result<bool, String> {
    let verified = state.pin_verified.lock().unwrap();
    if !*verified {
        return Err("PIN not verified".to_string());
    }

    let enc_key = state.encryption_key.lock().unwrap();
    let key = enc_key.as_ref().ok_or("No encryption key")?;

    if account_name.trim().is_empty() {
        return Err("Account name is required".to_string());
    }

    // Validate secret key by trying to generate a TOTP
    totp::generate_totp(&secret_key).map_err(|_| "Invalid secret key".to_string())?;

    let mut accounts = storage::load_accounts(&app)?;

    // Python版互換: 既存と同名なら追加を拒否
    if accounts.iter().any(|a| a.name == account_name) {
        return Err(format!("Account \"{}\" already exists", account_name));
    }

    let encrypted_secret = crypto::encrypt_secret(&secret_key, key).map_err(|e| e.to_string())?;
    accounts.push(AccountEntry {
        name: account_name,
        secret: encrypted_secret,
    });
    storage::save_accounts(&app, &accounts)?;

    Ok(true)
}

// Remove account
#[tauri::command]
fn remove_account(app: AppHandle, state: State<AppState>, account_name: String) -> Result<bool, String> {
    let verified = state.pin_verified.lock().unwrap();
    if !*verified {
        return Err("PIN not verified".to_string());
    }

    let mut accounts = storage::load_accounts(&app)?;
    accounts.retain(|a| a.name != account_name);
    storage::save_accounts(&app, &accounts)?;

    Ok(true)
}

// Reorder accounts
#[tauri::command]
fn reorder_accounts(app: AppHandle, state: State<AppState>, account_names: Vec<String>) -> Result<bool, String> {
    let verified = state.pin_verified.lock().unwrap();
    if !*verified {
        return Err("PIN not verified".to_string());
    }

    let accounts = storage::load_accounts(&app)?;

    // Reorder based on the provided names list
    let mut reordered: Vec<AccountEntry> = Vec::new();
    for name in &account_names {
        if let Some(account) = accounts.iter().find(|a| &a.name == name) {
            reordered.push(account.clone());
        }
    }

    // Add any accounts not in the provided list at the end (safety)
    for account in &accounts {
        if !account_names.contains(&account.name) {
            reordered.push(account.clone());
        }
    }

    storage::save_accounts(&app, &reordered)?;

    Ok(true)
}

// Export accounts
#[tauri::command]
fn export_accounts(app: AppHandle, state: State<AppState>, export_key: String) -> Result<String, String> {
    let verified = state.pin_verified.lock().unwrap();
    if !*verified {
        return Err("PIN not verified".to_string());
    }

    let enc_key = state.encryption_key.lock().unwrap();
    let key = enc_key.as_ref().ok_or("No encryption key")?;

    let accounts = storage::load_accounts(&app)?;

    let mut export_accounts = Vec::new();
    for account in &accounts {
        let secret = crypto::decrypt_secret(&account.secret, key).map_err(|e| e.to_string())?;
        export_accounts.push(ExportAccount {
            name: account.name.clone(),
            secret,
        });
    }

    let export_data = ExportData {
        accounts: export_accounts,
    };

    let json = serde_json::to_string(&export_data).map_err(|e| e.to_string())?;
    let encrypted = crypto::encrypt_export(&json, &export_key).map_err(|e| e.to_string())?;

    Ok(encrypted)
}

/// インポート時の復号: まず新形式 → ダメなら Python 版 (Fernet) で再試行する。
fn try_decrypt_any_format(data: &str, key: &str) -> Result<String, String> {
    // 新形式 (AES-256-GCM, base64)
    if let Ok(plain) = crypto::decrypt_export(data, key) {
        return Ok(plain);
    }
    // Python 版 (Fernet)
    crypto::decrypt_export_legacy_fernet(data, key)
        .map_err(|e| format!("Invalid key or corrupted data file. ({})", e))
}

/// 復号した JSON を以下の両形式から `Vec<ExportAccount>` へ正規化:
///   - 新形式: { "accounts": [{ "name": ..., "secret": ... }, ...] }
///   - Python版形式: { "AccountName1": "BASE32SECRET", ... }
fn parse_imported_json(json: &str) -> Result<Vec<ExportAccount>, String> {
    use std::collections::HashMap;
    // 1) 新形式
    if let Ok(data) = serde_json::from_str::<ExportData>(json) {
        return Ok(data.accounts);
    }
    // 2) Python版互換 (dict)
    if let Ok(map) = serde_json::from_str::<HashMap<String, String>>(json) {
        let mut accounts: Vec<ExportAccount> = map
            .into_iter()
            .map(|(name, secret)| ExportAccount { name, secret })
            .collect();
        // 名前順にしておくと UX 的に分かりやすい
        accounts.sort_by(|a, b| a.name.cmp(&b.name));
        return Ok(accounts);
    }
    Err("Unsupported import file format".to_string())
}

// Import accounts
#[tauri::command]
fn import_accounts(
    app: AppHandle,
    state: State<AppState>,
    encrypted_data: String,
    import_key: String,
    overwrite: Option<bool>,
) -> Result<Vec<String>, String> {
    let verified = state.pin_verified.lock().unwrap();
    if !*verified {
        return Err("PIN not verified".to_string());
    }

    let enc_key = state.encryption_key.lock().unwrap();
    let key = enc_key.as_ref().ok_or("No encryption key")?;

    let json = try_decrypt_any_format(&encrypted_data, &import_key)?;
    let imported = parse_imported_json(&json)?;

    let mut accounts = if overwrite.unwrap_or(false) {
        // Python版の「既存データを上書きするか？」で Yes に該当する挙動
        Vec::new()
    } else {
        storage::load_accounts(&app)?
    };

    let mut imported_names = Vec::new();
    for imp_account in imported {
        // secret の妥当性チェック (TOTP 生成可能か)
        if totp::generate_totp(&imp_account.secret).is_err() {
            // Python 版では検証していなかったが、不正な値で上書きしないよう skip
            continue;
        }
        let encrypted_secret =
            crypto::encrypt_secret(&imp_account.secret, key).map_err(|e| e.to_string())?;

        // 既存に同名があれば上書き、なければ追加
        if let Some(existing) = accounts.iter_mut().find(|a| a.name == imp_account.name) {
            existing.secret = encrypted_secret;
        } else {
            accounts.push(AccountEntry {
                name: imp_account.name.clone(),
                secret: encrypted_secret,
            });
        }
        imported_names.push(imp_account.name);
    }

    storage::save_accounts(&app, &accounts)?;

    Ok(imported_names)
}

/// QR コード画像から secret を抽出する
#[tauri::command]
fn read_qr_code(image_path: String) -> Result<qr::QrCodeResult, String> {
    qr::read_qr_code(&image_path)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .manage(AppState {
            encryption_key: Mutex::new(None),
            pin_verified: Mutex::new(false),
        })
        .invoke_handler(tauri::generate_handler![
            pin_exists,
            set_pin,
            verify_pin,
            get_accounts,
            generate_totp_code,
            add_account,
            remove_account,
            reorder_accounts,
            export_accounts,
            import_accounts,
            read_qr_code,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
