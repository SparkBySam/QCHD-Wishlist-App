import * as React from "react";

export interface PanelProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  /** Right-aligned toolbar contents — search, filters, action buttons. */
  toolbar?: React.ReactNode;
  children: React.ReactNode;
}
