import * as React from "react";

export interface DetailCardProps {
  title: React.ReactNode;
  onClose?: () => void;
  children: React.ReactNode;
}

export interface DetailFieldProps {
  label: React.ReactNode;
  full?: boolean;
  children: React.ReactNode;
}
