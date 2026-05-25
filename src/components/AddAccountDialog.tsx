import { useState, useRef, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-dialog";

interface AddAccountDialogProps {
  onAdd: (name: string, secret: string) => void;
  onClose: () => void;
}

interface QrCodeResult {
  secret: string;
  issuer?: string | null;
  account?: string | null;
}

function AddAccountDialog({ onAdd, onClose }: AddAccountDialogProps) {
  const [accountName, setAccountName] = useState("");
  const [secretKey, setSecretKey] = useState("");
  const [qrError, setQrError] = useState<string>("");
  const [scanning, setScanning] = useState(false);
  const nameInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    nameInputRef.current?.focus();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (accountName.trim() && secretKey.trim()) {
      onAdd(accountName.trim(), secretKey.trim());
    }
  };

  const handlePasteSecret = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        // Try to extract secret from otpauth URI
        const secretMatch = text.match(/secret=([A-Z2-7]+)/i);
        const issuerMatch = text.match(/issuer=([^&]+)/i);

        if (secretMatch) {
          setSecretKey(secretMatch[1]);
          if (issuerMatch && !accountName) {
            setAccountName(decodeURIComponent(issuerMatch[1]));
          }
        } else {
          setSecretKey(text.trim());
        }
      }
    } catch {
      // Clipboard access may fail
    }
  };

  /**
   * Python版 mfa_app.py の "Select QR Code" ボタンと同等の機能。
   * 画像ファイルを選択してQRコードから secret/issuer を抽出する。
   */
  const handleSelectQrCode = async () => {
    setQrError("");
    try {
      const filePath = await open({
        title: "Select QR Code Image",
        defaultPath: undefined,
        filters: [
          {
            name: "Image files",
            extensions: ["png", "jpg", "jpeg", "gif", "bmp"],
          },
        ],
        multiple: false,
        directory: false,
      });

      if (!filePath || typeof filePath !== "string") return;

      setScanning(true);
      const result = await invoke<QrCodeResult>("read_qr_code", {
        imagePath: filePath,
      });

      setSecretKey(result.secret);
      if (result.issuer && !accountName) {
        setAccountName(result.issuer);
      } else if (result.account && !accountName) {
        setAccountName(result.account);
      }
    } catch (err) {
      setQrError(typeof err === "string" ? err : `Error: ${err}`);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-sm">
        <h2 className="text-lg font-bold text-gray-800 mb-4">Add Account</h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Account Name
            </label>
            <input
              ref={nameInputRef}
              type="text"
              value={accountName}
              onChange={(e) => setAccountName(e.target.value)}
              className="input-field"
              placeholder="e.g., AWS, GitHub"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Secret Key
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={secretKey}
                onChange={(e) => setSecretKey(e.target.value)}
                className="input-field flex-1"
                placeholder="Base32 secret or otpauth URI"
              />
              <button
                type="button"
                onClick={handlePasteSecret}
                className="btn-secondary text-xs px-3"
                title="Paste from clipboard"
              >
                📋
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Paste a base32 secret key or an otpauth:// URI
            </p>
          </div>

          {/* QR コード画像読み取り */}
          <div className="mb-4">
            <button
              type="button"
              onClick={handleSelectQrCode}
              disabled={scanning}
              className="w-full btn-secondary text-sm disabled:opacity-50"
            >
              {scanning ? "Scanning..." : "📷 Select QR Code Image"}
            </button>
            {qrError && (
              <p className="text-xs text-red-600 mt-1">{qrError}</p>
            )}
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!accountName.trim() || !secretKey.trim()}
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Add
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddAccountDialog;
