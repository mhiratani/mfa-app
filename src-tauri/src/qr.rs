use serde::Serialize;
use std::path::Path;

#[derive(Serialize)]
pub struct QrCodeResult {
    pub secret: String,
    pub issuer: Option<String>,
    pub account: Option<String>,
}

/// Read a QR code image from the given file path and try to extract a TOTP secret.
///
/// Python版 mfa_app.py の AddAccountDialog.read_qr_code 相当:
///   - 画像から QR コードを検出
///   - otpauth URI から `secret=` と `issuer=` を抜き出す
pub fn read_qr_code(image_path: &str) -> Result<QrCodeResult, String> {
    let path = Path::new(image_path);
    if !path.exists() {
        return Err(format!(
            "Failed to read image file: {}",
            path.file_name()
                .and_then(|s| s.to_str())
                .unwrap_or(image_path)
        ));
    }

    // 画像の読み込み（image クレートは UTF-8 パスでバイナリ読み込み）
    let img = image::open(path)
        .map_err(|e| format!("Failed to read image file: {}", e))?
        .to_luma8();

    // QR コード検出
    let mut prepared = rqrr::PreparedImage::prepare(img);
    let grids = prepared.detect_grids();
    if grids.is_empty() {
        return Err("Failed to extract information from QR code.".to_string());
    }

    for grid in grids {
        if let Ok((_meta, content)) = grid.decode() {
            if let Some(result) = parse_otpauth(&content) {
                return Ok(result);
            }
        }
    }

    Err("Failed to extract information from QR code.".to_string())
}

/// Parse an `otpauth://totp/...?secret=XXXX&issuer=YYY` URI.
fn parse_otpauth(content: &str) -> Option<QrCodeResult> {
    // url クレートで安全にパース、失敗したら正規表現フォールバック
    if let Ok(parsed) = url::Url::parse(content) {
        if parsed.scheme() == "otpauth" {
            let mut secret: Option<String> = None;
            let mut issuer: Option<String> = None;
            for (k, v) in parsed.query_pairs() {
                match k.as_ref() {
                    "secret" => secret = Some(v.to_string()),
                    "issuer" => issuer = Some(v.to_string()),
                    _ => {}
                }
            }

            // パス部分は "/totp/Issuer:account" の形式
            let label = parsed.path().trim_start_matches('/');
            // "totp/" or "hotp/" の prefix を除去
            let label = label
                .splitn(2, '/')
                .nth(1)
                .unwrap_or(label);
            let label = percent_decode(label);

            let (path_issuer, account) = if let Some(idx) = label.find(':') {
                (Some(label[..idx].to_string()), Some(label[idx + 1..].trim().to_string()))
            } else if !label.is_empty() {
                (None, Some(label))
            } else {
                (None, None)
            };

            if issuer.is_none() {
                issuer = path_issuer;
            }

            if let Some(s) = secret {
                return Some(QrCodeResult {
                    secret: s,
                    issuer,
                    account,
                });
            }
        }
    }

    // フォールバック: シンプルな文字列マッチ（Python版互換）
    let secret = simple_capture(content, "secret=")?;
    let issuer = simple_capture(content, "issuer=");
    Some(QrCodeResult {
        secret,
        issuer,
        account: None,
    })
}

fn simple_capture(s: &str, key: &str) -> Option<String> {
    let idx = s.find(key)?;
    let rest = &s[idx + key.len()..];
    let end = rest.find('&').unwrap_or(rest.len());
    Some(rest[..end].to_string())
}

fn percent_decode(s: &str) -> String {
    // 簡易 percent-decode (url クレートの query_pairs は自動だが path は手動)
    let mut out = Vec::with_capacity(s.len());
    let bytes = s.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        if bytes[i] == b'%' && i + 2 < bytes.len() {
            if let (Some(h), Some(l)) = (hex_val(bytes[i + 1]), hex_val(bytes[i + 2])) {
                out.push((h << 4) | l);
                i += 3;
                continue;
            }
        }
        out.push(bytes[i]);
        i += 1;
    }
    String::from_utf8_lossy(&out).into_owned()
}

fn hex_val(b: u8) -> Option<u8> {
    match b {
        b'0'..=b'9' => Some(b - b'0'),
        b'a'..=b'f' => Some(b - b'a' + 10),
        b'A'..=b'F' => Some(b - b'A' + 10),
        _ => None,
    }
}
