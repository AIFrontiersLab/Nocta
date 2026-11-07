import clsx from "clsx";

export function Card({
  children,
  className,
  hover = false,
}: {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}) {
  return (
    <div className={clsx("card p-5", hover && "transition hover:-translate-y-0.5", className)}>
      {children}
    </div>
  );
}
