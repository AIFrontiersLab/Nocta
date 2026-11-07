import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

type Convergence = {
  id?: string;
  title?: string;
  nodes?: string[];
  strength?: number;
  summary?: string;
};

export function ConvergenceMap({ items }: { items: Convergence[] }) {
  if (!items.length) {
    return <p className="text-sm text-mute">No convergences detected yet.</p>;
  }
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {items.map((item, idx) => (
        <Card key={item.id || idx}>
          <h3 className="text-lg font-semibold">{item.title || "Convergence"}</h3>
          {item.summary && <p className="mt-2 text-sm text-mute">{item.summary}</p>}
          <div className="mt-4 flex flex-wrap gap-2">
            {(item.nodes || []).map((node) => (
              <Badge key={node} tone="info">
                {node}
              </Badge>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}
