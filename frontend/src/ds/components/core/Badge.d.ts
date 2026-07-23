import * as React from "react";

export interface BadgeProps {
  children: React.ReactNode;
  /** Maps directly to the app's status vocabulary. */
  tone?: "neutral" | "active" | "new" | "done" | "fulfilled" | "cancelled";
}
