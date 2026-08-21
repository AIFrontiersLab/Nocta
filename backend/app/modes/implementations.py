from __future__ import annotations

from app.llm.schemas import IdeaDraft
from app.modes.base import ModeContext
from app.modes.catalog import primitive_catalog, theme_inventions


def _from_catalog(items: list[dict], mode: str) -> list[IdeaDraft]:
    drafts = []
    for item in items:
        drafts.append(
            IdeaDraft(
                name=item["name"],
                one_liner=item["one_liner"],
                problem=item["problem"],
                customer=item["customer"],
                future_thesis=item.get("future_thesis", ""),
                technology_convergence=item.get("technology_convergence", []),
                why_now=item.get("why_now", ""),
                why_difficult_before=item.get("why_difficult_before", ""),
                what_recently_changed=item.get("what_recently_changed", ""),
                current_alternatives=item.get("current_alternatives", []),
                novelty=item.get("novelty", ""),
                potential_moat=item.get("potential_moat", ""),
                mvp=item.get("mvp", ""),
                architecture=item.get("architecture", ""),
                risks=item.get("risks", []),
                unknowns=item.get("unknowns", []),
                why_may_win=item.get("why_may_win", ""),
                why_may_fail=item.get("why_may_fail", ""),
                market=item.get("market", ""),
                first_customer=item.get("first_customer", item["customer"]),
                product=item.get("product", item["one_liner"]),
                assumptions=item.get("assumptions", []),
                signal_bias=float(item.get("_signal_bias") or item.get("signal_bias") or 0.0),
            )
        )
    return drafts


class MissingPrimitiveMode:
    id = "missing-primitive"
    name = "Missing Primitive Detector"
    question = "What foundational capability will this ecosystem eventually require that does not yet exist?"

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]:
        theme = ctx.theme or "Autonomous AI Agents"
        return _from_catalog(primitive_catalog(theme, ctx.signals, ctx.convergences), self.id)


class InventionLabMode:
    id = "invention-lab"
    name = "Autonomous Invention Lab"
    question = "What useful thing has not been invented yet?"

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]:
        return _from_catalog(theme_inventions(ctx.theme or "human coordination", ctx.signals), self.id)


class FutureProblemMode:
    id = "future-problem"
    name = "Future Problem Generator"
    question = "What important problems may exist 2–5 years from now?"

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]:
        items = [
            {
                "name": "Permission Exhaustion Desk",
                "one_liner": "A workplace product for humans drowning in agent-generated approval requests.",
                "problem": "By 2029, knowledge workers spend more time ratifying agent actions than doing original work.",
                "customer": "Operations leads at companies that deployed internal agents widely.",
                "future_thesis": "Agent productivity creates a new bottleneck: human attestation fatigue.",
                "technology_convergence": ["Authorization", "Agent Identity", "Computer Use"],
                "why_now": "Internal agents are being connected to real systems faster than approval UX is being redesigned.",
                "why_difficult_before": "There were not enough autonomous actions to create approval fatigue.",
                "what_recently_changed": "Computer-use agents can now operate existing software.",
                "current_alternatives": ["Slack approvals", "Okta workflows", "ServiceNow tickets"],
                "novelty": "Treats human attention as the scarce resource in an agent-heavy org, not model quality.",
                "potential_moat": "Policy graph + attested action history across tools.",
                "mvp": "Inbox of proposed agent actions with batch-risk grouping and one-shot policy promotion.",
                "architecture": "Action bus, risk classifier, policy compiler, human inbox, audit log.",
                "risks": ["Incumbent ITSM vendors add this as a feature"],
                "unknowns": ["How fast approval volume actually grows"],
                "why_may_win": "The pain is downstream of a trend already in motion.",
                "why_may_fail": "Companies may simply restrict agents instead of buying a new desk.",
                "market": "Enterprise IT / GRC adjacency",
                "first_customer": "A 400-person company that already has 20 internal agents in production",
                "product": "A control surface for agent-generated work, not another chatbot.",
            },
            {
                "name": "Synthetic Provenance Bureau",
                "one_liner": "A verification layer for media, documents, and agent artifacts as synthetic content becomes default.",
                "problem": "In 2–5 years, 'is this real' is a daily operational question, not a media curiosity.",
                "customer": "Insurers, journalists, and procurement teams authenticating incoming artifacts.",
                "future_thesis": "Cheap generation without cheap verification breaks institutions.",
                "technology_convergence": ["Persistent Memory", "Agent Identity", "Small Models"],
                "why_now": "Generation quality crossed the casual-inspection threshold; provenance standards are still fragmented.",
                "why_difficult_before": "Synthetic media was obviously fake or expensive.",
                "what_recently_changed": "On-device generation plus agent-authored documents.",
                "current_alternatives": ["C2PA pilots", "manual review", "watermarking"],
                "novelty": "Focuses on operational artifact streams (invoices, claims, field photos), not social feeds.",
                "potential_moat": "Corpus of attested real-world capture devices and agent signers.",
                "mvp": "API that scores provenance of an uploaded document/photo against known capture and signer graphs.",
                "architecture": "Ingest, signature graph, model-origin heuristics, decision API, auditor UI.",
                "risks": ["Standards bodies make a generic bureau unnecessary"],
                "unknowns": ["Willingness to pay vs. treating as public infrastructure"],
                "why_may_win": "High-stakes workflows cannot wait for perfect global standards.",
                "why_may_fail": "If browsers and cameras ship this natively, independent bureaus shrink.",
                "market": "Insurance + compliance tooling",
                "first_customer": "Claims ops at a regional insurer",
                "product": "Provenance scoring for operational artifacts.",
            },
        ]
        return _from_catalog(items, self.id)


