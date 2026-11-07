import { Shell } from "@/components/layout/Shell";

export default function SettingsPage() {
  return (
    <Shell>
      <h1 className="font-display text-4xl font-semibold">Settings</h1>
      <div className="mt-6 card p-6 text-mute">
        Configure limits, model routing, prototype thresholds, and Hermes/WhatsApp delivery in <code>.env</code> at the project root.
        Nocta reuses the existing <code>hermes send</code> integration — it does not create a duplicate WhatsApp client.
      </div>
    </Shell>
  );
}
