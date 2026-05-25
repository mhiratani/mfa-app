use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use tauri_plugin_store::StoreExt;

const STORE_FILENAME: &str = "app_data.json";

// Keys in the store
const KEY_PIN_HASH: &str = "pin_hash";
const KEY_PIN_SALT: &str = "pin_salt";
const KEY_ACCOUNTS: &str = "accounts";

/// A single account entry (ordered)
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct AccountEntry {
    pub name: String,
    pub secret: String,
}

/// Check if PIN exists in store
pub fn pin_exists(app: &AppHandle) -> Result<bool, String> {
    let store = app.store(STORE_FILENAME).map_err(|e| e.to_string())?;
    Ok(store.get(KEY_PIN_HASH).is_some())
}

/// Save PIN hash and salt to store
pub fn save_pin_data(app: &AppHandle, pin_hash: &str, salt: &str) -> Result<(), String> {
    let store = app.store(STORE_FILENAME).map_err(|e| e.to_string())?;
    store.set(KEY_PIN_HASH, serde_json::json!(pin_hash));
    store.set(KEY_PIN_SALT, serde_json::json!(salt));
    store.save().map_err(|e| e.to_string())?;
    Ok(())
}

/// Load PIN hash and salt from store
pub fn load_pin_data(app: &AppHandle) -> Result<(String, String), String> {
    let store = app.store(STORE_FILENAME).map_err(|e| e.to_string())?;

    let pin_hash = store
        .get(KEY_PIN_HASH)
        .and_then(|v| v.as_str().map(|s| s.to_string()))
        .ok_or("PIN hash not found in store")?;

    let pin_salt = store
        .get(KEY_PIN_SALT)
        .and_then(|v| v.as_str().map(|s| s.to_string()))
        .ok_or("PIN salt not found in store")?;

    Ok((pin_hash, pin_salt))
}

/// Load accounts from store (ordered)
pub fn load_accounts(app: &AppHandle) -> Result<Vec<AccountEntry>, String> {
    let store = app.store(STORE_FILENAME).map_err(|e| e.to_string())?;

    match store.get(KEY_ACCOUNTS) {
        Some(value) => {
            let accounts: Vec<AccountEntry> =
                serde_json::from_value(value.clone()).map_err(|e| e.to_string())?;
            Ok(accounts)
        }
        None => Ok(Vec::new()),
    }
}

/// Save accounts to store (ordered)
pub fn save_accounts(app: &AppHandle, accounts: &[AccountEntry]) -> Result<(), String> {
    let store = app.store(STORE_FILENAME).map_err(|e| e.to_string())?;
    let value = serde_json::to_value(accounts).map_err(|e| e.to_string())?;
    store.set(KEY_ACCOUNTS, value);
    store.save().map_err(|e| e.to_string())?;
    Ok(())
}
