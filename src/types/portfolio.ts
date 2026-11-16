export interface QuickStat {
  value: string;
  label: string;
  numeric_value?: number | null;
  unit?: string;
}

export interface HeroProfile {
  brand_initials: string;
  brand_name: string;
  full_name: string;
  initials_fallback: string;
  status_badge: string;
  summary: string;
  roles: string[];
  location: string;
  university_short: string;
  hackathon_badge: string;
  batch_period: string;
  github_url: string;
  linkedin_url: string;
  float_chip_title: string;
  float_chip_subtitle: string;
  quick_stats: QuickStat[];
}

export interface SemesterMetric {
  semester: number;
  label: string;
  status: string;
  sgpa: number | null;
  max_sgpa: number;
  progress_percent: number;
  credits: number;
  display_score: string;
}

export interface EducationProfile {
  institution: string;
  location: string;
  degree: string;
  period: string;
  current_year_label: string;
  focus: string;
  current_semester: number;
  total_semesters: number;
  degree_progress_percent: number;
  semesters: SemesterMetric[];
}

export interface AcademicAnalytics {
  completed_semesters: number;
  total_credits_completed: number;
  cumulative_cgpa: number;
  mean_sgpa: number;
  sgpa_stdev: number;
  highest_sgpa: number;
  lowest_sgpa: number;
  latest_delta: number;
  degree_progress_percent: number;
  standing: string;
}

export type SkillCategory = 'all' | 'languages' | 'web' | 'tools';

export interface SkillItem {
  id: string;
  name: string;
  category: Exclude<SkillCategory, 'all'>;
  category_label: string;
  level: 'Beginner' | 'Intermediate' | 'Advanced';
  proficiency: number;
  keywords: string[];
}

export interface SkillsPayload {
  filter: string;
  query: string;
  sort_by: string;
  total_count: number;
  matched_count: number;
  average_proficiency: number;
  items: SkillItem[];
}

export interface CoreKnowledgeTopic {
  id: string;
  title: string;
  short_label: string;
  description: string;
  applied_in: string[];
}

export interface ArchitectureLayer {
  id: string;
  tab_label: string;
  title: string;
  summary: string;
  highlights: string[];
  technologies: string[];
}

export interface ProjectShowcase {
  id: string;
  title: string;
  stage_label: string;
  description: string;
  tech_tags: string[];
  live_url: string;
  github_url: string;
  layers: ArchitectureLayer[];
}

export interface AchievementCard {
  id: string;
  icon: string;
  title: string;
  description: string;
  chips: string[];
  highlight_first_chip?: boolean;
}

export interface ContactChannel {
  id: string;
  label: string;
  display_value: string;
  action_type: 'copy' | 'link';
  action_value: string;
}

export interface PortfolioPayload {
  hero: HeroProfile;
  has_profile_photo: boolean;
  profile_photo_url: string | null;
  education: EducationProfile;
  academic_analytics: AcademicAnalytics;
  skills: SkillsPayload;
  core_knowledge: CoreKnowledgeTopic[];
  featured_project: ProjectShowcase;
  achievements: AchievementCard[];
  contact_channels: ContactChannel[];
}

export interface ContactSubmitResponse {
  ok: boolean;
  submission_id?: string;
  mailto_url?: string;
  confirmation?: string;
  message?: string;
  errors?: string[];
}
