import { useState, useEffect, useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";
import { writeText } from "@tauri-apps/plugin-clipboard-manager";

interface TotpResult {
  code: string;
  seconds_remaining: number;
}

interface TOTPDisplayProps {
  accountName: string;
}

function TOTPDisplay({ accountName }: TOTPDisplayProps) {
  const [code, setCode] = useState<string>("");
  const [secondsRemaining, setSecondsRemaining] = useState<number>(30);
  const [copied, setCopied] = useState(false);

  const fetchCode = useCallback(async () => {
    try {
      const result = await invoke<TotpResult>("generate_totp_code", {
        accountName,
      });
      setCode(result.code);
      setSecondsRemaining(result.seconds_remaining);
    } catch (err) {
      console.error("Failed to generate TOTP:", err);
      setCode("Error");
    }
  }, [accountName]);

  useEffect(() => {
    fetchCode();
    const interval = setInterval(fetchCode, 1000);
    return () => clearInterval(interval);
  }, [fetchCode]);

  const handleCopy = async () => {
    if (code && code !== "Error") {
      try {
        await writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error("Failed to copy:", err);
      }
    }
  };

  // Handle Enter key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter") {
        handleCopy();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  });

  const progressPercentage = (secondsRemaining / 30) * 100;

  return (
    <div className="card mb-4">
      {/* Code Display */}
      <div className="text-center mb-4">
        <div className="text-5xl font-mono font-bold text-gray-800 tracking-wider mb-2">
          {code ? `${code.slice(0, 3)} ${code.slice(3)}` : "--- ---"}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-3">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-1000 ${
              secondsRemaining <= 5 ? "bg-red-500" : "bg-blue-500"
            }`}
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-1 text-center">
          Refreshing in {secondsRemaining}s
        </p>
      </div>

      {/* Copy Button */}
      <button
        onClick={handleCopy}
        className={`w-full py-3 rounded-lg font-medium transition-all duration-200 ${
          copied
            ? "bg-green-500 text-white"
            : "bg-blue-600 hover:bg-blue-700 text-white"
        }`}
      >
        {copied ? "✓ Copied!" : "Copy Code (Enter)"}
      </button>
    </div>
  );
}

export default TOTPDisplay;