class TechnologyCollisionMode:
    id = "technology-collision"
    name = "Technology Collision Machine"
    question = "What products become possible only because unrelated technologies now converge?"

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]:
        if ctx.convergences:
            items = []
            for conv in ctx.convergences[:6]:
                nodes = conv.get("nodes") or []
                name = " × ".join(nodes[:3]) + " Operator"
                items.append(
                    {
                        "name": name[:80],
                        "one_liner": conv.get("opportunities", ["A product at this intersection."])[0],
                        "problem": conv.get("thesis") or "Capabilities exist separately; the joint product does not.",
                        "customer": "Teams already using at least one of the colliding technologies in production.",
                        "future_thesis": conv.get("why_connect") or "",
                        "technology_convergence": nodes,
                        "why_now": "These technologies started showing up in the same signal clusters this cycle.",
                        "why_difficult_before": "At least one of the ingredients was too weak, expensive, or unstandardized.",
                        "what_recently_changed": "Signal cluster formed across independent sources.",
                        "current_alternatives": ["Stitching tools together manually"],
                        "novelty": "The product is the collision, not an incremental feature in one category.",
                        "potential_moat": "Workflow data at the intersection.",
                        "mvp": "A narrow demo that only works if all colliding capabilities are present.",
                        "architecture": "Adapters for each capability + a joint orchestration core.",
                        "risks": ["One of the technologies remains a toy"],
                        "unknowns": ["Which node is actually the bottleneck"],
                        "why_may_win": "Category does not yet have an incumbent owner.",
                        "why_may_fail": "The collision is interesting but not a job-to-be-done.",
                        "market": "Emerging infrastructure",
                        "first_customer": "A lab or startup already combining two of the three",
                        "product": conv.get("title"),
                    }
                )
            return _from_catalog(items, self.id)
        return InventionLabMode().generate(ctx)


