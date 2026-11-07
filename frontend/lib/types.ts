export type Idea = {
  id: string;
  name: string;
  one_liner: string;
  score: number;
  score_band: string;
  status: string;
  why_now?: string;
  mode?: string;
  is_demo?: boolean;
  technology_convergence?: string[];
};

export type Signal = {
  id: string;
  title: string;
  summary?: string;
  source?: string;
  source_url?: string;
  category?: string;
  novelty_score?: number;
  momentum_score?: number;
  tags?: string[];
};

export type RunSummary = {
  id: string;
  status: string;
  mode?: string;
  winner_id?: string;
  winner_score?: number;
  created_at?: string;
  runtime_seconds?: number;
};

export type TimelineEvent = {
  id: string;
  stage: string;
  message: string;
  occurred_at?: string;
  status?: string;
  agent?: string;
};
