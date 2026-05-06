export interface User {
  id: string
  email: string
  full_name: string
  role: 'candidate' | 'recruiter' | 'admin'
  avatar_url: string | null
  created_at: string
}

export interface CodingProfile {
  id: string
  platform: string
  platform_username: string
  created_at: string
}

export interface PlatformSnapshot {
  id: string
  problems_solved: number
  contest_rating: number | null
  topic_stats: Record<string, number>
  submission_calendar: Record<string, number>
  raw_data: Record<string, unknown>
  scraped_at: string
}

export interface InsightReport {
  id: string
  strengths: Array<{ topic: string; score: number; detail: string }>
  weaknesses: Array<{ topic: string; score: number; detail: string }>
  career_recs: string[]
  roadmap: Array<{ range: string; focus: string; actions: string[] }>
  overall_score: number
  summary_text: string
  created_at: string
}

export interface ChatSession {
  id: string
  title: string
  created_at: string
}

export interface ChatMessageType {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Company {
  id: string
  name: string
  slug: string
  owner_id: string
  created_at: string
}

export interface Job {
  id: string
  company_id: string
  title: string
  description: string
  required_skills: string[]
  min_overall_score: number | null
  is_active: boolean
  created_at: string
}

export interface Assessment {
  id: string
  company_id: string
  title: string
  description: string
  time_limit_mins: number
  created_at: string
}

export interface JobMatch {
  job_id: string | null
  source: string
  title: string
  company: string
  description: string
  required_skills: string[]
  location: string | null
  apply_url: string | null
  match_score: number
  reasoning: string
  skill_gaps: string[]
  highlights: string[]
}

export interface ExternalJob {
  source: string
  source_id: string
  title: string
  company: string
  description: string
  required_skills: string[]
  location: string | null
  apply_url: string | null
  posted_at: string | null
}

export interface NormalizedPerPlatform {
  platform: string
  username: string
  problems_solved: number
  raw_rating: number | null
  rating_percentile: number | null
  canonical_topics: Record<string, number>
  difficulty_breakdown: Record<string, number>
  weighted_volume: number
}

export interface NormalizedAggregate {
  platforms: string[]
  total_problems_raw: number
  total_weighted_volume: number
  canonical_topic_stats: Record<string, number>
  canonical_topic_share: Record<string, number>
  difficulty_breakdown: Record<string, number>
  rating_percentile_per_platform: Record<string, number | null>
  rating_percentile_overall: number | null
  top_topic: string | null
  weakest_known_topic: string | null
  coverage: number
  topic_labels: Record<string, string>
  per_platform: NormalizedPerPlatform[]
  all_canonical_topics: string[]
}
