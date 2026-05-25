use std::time::{SystemTime, UNIX_EPOCH};
use totp_rs::{Algorithm, Secret, TOTP};

/// Generate a TOTP code from a base32 secret key.
/// Returns (code, seconds_remaining).
pub fn generate_totp(secret_key: &str) -> Result<(String, u64), Box<dyn std::error::Error>> {
    // Clean up the secret key (remove spaces, convert to uppercase)
    let clean_secret = secret_key
        .trim()
        .replace(' ', "")
        .to_uppercase();

    let secret = Secret::Encoded(clean_secret)
        .to_bytes()
        .map_err(|e| format!("Invalid secret key: {}", e))?;

    // Use new_unchecked to allow secrets shorter than 128 bits (e.g., 80-bit secrets from some services)
    // RFC 4226 allows 80-bit minimum secrets, but totp-rs TOTP::new() enforces 128-bit minimum
    let totp = TOTP::new_unchecked(Algorithm::SHA1, 6, 1, 30, secret, None, "".to_string());

    let time = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| format!("Time error: {}", e))?;

    let code = totp.generate(time.as_secs());
    let seconds_remaining = 30 - (time.as_secs() % 30);

    Ok((code, seconds_remaining))
}
