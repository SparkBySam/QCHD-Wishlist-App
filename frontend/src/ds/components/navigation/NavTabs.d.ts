import * as React from "react";

export interface NavTabsItem {
  id: string;
  label: string;
}

export interface NavTabsProps {
  items: NavTabsItem[];
  activeId: string;
  onChange: (id: string) => void;
}
