import React from "react";

export function Button({
  children,
  variant = "default",
  size = "md",
  disabled = false,
  onClick,
  type = "button",
  title,
}) {
  const cls = [
    "btn",
    variant === "primary" && "btn-primary",
    variant === "success" && "btn-success",
    variant === "danger" && "btn-danger",
    variant === "ghost" && "btn-ghost",
    size === "sm" && "btn-sm",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={cls} disabled={disabled} onClick={onClick} type={type} title={title}>
      {children}
    </button>
  );
}
