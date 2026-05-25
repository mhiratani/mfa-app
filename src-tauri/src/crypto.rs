use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce,
};
use argon2::Argon2;
use base64::{engine::general_purpose::STANDARD as BASE64, Engine};
use rand::RngCore;
use sha2::{Digest, Sha256};
use std::io;
use tauri::AppHandle;

use crate::storage;

const SECRET_KEY: &str = "magical_flying_alpaca_secret_2026";

/// Derive encryption key from PIN + hardware_id
fn derive_key(pin: &str, salt: &[u8], hardware_id: &str) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    let input = format!("{}{}{}", pin, SECRET_KEY, hardware_id);
    let mut key = vec![0u8; 32];
    Argon2::default()
        .hash_password_into(input.as_bytes(), salt, &mut key)
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;
    Ok(key)
}

/// Hash PIN for verification
fn hash_pin(pin: &str, hardware_id: &str) -> String {
    let input = format!("{}{}{}", pin, SECRET_KEY, hardware_id);
    let hash = Sha256::digest(input.as_bytes());
    hex::encode(hash)
}

/// Set a new PIN and return the encryption key
pub fn set_pin(app: &AppHandle, pin: &str, hardware_id: &str) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    let mut salt = vec![0u8; 16];
    rand::thread_rng().fill_bytes(&mut salt);

    let pin_hash = hash_pin(pin, hardware_id);
    let key = derive_key(pin, &salt, hardware_id)?;

    // Store pin hash and salt (base64 encoded)
    let salt_b64 = BASE64.encode(&salt);
    storage::save_pin_data(app, &pin_hash, &salt_b64)
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e))?;

    Ok(key)
}

/// Verify PIN and return encryption key if correct
pub fn verify_pin(app: &AppHandle, pin: &str, hardware_id: &str) -> Result<Option<Vec<u8>>, Box<dyn std::error::Error>> {
    let (stored_hash, salt_b64) = storage::load_pin_data(app)
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e))?;
    let salt = BASE64.decode(&salt_b64)?;
    let pin_hash = hash_pin(pin, hardware_id);

    if pin_hash == stored_hash {
        let key = derive_key(pin, &salt, hardware_id)?;
        Ok(Some(key))
    } else {
        Ok(None)
    }
}

/// Encrypt a secret key for storage
pub fn encrypt_secret(secret: &str, key: &[u8]) -> Result<String, Box<dyn std::error::Error>> {
    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;

    let mut nonce_bytes = [0u8; 12];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    let ciphertext = cipher
        .encrypt(nonce, secret.as_bytes())
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;

    // Combine nonce + ciphertext and base64 encode
    let mut combined = nonce_bytes.to_vec();
    combined.extend(ciphertext);

    Ok(BASE64.encode(combined))
}

/// Decrypt a stored secret
pub fn decrypt_secret(encrypted: &str, key: &[u8]) -> Result<String, Box<dyn std::error::Error>> {
    let combined = BASE64.decode(encrypted)?;

    if combined.len() < 12 {
        return Err("Invalid encrypted data".into());
    }

    let (nonce_bytes, ciphertext) = combined.split_at(12);
    let nonce = Nonce::from_slice(nonce_bytes);

    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;

    let plaintext = cipher
        .decrypt(nonce, ciphertext)
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;

    Ok(String::from_utf8(plaintext)?)
}

/// Encrypt data for export with a user-provided key
pub fn encrypt_export(data: &str, export_key: &str) -> Result<String, Box<dyn std::error::Error>> {
    let key_hash = Sha256::digest(export_key.as_bytes());
    let key = &key_hash[..32];

    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;

    let mut nonce_bytes = [0u8; 12];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    let ciphertext = cipher
        .encrypt(nonce, data.as_bytes())
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;

    let mut combined = nonce_bytes.to_vec();
    combined.extend(ciphertext);

    Ok(BASE64.encode(combined))
}

