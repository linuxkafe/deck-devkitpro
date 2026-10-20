// i18n — Internationalization for DevKitPro Deck plugin
// English (default) and Portuguese (auto when system locale is pt-*)

import { getLanguage } from "@decky/api";

let currentLang = "en";

export function setLanguage(lang: string) {
  currentLang = lang;
}

// Auto-detect on init
try {
  const sysLang = navigator.language || "en";
  if (sysLang.startsWith("pt")) {
    currentLang = "pt";
  }
} catch {
  // ignore — running outside browser
}

const strings: Record<string, Record<string, string>> = {
  en: {
    title: "DevKitPro Deck",
    "status.title": "Status",
    "status.image": "Image",
    "status.container": "Container",
    "status.toolchain": "Toolchain",
    "status.unknown": "Unknown",
    "status.imagePulled": "Image pulled",
    "actions.title": "Actions",
    "actions.pull": "Pull Image",
    "actions.pulling": "Pulling...",
    "details.title": "Details",
    "errors.status": "Status error",
    "errors.pull": "Pull error",
    "errors.noStatus": "No status available",
  },
  pt: {
    title: "DevKitPro Deck",
    "status.title": "Estado",
    "status.image": "Imagem",
    "status.container": "Container",
    "status.toolchain": "Toolchain",
    "status.unknown": "Desconhecido",
    "status.imagePulled": "Imagem actualizada",
    "actions.title": "Acções",
    "actions.pull": "Obter Imagem",
    "actions.pulling": "A obter...",
    "details.title": "Detalhes",
    "errors.status": "Erro de estado",
    "errors.pull": "Erro ao obter",
    "errors.noStatus": "Estado indisponível",
  },
};

export function t(key: string): string {
  return strings[currentLang]?.[key] || strings.en[key] || key;
}

export function isPt(): boolean {
  return currentLang === "pt";
}