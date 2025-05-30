// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import Image from "next/image";

import { cn } from "~/lib/utils";

export function FavIcon({
  className,
  url,
  title,
}: {
  className?: string;
  url: string;
  title?: string;
}) {
  const faviconUrl = new URL(url).origin + "/favicon.ico";
  const fallbackUrl = "https://perishablepress.com/wp/wp-content/images/2021/favicon-standard.png";

  return (
    <Image
      className={cn("bg-accent h-4 w-4 rounded-full shadow-sm", className)}
      width={16}
      height={16}
      src={faviconUrl}
      alt={title || "Favicon"}
      onError={(e) => {
        e.currentTarget.src = fallbackUrl;
      }}
    />
  );
}
