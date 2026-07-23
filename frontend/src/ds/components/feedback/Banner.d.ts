import * as React from "react";

export interface BannerProps {
  tone?: "error" | "success" | "info" | "warning" | "subtle";
  children: React.ReactNode;
}
