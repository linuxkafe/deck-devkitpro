import {
  PanelSection,
  PanelSectionRow,
  ToggleField,
  ButtonItem,
  staticClasses,
} from "@decky/ui";
import { callable, definePlugin, toaster } from "@decky/api";
import { Fragment, useEffect, useState } from "react";
import { FaContainer, FaDownload, FaTerminal, FaInfo } from "react-icons/fa";
import { t } from "./i18n";

type Status = {
  image_present: boolean;
  container_running: boolean;
  toolchain: {
    ok: boolean;
    version: string | null;
    output: string;
    error: string;
  };
  error: string;
};

type ToolchainInfo = {
  ok: boolean;
  version: string | null;
  output: string;
  error: string;
};

const StatusRow = ({ label, value }: { label: string; value: boolean }) => (
  <PanelSectionRow>
    <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
      {value ? "✅" : "❌"}
      {label}
    </span>
  </PanelSectionRow>
);

export default definePlugin(() => {
  const [status, setStatus] = useState<Status | null>(null);
  const [toolchain, setToolchain] = useState<ToolchainInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [pulling, setPulling] = useState(false);

  const refresh = async () => {
    try {
      const s = await callable<[], Status>("get_status")();
      setStatus(s);
      if (s.image_present) {
        const t = await callable<[], ToolchainInfo>("toolchain_info")();
        setToolchain(t);
      }
    } catch (err) {
      toaster.toast({ title: t("errors.status"), content: String(err), priority: "error" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, []);

  const handlePull = async () => {
    setPulling(true);
    try {
      const result = await callable<[], { ok: boolean; message: string }>("pull_image")();
      if (result.ok) {
        toaster.toast({ title: t("status.imagePulled"), content: result.message, priority: "success" });
        await refresh();
      } else {
        toaster.toast({ title: t("errors.pull"), content: result.error, priority: "error" });
      }
    } catch (err) {
      toaster.toast({ title: t("errors.pull"), content: String(err), priority: "error" });
    } finally {
      setPulling(false);
    }
  };

  if (loading) {
    return (
      <PanelSection title={t("title")}>
        <PanelSectionRow>Carregando...</PanelSectionRow>
      </PanelSection>
    );
  }

  if (!status) {
    return (
      <PanelSection title={t("title")}>
        <PanelSectionRow>{t("errors.noStatus")}</PanelSectionRow>
      </PanelSection>
    );
  }

  return (
    <Fragment>
      <PanelSection title={t("status.title")}>
        <StatusRow label={t("status.image")} value={status.image_present} />
        <StatusRow label={t("status.container")} value={status.container_running} />
        {toolchain && (
          <PanelSectionRow>
            <span>
              {t("status.toolchain")}: {toolchain.version || t("status.unknown")}
            </span>
          </PanelSectionRow>
        )}
      </PanelSection>

      <PanelSection title={t("actions.title")}>
        <PanelSectionRow>
          <button
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "8px 16px",
              background: "#22c55e",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: 500,
            }}
            onClick={handlePull}
            disabled={pulling}
          >
            <FaDownload size={14} />
            {pulling ? t("actions.pulling") : t("actions.pull")}
          </button>
        </PanelSectionRow>
      </PanelSection>

      {toolchain && toolchain.output && (
        <PanelSection title={t("details.title")}>
          <PanelSectionRow>
            <pre
              style={{
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                fontSize: "12px",
                fontFamily: "monospace",
                background: "#1a1a1a",
                padding: "8px",
                borderRadius: "4px",
                margin: 0,
                maxHeight: "200px",
                overflow: "auto",
              }}
            >
              {toolchain.output}
            </pre>
          </PanelSectionRow>
        </PanelSection>
      )}
    </Fragment>
  );
});