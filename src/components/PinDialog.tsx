import { useState, useRef, useEffect } from "react";

interface PinDialogProps {
  isSetup: boolean;
  onSubmit: (pin: string) => void;
  error: string;
  onErrorClear: () => void;
}

function PinDialog({ isSetup, onSubmit, error, onErrorClear }: PinDialogProps) {
  const [pin, setPin] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (pin.length >= 8 && /^\d+$/.test(pin)) {
      onSubmit(pin);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Only allow digits
    if (/^\d*$/.test(value)) {
      setPin(value);
      if (error) onErrorClear();
    }
  };

  const isValid = pin.length >= 8 && /^\d+$/.test(pin);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="card w-full max-w-sm">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-1">
            🦙 Magical Flying Alpaca
          </h1>
          <p className="text-sm text-gray-500">
            {isSetup ? "Set your PIN to get started" : "こんにちは"}
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {isSetup ? "Enter new PIN (8+ digits)" : "Enter PIN"}
            </label>
            <input
              ref={inputRef}
              type="password"
              value={pin}
              onChange={handleChange}
              className="input-field text-center text-2xl tracking-widest"
              placeholder="••••••••"
              maxLength={20}
              autoFocus
            />
          </div>

          {isSetup && (
            <p className="text-xs text-gray-500 mb-4">
              Choose a memorable 8+ digit PIN to secure your accounts.
            </p>
          )}

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={!isValid}
            className={`w-full py-3 rounded-lg font-medium transition-colors duration-200 ${
              isValid
                ? "bg-blue-600 hover:bg-blue-700 text-white"
                : "bg-gray-200 text-gray-400 cursor-not-allowed"
            }`}
          >
            {isSetup ? "Set PIN" : "Unlock"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default PinDialog;
