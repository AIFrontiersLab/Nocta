import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

type Prototype = {
  id: string;
  name?: string;
  idea_id?: string;
  status?: string;
  path?: string;
  github_url?: string;
};

export function PrototypeCard({ prototype }: { prototype: Prototype }) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold">{prototype.name || prototype.id}</h3>
          {prototype.path && <p className="mt-1 text-xs text-mute">{prototype.path}</p>}
        </div>
        <Badge tone="success">{prototype.status || "built"}</Badge>
      </div>
      <div className="mt-4 flex flex-wrap gap-3 text-sm">
        {prototype.idea_id && (
          <Link href={`/ideas/${prototype.idea_id}`} className="font-semibold text-electric">
            View idea
          </Link>
        )}
        {prototype.github_url && (
          <a href={prototype.github_url} target="_blank" rel="noreferrer" className="font-semibold text-electric">
            GitHub
          </a>
        )}
      </div>
    </Card>
  );
}
