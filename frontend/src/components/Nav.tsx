"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ProviderPicker } from "./ProviderPicker";

const LINKS = [
  { href: "/", label: "Reader", icon: "📖" },
  { href: "/chat", label: "Chat", icon: "💬" },
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 border-b border-borderc bg-[rgba(11,13,19,0.85)] backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-4">
        <Link
          href="/"
          className="flex items-center gap-2 whitespace-nowrap font-semibold tracking-tight"
        >
          <span className="grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-accent to-sky-500 text-sm shadow-[0_0_14px_var(--accent-glow)]">
            ✦
          </span>
          <span className="hidden lg:inline">help-me-learn</span>
        </Link>
        <nav className="flex gap-1">
          {LINKS.map(({ href, label, icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`rounded-lg px-3 py-1.5 text-sm transition-colors ${
                  active
                    ? "bg-surface-2 text-foreground shadow-[inset_0_0_0_1px_var(--border)]"
                    : "text-muted hover:text-foreground"
                }`}
              >
                <span className="mr-1.5">{icon}</span>
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="ml-auto">
          <ProviderPicker />
        </div>
      </div>
    </header>
  );
}
