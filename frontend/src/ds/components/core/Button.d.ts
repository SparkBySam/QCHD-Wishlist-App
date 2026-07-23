import * as React from "react";

export interface ButtonProps {
  children: React.ReactNode;
  /** Visual weight — default is the neutral surface button used for most actions. */
  variant?: "default" | "primary" | "success" | "danger" | "ghost";
  size?: "md" | "sm";
  disabled?: boolean;
  onClick?: (e: React.MouseEvent) => void;
  type?: "button" | "submit";
  title?: string;
}
