import * as React from "react";

export interface FieldProps {
  label: React.ReactNode;
  /** Span the full width of a .form-grid row — used for notes/textarea fields. */
  full?: boolean;
  children: React.ReactNode;
}
