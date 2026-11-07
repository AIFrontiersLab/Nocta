import clsx from "clsx";

const tones: Record<string, string> = {
  default: "bg-slate-100 text-ink",
  success: "bg-emerald-50 text-emerald-700",
  warn: "bg-amber-50 text-amber-700",
  danger: "bg-rose-50 text-rose-700",
  info: "bg-blue-50 text-electric",
  violet: "bg-violet/10 text-violet",
};

export function Badge({
  children,
  tone = "default",
  className,
}: {
  children: React.ReactNode;
  tone?: keyof typeof tones;
  className?: string;
}) {
  return (
    <span className={clsx("inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold", tones[tone], className)}>
      {children}
    </span>
  );
}
