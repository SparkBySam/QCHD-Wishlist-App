import * as React from "react";

export interface StatCardProps {
  label: React.ReactNode;
  value: React.ReactNode;
  /** Orange value text — reserve for the number staff should act on (e.g. unhandled matches). */
  accent?: boolean;
}
