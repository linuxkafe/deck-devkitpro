// UI components for DevKitPro Deck plugin

import { PanelSectionRow } from "@decky/ui";
import { ReactNode } from "react";

export const FocusBtn = ({ children, onClick, disabled }: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}) => (
  <button
    style={{
      display: "flex",
      alignItems: "center",
      gap: "8px",
      padding: "8px 16px",
      background: disabled ? "#555" : "#22c55e",
      color: "#fff",
      border: "none",
      borderRadius: "6px",
      cursor: disabled ? "not-allowed" : "pointer",
      fontSize: "14px",
      fontWeight: 500,
    }}
    onClick={onClick}
    disabled={disabled}
  >
    {children}
  </button>
);

export const StatusBadge = ({ ok }: { ok: boolean }) => (
  <span style={{ color: ok ? "#22c55e" : "#ef4444" }}>
    {ok ? "✅" : "❌"}
  </span>
);