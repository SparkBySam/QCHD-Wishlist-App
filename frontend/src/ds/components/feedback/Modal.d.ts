import * as React from "react";

export interface ModalProps {
  open: boolean;
  title?: React.ReactNode;
  children: React.ReactNode;
  /** Right-aligned action buttons, e.g. <Button variant="ghost">Cancel</Button> <Button variant="danger">Delete</Button> */
  actions?: React.ReactNode;
  onClose: () => void;
}
