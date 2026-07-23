import React from "react";

export function Banner({ tone = "info", children }) {
  return <div className={`banner banner-${tone}`}>{children}</div>;
}
