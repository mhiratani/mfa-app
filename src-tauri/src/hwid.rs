use std::process::Command;

/// Get a hardware-specific ID for this machine.
/// Used to bind encryption to a specific device.
pub fn get_hardware_id() -> String {
    // Try to get motherboard serial number on Windows
    #[cfg(target_os = "windows")]
    {
        if let Ok(output) = Command::new("wmic")
            .args(["baseboard", "get", "serialnumber"])
            .output()
        {
            let result = String::from_utf8_lossy(&output.stdout);
            let serial = result.lines().nth(1).unwrap_or("").trim().to_string();
            if !serial.is_empty() && serial != "To be filled by O.E.M." {
                return serial;
            }
        }

        // Fallback: try to get machine GUID from registry
        if let Ok(output) = Command::new("reg")
            .args([
                "query",
                "HKLM\\SOFTWARE\\Microsoft\\Cryptography",
                "/v",
                "MachineGuid",
            ])
            .output()
        {
            let result = String::from_utf8_lossy(&output.stdout);
            for line in result.lines() {
                if line.contains("MachineGuid") {
                    if let Some(guid) = line.split_whitespace().last() {
                        return guid.to_string();
                    }
                }
            }
        }
    }

    #[cfg(target_os = "macos")]
    {
        if let Ok(output) = Command::new("system_profiler")
            .args(["SPHardwareDataType"])
            .output()
        {
            let result = String::from_utf8_lossy(&output.stdout);
            for line in result.lines() {
                if line.contains("Hardware UUID") {
                    if let Some(uuid) = line.split(':').nth(1) {
                        return uuid.trim().to_string();
                    }
                }
            }
        }
    }

    // Fallback
    "FFFFFFFF".to_string()
}
