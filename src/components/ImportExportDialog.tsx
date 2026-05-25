import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { save, open, ask } from "@tauri-apps/plugin-dialog";
import { writeTextFile, readTextFile } from "@tauri-apps/plugin-fs";

interface ImportExportDialogProps {
  mode: "import" | "export";
  onClose: () => void;
  onMessage: (text: string, type: "success" | "error") => void;
}

function ImportExportDialog({ mode, onClose, onMessage }: ImportExportDialogProps) {
  const [key, setKey] = useState("");
  const [loading, setLoading] = useState(false);

  const isKeyValid = () => {
    if (mode === "export") {
      return (
        key.length >= 16 &&
        /[a-zA-Z]/.test(key) &&
        /\d/.test(key) &&
        /[!@#$%^&*(),.?":{}|<>]/.test(key)
      );
    }
    return key.length > 0;
  };

  const getStrength = () => {
    let score = 0;
    if (key.length >= 16) score++;
    if (/[a-zA-Z]/.test(key)) score++;
    if (/\d/.test(key)) score++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(key)) score++;
    return score;
  };

  const handleExport = async () => {
    if (!isKeyValid()) return;
    setLoading(true);

    try {
      const encryptedData = await invoke<string>("export_accounts", {
        exportKey: key,
      });

      const filePath = await save({
        defaultPath: "AlpacaBackup.enc",
        filters: [{ name: "Encrypted Backup", extensions: ["enc"] }],
      });

      if (filePath) {
        await writeTextFile(filePath, encryptedData);
        onMessage("Accounts exported successfully", "success");
        onClose();
      }
    } catch (err) {
      onMessage(`Export failed: ${err}`, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!key) return;
    setLoading(true);

    try {
      const filePath = await open({
        filters: [
          // Python版 (.json) と新形式 (.enc) の両方をサポート
          { name: "Backup files", extensions: ["enc", "json"] },
          { name: "All files", extensions: ["*"] },
        ],
      });

      if (filePath) {
        const encryptedData = await readTextFile(filePath as string);

        // Python版互換: 既存アカウントを上書きするか確認
        // Tauri 2 の WebView では window.confirm が非ブロッキングのため
        // dialog プラグインの ask() を使う
        const overwrite = await ask(
          "Do you want to overwrite your existing accounts with the imported data?\n" +
            "(Yes: overwrite all / No: merge with existing)",
          {
            title: "Import Accounts",
            kind: "warning",
            okLabel: "Overwrite",
            cancelLabel: "Merge",
          }
        );

        const importedNames = await invoke<string[]>("import_accounts", {
          encryptedData,
          importKey: key,
          overwrite: Boolean(overwrite),
        });
        onMessage(
          `Imported ${importedNames.length} account(s) successfully`,
          "success"
        );
        onClose();
      }
    } catch (err) {
      onMessage(`Import failed: ${err}`, "error");
    } finally {
      setLoading(false);
    }
  };

  const strength = getStrength();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-sm">
        <h2 className="text-lg font-bold text-gray-800 mb-4">
          {mode === "export" ? "Export Accounts" : "Import Accounts"}
        </h2>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {mode === "export" ? "Set Export Key" : "Enter Import Key"}
          </label>
          <input
            type="password"
            value={key}
            onChange={(e) => setKey(e.target.value)}
            className="input-field"
            placeholder={
              mode === "export"
                ? "16+ chars with letters, numbers, symbols"
                : "Enter the key used during export"
            }
            autoFocus
          />
        </div>

        {mode === "export" && (
          <div className="mb-4">
            {/* Strength indicator */}
            <div className="flex gap-1 mb-2">
              {[1, 2, 3, 4].map((level) => (
                <div
                  key={level}
                  className={`h-1.5 flex-1 rounded ${
                    strength >= level
                      ? level <= 1
                        ? "bg-red-400"
                        : level <= 2
                        ? "bg-orange-400"
                        : level <= 3
                        ? "bg-yellow-400"
                        : "bg-green-500"
                      : "bg-gray-200"
                  }`}
                />
              ))}
            </div>

            {/* Requirements */}
            <div className="text-xs space-y-1">
              <p className={key.length >= 16 ? "text-green-600" : "text-gray-400"}>
                {key.length >= 16 ? "✅" : "❌"} 16+ characters
              </p>
              <p className={/[a-zA-Z]/.test(key) ? "text-green-600" : "text-gray-400"}>
                {/[a-zA-Z]/.test(key) ? "✅" : "❌"} Contains letters
              </p>
              <p className={/\d/.test(key) ? "text-green-600" : "text-gray-400"}>
                {/\d/.test(key) ? "✅" : "❌"} Contains numbers
              </p>
              <p className={/[!@#$%^&*(),.?":{}|<>]/.test(key) ? "text-green-600" : "text-gray-400"}>
                {/[!@#$%^&*(),.?":{}|<>]/.test(key) ? "✅" : "❌"} Contains special characters
              </p>
            </div>
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary flex-1"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={mode === "export" ? handleExport : handleImport}
            disabled={!isKeyValid() || loading}
            className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading
              ? "Processing..."
              : mode === "export"
              ? "Export"
              : "Import"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ImportExportDialog;
