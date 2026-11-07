import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { FlaskConical } from "lucide-react";

const links = [
  ["Home", "/"],
  ["Signals", "/signals"],
  ["Convergences", "/convergences"],
  ["Experiments", "/experiments"],
  ["Ideas", "/ideas"],
  ["Prototypes", "/prototypes"],
  ["Resurrections", "/resurrections"],
  ["Memory", "/memory"],
  ["Runs", "/runs"],
  ["Analytics", "/analytics"],
  ["Settings", "/settings"],
];

export function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-line/80 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-6 py-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-electric to-cyan text-white">
              <FlaskConical size={18} />
            </div>
            <div>
              <div className="font-display text-lg font-semibold">Vectra FutureLab</div>
              <div className="text-xs text-mute">Invent tomorrow while you sleep.</div>
            </div>
          </Link>
          <nav className="hidden flex-wrap items-center gap-1 lg:flex">
            {links.map(([label, href]) => (
              <Link
                key={href}
                href={href}
                className={clsx(
                  "rounded-full px-3 py-1.5 text-sm transition",
                  pathname === href ? "bg-ink text-white" : "text-mute hover:bg-slate-100 hover:text-ink",
                )}
              >
                {label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
    </div>
  );
}
