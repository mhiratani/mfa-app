import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import PinDialog from "./components/PinDialog";
import MainView from "./components/MainView";

type AppView = "loading" | "pin-setup" | "pin-verify" | "main";

function App() {
  const [view, setView] = useState<AppView>("loading");
  const [error, setError] = useState<string>("");

  useEffect(() => {
    checkPinStatus();
  }, []);

  const checkPinStatus = async () => {
    try {
      const exists = await invoke<boolean>("pin_exists");
      setView(exists ? "pin-verify" : "pin-setup");
    } catch (err) {
      setError(`Error: ${err}`);
    }
  };

  const handlePinSet = async (pin: string) => {
    try {
      await invoke<boolean>("set_pin", { pin });
      setView("main");
      setError("");
    } catch (err) {
      setError(`Failed to set PIN: ${err}`);
    }
  };

  const handlePinVerify = async (pin: string) => {
    try {
      const result = await invoke<boolean>("verify_pin", { pin });
      if (result) {
        setView("main");
        setError("");
      } else {
        setError("Incorrect PIN. Please try again.");
      }
    } catch (err) {
      setError(`Verification error: ${err}`);
    }
  };

  if (view === "loading") {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (view === "pin-setup" || view === "pin-verify") {
    return (
      <PinDialog
        isSetup={view === "pin-setup"}
        onSubmit={view === "pin-setup" ? handlePinSet : handlePinVerify}
        error={error}
        onErrorClear={() => setError("")}
      />
    );
  }

  return <MainView />;
}

export default App;