/// Decrypt exported data with a user-provided key (current AES-256-GCM format)
pub fn decrypt_export(encrypted: &str, import_key: &str) -> Result<String, Box<dyn std::error::Error>> {
    let key_hash = Sha256::digest(import_key.as_bytes());
    let key = &key_hash[..32];

    let combined = BASE64.decode(encrypted)?;

    if combined.len() < 12 {
        return Err("Invalid encrypted data".into());
    }

    let (nonce_bytes, ciphertext) = combined.split_at(12);
    let nonce = Nonce::from_slice(nonce_bytes);

    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;

    let plaintext = cipher
        .decrypt(nonce, ciphertext)
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;

    Ok(String::from_utf8(plaintext)?)
}

/// Decrypt exported data using the Python (legacy) Fernet format.
///
/// Python版 mfa_app.py の data_export() は以下と互換:
///   key32  = SHA256(user_key).digest()           # 32 bytes
///   fkey   = base64.urlsafe_b64encode(key32)     # Fernet key
///   token  = Fernet(fkey).encrypt(json_bytes)    # str (URL-safe base64)
///
/// Fernet token format:
///   0x80 (version, 1B) || timestamp (8B BE) || iv (16B) ||
///   ciphertext (n*16B, AES-128-CBC, PKCS7) || hmac (32B HMAC-SHA256)
///
/// 注: 互換のために Pure Rust で自前実装している。
pub fn decrypt_export_legacy_fernet(
    encrypted: &str,
    import_key: &str,
) -> Result<String, Box<dyn std::error::Error>> {
    use aes::Aes128;
    use base64::engine::general_purpose::URL_SAFE as URL_SAFE_B64;
    use cbc::cipher::{block_padding::Pkcs7, BlockDecryptMut, KeyIvInit};
    use hmac::{Hmac, Mac};

    type HmacSha256 = Hmac<Sha256>;
    type Aes128CbcDec = cbc::Decryptor<Aes128>;

    // Python では key_bytes は SHA256(user_key).digest() (32 bytes) そのもの
    let key_hash = Sha256::digest(import_key.as_bytes());
    let signing_key = &key_hash[..16];
    let enc_key = &key_hash[16..32];

    // Fernet トークンは URL-safe base64 (パディングあり) でデコード
    let token = encrypted.trim();
    let raw = URL_SAFE_B64
        .decode(token.as_bytes())
        .map_err(|e| io::Error::new(io::ErrorKind::Other, format!("Base64 decode failed: {}", e)))?;

    if raw.len() < 1 + 8 + 16 + 32 {
        return Err("Invalid Fernet token (too short)".into());
    }
    if raw[0] != 0x80 {
        return Err("Invalid Fernet token (bad version)".into());
    }

    let hmac_offset = raw.len() - 32;
    let signed_part = &raw[..hmac_offset];
    let mac_value = &raw[hmac_offset..];

    // HMAC 検証
    let mut mac = <HmacSha256 as Mac>::new_from_slice(signing_key)
        .map_err(|e: hmac::digest::InvalidLength| io::Error::new(io::ErrorKind::Other, e.to_string()))?;
    mac.update(signed_part);
    mac.verify_slice(mac_value)
        .map_err(|_| io::Error::new(io::ErrorKind::Other, "Fernet HMAC verification failed"))?;

    let iv = &raw[1 + 8..1 + 8 + 16];
    let ciphertext = &raw[1 + 8 + 16..hmac_offset];

    // AES-128-CBC 復号 + PKCS7 除去
    let cipher = Aes128CbcDec::new_from_slices(enc_key, iv)
        .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;
    let mut buf = ciphertext.to_vec();
    let plaintext = cipher
        .decrypt_padded_mut::<Pkcs7>(&mut buf)
        .map_err(|e| io::Error::new(io::ErrorKind::Other, format!("AES-CBC decrypt failed: {}", e)))?;

    Ok(String::from_utf8(plaintext.to_vec())?)
}
