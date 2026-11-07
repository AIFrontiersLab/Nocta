import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { formatScore } from "@/lib/format";
import type { Idea } from "@/lib/types";

export function HeroInvention({
  winner,
  prototypeStatus,
}: {
  winner?: Idea | null;
  prototypeStatus?: string;
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="card relative overflow-hidden p-8 md:p-10"
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(37,99,235,0.08),transparent_45%),radial-gradient(circle_at_bottom_left,rgba(8,145,178,0.08),transparent_40%)]" />
      <div className="relative">
        <div className="kicker">Last night&apos;s invention</div>
        <h2 className="mt-3 font-display text-4xl font-semibold md:text-5xl">
          {winner?.name || "Awaiting first run"}
        </h2>
        <p className="mt-3 max-w-3xl text-lg text-mute">{winner?.one_liner}</p>
        <div className="mt-6 flex flex-wrap items-center gap-3">
          <span className="score-pill">FutureLab Score {formatScore(winner?.score)} / 100</span>
          <Badge>
            Prototype: {prototypeStatus === "built" ? "BUILT" : prototypeStatus || "—"}
          </Badge>
          {winner?.is_demo && <Badge tone="violet">Demo data</Badge>}
        </div>
        <div className="mt-6 flex flex-wrap gap-3">
          {winner && (
            <Link
              href={`/ideas/${winner.id}`}
              className="inline-flex items-center gap-2 rounded-full bg-ink px-5 py-2.5 text-sm font-semibold text-white"
            >
              Explore Invention <ArrowRight size={16} />
            </Link>
          )}
          <Link
            href="/prototypes"
            className="inline-flex items-center gap-2 rounded-full border border-line px-5 py-2.5 text-sm font-semibold"
          >
            View Prototype
          </Link>
        </div>
        {winner?.why_now && (
          <div className="mt-8 rounded-2xl border border-line bg-white/70 p-5">
            <div className="kicker">Why now</div>
            <p className="mt-2 text-mute">{winner.why_now}</p>
          </div>
        )}
      </div>
    </motion.section>
  );
}
