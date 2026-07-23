import * as React from "react";

export interface DataTableColumn<T = any> {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (row: T) => React.ReactNode;
}

export interface DataTableProps<T = any> {
  columns: DataTableColumn<T>[];
  rows: T[];
  sortKey?: string;
  sortDir?: "asc" | "desc";
  onSort?: (key: string) => void;
  onRowClick?: (row: T) => void;
  selectedId?: string | number;
  /** Field on each row used as the React key / selection id. Default "id". */
  rowKey?: string;
}
