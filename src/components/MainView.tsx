import { useState, useEffect, useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";
import { ask } from "@tauri-apps/plugin-dialog";
import TOTPDisplay from "./TOTPDisplay";
import AddAccountDialog from "./AddAccountDialog";
import ImportExportDialog from "./ImportExportDialog";

function MainView() {
  const [accounts, setAccounts] = useState<string[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<string>("");
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showImportExport, setShowImportExport] = useState<"import" | "export" | null>(null);
  const [message, setMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);

  const loadAccounts = useCallback(async () => {
    try {
      const accountList = await invoke<string[]>("get_accounts");
      setAccounts(accountList);
      if (accountList.length > 0 && !selectedAccount) {
        setSelectedAccount(accountList[0]);
      }
    } catch (err) {
      console.error("Failed to load accounts:", err);
    }
  }, [selectedAccount]);

  useEffect(() => {
    loadAccounts();
  }, [loadAccounts]);

  const handleAddAccount = async (name: string, secret: string) => {
    try {
      await invoke<boolean>("add_account", {
        accountName: name,
        secretKey: secret,
      });
      await loadAccounts();
      setSelectedAccount(name);
      setShowAddDialog(false);
      showMessage("Account added successfully", "success");
    } catch (err) {
      showMessage(`Failed to add account: ${err}`, "error");
    }
  };

  const handleRemoveAccount = async () => {
    if (!selectedAccount) return;

    // Tauri 2 の WebView では window.confirm が非ブロッキングのため
    // dialog プラグインの ask() を使う
    const confirmed = await ask(
      `Are you sure you want to remove "${selectedAccount}"?`,
      {
        title: "Remove Account",
        kind: "warning",
        okLabel: "Remove",
        cancelLabel: "Cancel",
      }
    );
    if (!confirmed) return;

    try {
      await invoke<boolean>("remove_account", { accountName: selectedAccount });
      const newAccounts = accounts.filter((a) => a !== selectedAccount);
      setAccounts(newAccounts);
      setSelectedAccount(newAccounts.length > 0 ? newAccounts[0] : "");
      showMessage("Account removed", "success");
    } catch (err) {
      showMessage(`Failed to remove account: ${err}`, "error");
    }
  };

  const handleMoveAccount = async (direction: "up" | "down") => {
    if (!selectedAccount) return;
    const currentIndex = accounts.indexOf(selectedAccount);
    if (currentIndex === -1) return;

    const newIndex = direction === "up" ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= accounts.length) return;

    // Swap positions
    const newAccounts = [...accounts];
    [newAccounts[currentIndex], newAccounts[newIndex]] = [newAccounts[newIndex], newAccounts[currentIndex]];

    try {
      await invoke<boolean>("reorder_accounts", { accountNames: newAccounts });
      setAccounts(newAccounts);
    } catch (err) {
      showMessage(`Failed to reorder: ${err}`, "error");
    }
  };

  const showMessage = (text: string, type: "success" | "error") => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 3000);
  };

  const selectedIndex = accounts.indexOf(selectedAccount);
  const isFirst = selectedIndex <= 0;
  const isLast = selectedIndex >= accounts.length - 1;

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="text-center mb-4">
          <h1 className="text-xl font-bold text-gray-800">
            🦙 Magical Flying Alpaca
          </h1>
        </div>

        {/* Message */}
        {message && (
          <div
            className={`mb-4 p-3 rounded-lg text-sm ${
              message.type === "success"
                ? "bg-green-50 border border-green-200 text-green-700"
                : "bg-red-50 border border-red-200 text-red-700"
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Account Selector */}
        <div className="card mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Account
          </label>
          <div className="flex gap-2 items-center">
            <select
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="input-field flex-1"
            >
              {accounts.length === 0 && (
                <option value="">No accounts</option>
              )}
              {accounts.map((account) => (
                <option key={account} value={account}>
                  {account}
                </option>
              ))}
            </select>
            <button
              onClick={() => handleMoveAccount("up")}
              disabled={isFirst || accounts.length <= 1}
              className="px-2 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors duration-200 disabled:opacity-30 disabled:cursor-not-allowed text-sm font-bold"
              title="Move up"
            >
              ▲
            </button>
            <button
              onClick={() => handleMoveAccount("down")}
              disabled={isLast || accounts.length <= 1}
              className="px-2 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors duration-200 disabled:opacity-30 disabled:cursor-not-allowed text-sm font-bold"
              title="Move down"
            >
              ▼
            </button>
          </div>
        </div>

        {/* TOTP Display */}
        {selectedAccount && <TOTPDisplay accountName={selectedAccount} />}

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3 mb-3">
          <button
            onClick={() => setShowAddDialog(true)}
            className="btn-primary text-sm"
          >
            Add Account
          </button>
          <button
            onClick={handleRemoveAccount}
            disabled={!selectedAccount}
            className="btn-danger text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Remove Account
          </button>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => setShowImportExport("export")}
            disabled={accounts.length === 0}
            className="btn-secondary text-sm disabled:opacity-50"
          >
            Export
          </button>
          <button
            onClick={() => setShowImportExport("import")}
            className="btn-secondary text-sm"
          >
            Import
          </button>
        </div>
      </div>

      {/* Dialogs */}
      {showAddDialog && (
        <AddAccountDialog
          onAdd={handleAddAccount}
          onClose={() => setShowAddDialog(false)}
        />
      )}

      {showImportExport && (
        <ImportExportDialog
          mode={showImportExport}
          onClose={() => {
            setShowImportExport(null);
            loadAccounts();
          }}
          onMessage={showMessage}
        />
      )}
    </div>
  );
}

export default MainView;
