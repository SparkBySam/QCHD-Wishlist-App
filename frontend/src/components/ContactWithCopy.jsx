import { useState } from "react";

function isEmail(contact) {
  return contact?.includes("@");
}

function CopyPhoneButton({ onCopy, copied, stopRowClick }) {
  async function handleClick(event) {
    if (stopRowClick) event.stopPropagation();
    await onCopy(event);
  }

  return (
    <button
      type="button"
      className={`copy-icon-btn${copied ? " copied" : ""}`}
      onClick={handleClick}
      aria-label={copied ? "Copied" : "Copy phone number"}
      title={copied ? "Copied" : "Copy phone number"}
    >
      {copied ? (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M20 6L9 17l-5-5"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ) : (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect
            x="9"
            y="9"
            width="13"
            height="13"
            rx="2"
            stroke="currentColor"
            strokeWidth="1.75"
          />
          <path
            d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
          />
        </svg>
      )}
    </button>
  );
}

export default function ContactWithCopy({ contact, stopRowClick = false }) {
  const [copied, setCopied] = useState(false);

  if (!contact) return "—";

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(contact);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard may be unavailable outside secure context.
    }
  }

  if (isEmail(contact)) {
    return (
      <a
        href={`mailto:${contact}`}
        onClick={stopRowClick ? (e) => e.stopPropagation() : undefined}
      >
        {contact}
      </a>
    );
  }

  return (
    <span
      className="contact-with-copy"
      onClick={stopRowClick ? (e) => e.stopPropagation() : undefined}
    >
      <a href={`tel:${contact.replace(/\D/g, "")}`}>{contact}</a>
      <CopyPhoneButton
        onCopy={handleCopy}
        copied={copied}
        stopRowClick={stopRowClick}
      />
    </span>
  );
}