class BackcasterMode:
    id = "2035-backcaster"
    name = "2035 Product Backcaster"
    question = "What 2035 product can have a credible Version 0.1 built today?"

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]:
        items = [
            {
                "name": "Personal World Model",
                "one_liner": "A continuously updated private simulation of a person's work, home, and commitments.",
                "problem": "Software still stores files and messages, not a living model of a person's world.",
                "customer": "Founders and operators who already run their life through agents and calendars.",
                "future_thesis": "By 2035 millions use a private world model the way they used a smartphone home screen in 2015.",
                "technology_convergence": ["Persistent Memory", "World Models", "Small Models"],
                "why_now": "Long-context models and local SLMs make a private continuously updated model feasible.",
                "why_difficult_before": "Memory was session-based; on-device models were too weak; sensors were siloed.",
                "what_recently_changed": "Local 9B-class models and cheaper multimodal understanding.",
                "current_alternatives": ["Note apps", "personal CRMs", "chat memory"],
                "novelty": "The product is a world model, not a document store with embeddings.",
                "potential_moat": "Years of private state that cannot be re-scraped.",
                "mvp": "A local daemon that maintains a structured model of projects, people, and open loops, queryable by agents.",
                "architecture": "Local event ingest, entity graph, daily consolidation, agent query API, privacy firewall.",
                "risks": ["Feels like surveillance to the owner"],
                "unknowns": ["Whether users will tolerate the setup cost"],
                "why_may_win": "Every agent is more useful with a persistent world than with chat history.",
                "why_may_fail": "OS vendors ship a weaker version for free.",
                "market": "Personal infrastructure",
                "first_customer": "Power users already running local models",
                "product": "A private, queryable world model with Version 0.1 as a local graph + daily brief.",
            }
        ]
        return _from_catalog(items, self.id)


class AlienDesignerMode:
    id = "alien-designer"
    name = "Alien Product Designer"
    question = "If a category had never existed, what would we invent now?"

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]:
        items = [
            {
                "name": "Intent Mail",
                "one_liner": "A replacement for email designed as if AI agents had existed first.",
                "problem": "Email is a human inbox pretending to be a protocol. Agents drown in it.",
                "customer": "Teams whose work is already half-delegated to agents.",
                "future_thesis": "Messaging becomes attested intents and negotiated outcomes, not threads.",
                "technology_convergence": ["Agent Identity", "Authorization", "Persistent Memory"],
                "why_now": "Agents can draft, file, and act — but they still speak SMTP.",
                "why_difficult_before": "No identity for non-human senders; no shared memory of commitments.",
                "what_recently_changed": "Agent protocols and structured tool use.",
                "current_alternatives": ["Gmail + filters", "Superhuman", "Slack"],
                "novelty": "Starts from attested intents rather than messages.",
                "potential_moat": "Protocol + identity graph.",
                "mvp": "A client where humans and agents exchange signed intents with expiry, not infinite threads.",
                "architecture": "Intent objects, signer registry, negotiation engine, human glance UI.",
                "risks": ["Network effects of email are enormous"],
                "unknowns": ["Cold-start: who is on the other side?"],
                "why_may_win": "Agent-native communication needs a different primitive than inbox.",
                "why_may_fail": "Everyone keeps wrapping Gmail.",
                "market": "Communication infrastructure",
                "first_customer": "A 20-person AI-native company",
                "product": "Attested intents instead of email threads.",
            }
        ]
        return _from_catalog(items, self.id)


class WhatComesAfterMode:
    id = "what-comes-after"
    name = "What Comes After X?"
    question = "What eventually replaces an important existing category?"

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]:
        items = [
            {
                "name": "Ambient Memory Layer",
                "one_liner": "What comes after the notes app: a continuous memory substrate for humans and agents.",
                "problem": "Knowledge work still depends on people remembering to write things down.",
                "customer": "Researchers, founders, and field technicians who cannot stop to take notes.",
                "future_thesis": "The notes app is a transitional fossil. Memory becomes infrastructure.",
                "technology_convergence": ["Voice AI", "Persistent Memory", "Smart Glasses"],
                "why_now": "Always-on capture + local models make continuous memory less science-fiction.",
                "why_difficult_before": "Capture was socially unacceptable and models could not structure it.",
                "what_recently_changed": "Better on-device speech and cheaper local memory models.",
                "current_alternatives": ["Otter", "Notion", "Apple Notes", "Limitless"],
                "novelty": "Treats memory as a substrate other software queries, not a destination app.",
                "potential_moat": "Personal memory graph + retrieval quality over years.",
                "mvp": "A local capture-to-graph pipeline with an API other agents can query with consent.",
                "architecture": "Capture daemons, local encoder, entity graph, consent API, glance UI.",
                "risks": ["Privacy backlash", "hardware dependency"],
                "unknowns": ["Social acceptability of capture"],
                "why_may_win": "Every agent is starved for durable personal context.",
                "why_may_fail": "Phone OS vendors absorb the category.",
                "market": "Personal computing infrastructure",
                "first_customer": "Consultants and researchers already recording their days",
                "product": "A queryable memory layer, not a notebook.",
            }
        ]
        return _from_catalog(items, self.id)


class ProductEvolutionMode:
    id = "product-evolution"
    name = "Product Evolution Lab"
    question = "What radical evolution should an existing product undergo now?"

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]:
        items = [
            {
                "name": "AI Legacy App Operator",
                "one_liner": "An operator that uses existing enterprise GUIs instead of waiting for APIs.",
                "problem": "Most valuable software still has no complete API; work remains trapped in screens.",
                "customer": "Ops teams living in SAP, Epic, or custom internal tools.",
                "future_thesis": "The next integration layer is an operator, not another iPaaS connector.",
                "technology_convergence": ["Computer Use", "Authorization", "Persistent Memory"],
                "why_now": "Computer-use models became good enough to drive real GUIs with supervision.",
                "why_difficult_before": "RPA was brittle; models could not see and reason about screens.",
                "what_recently_changed": "Multimodal computer-use agents and cheaper runtime.",
                "current_alternatives": ["UiPath", "human shared-services teams", "custom APIs that never ship"],
                "novelty": "Combines computer use with attested identity and durable process memory.",
                "potential_moat": "Process graphs learned from real operator traces.",
                "mvp": "A supervised operator for one high-value legacy workflow with replayable traces.",
                "architecture": "Screen agent, policy sandbox, trace store, human takeover, connector-less I/O.",
                "risks": ["Incumbent RPA vendors add a model"],
                "unknowns": ["Reliability at production SLAs"],
                "why_may_win": "API coverage of legacy systems will stay incomplete for a decade.",
                "why_may_fail": "Error rates make it a demo forever.",
                "market": "Enterprise operations",
                "first_customer": "A shared-services team running a repetitive GUI workflow daily",
                "product": "A supervised AI operator for software that will never get a clean API.",
            }
        ]
        return _from_catalog(items, self.id)


class InternetTelescopeMode:
    id = "internet-telescope"
    name = "Internet Telescope"
    question = "What is forming before it receives a popular name?"

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]:
        if ctx.signals:
            top = ctx.signals[:5]
            items = []
            for sig in top:
                items.append(
                    {
                        "name": f"Unnamed: {sig.get('title', 'signal')[:48]}",
                        "one_liner": "A product hypothesis derived from an unnamed cluster, not a keyword.",
                        "problem": sig.get("summary") or "A weak signal without a category name yet.",
                        "customer": "Builders already poking at this cluster.",
                        "future_thesis": "This activity is a category in formation.",
                        "technology_convergence": sig.get("technologies") or ["Emerging"],
                        "why_now": "The cluster appeared across sources before it has a Gartner name.",
                        "why_difficult_before": "The underlying capability was missing or too expensive.",
                        "what_recently_changed": sig.get("title") or "",
                        "current_alternatives": ["Ad-hoc scripts"],
                        "novelty": "Detected from a chain of activity rather than a prompt about a known market.",
                        "potential_moat": "Being early enough to name and own the primitive.",
                        "mvp": "A thin tool that serves the people already in the cluster.",
                        "architecture": "Research watcher + smallest useful product for the cluster.",
                        "risks": ["The cluster is noise"],
                        "unknowns": ["Whether the unnamed thing is a product or a feature"],
                        "why_may_win": "Naming a primitive early is a strategic advantage.",
                        "why_may_fail": "The activity never coheres.",
                        "market": "Emerging",
                        "first_customer": "Researchers and hackers in the cluster",
                        "product": sig.get("title") or "Unnamed cluster tool",
                    }
                )
            return _from_catalog(items, self.id)
        return InventionLabMode().generate(ctx)


class StartupFactoryMode:
    id = "startup-factory"
    name = "One-Night Startup Factory"
    question = "Can this opportunity become a company-shaped artifact overnight?"

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]:
        return MissingPrimitiveMode().generate(ctx)


class AutoDiscoverMode:
    id = "auto"
    name = "Auto Discover"
    question = "What investigation is most interesting tonight?"

    def generate(self, ctx: ModeContext) -> list[IdeaDraft]:
        return MissingPrimitiveMode().generate(ctx)
