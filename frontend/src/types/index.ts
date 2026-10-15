// Define shared TypeScript shapes for API data and frontend components.
export interface Skill {
  id?: number;
  skill_name: string;
  category: string;
  confidence?: number;
  source_section?: string;
  is_confirmed?: boolean;
  weight?: number;
}

export interface AnalysisSkill {
  id?: number;
  skill_name: string;
  status: 'matched' | 'missing_mandatory' | 'missing_preferred' | 'additional';
  category: string;
  weight: number;
}

export interface JobRole {
  id: number;
  title: string;
  category: string;
  description: string;
  mandatory_skills: string[];
  preferred_skills: string[];
  total_skills_required: number;
}

export interface ResumeData {
  id: number;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size_bytes: number;
  candidate_name: string;
  email: string | null;
  phone: string | null;
  education_summary: string | null;
  experience_years: number;
  sections: Record<string, string>;
  skills_count: number;
  created_at: string;
}

export interface AlternativeRole {
  role: string;
  confidence: number;
}

export interface Suggestion {
  category: string;
  type: 'improvement' | 'warning' | 'strength';
  message: string;
  details: string;
}

export interface RoadmapItem {
  id: number;
  skill_name: string;
  priority: 'high' | 'medium' | 'low';
  stage: 'beginner' | 'intermediate' | 'advanced';
  reason: string;
  suggested_project: string;
  resources: Array<{
    title: string;
    url: string;
    type: string;
    provider: string;
  }>;
  status: 'not_started' | 'in_progress' | 'completed';
  estimated_hours: number;
}

export interface Roadmap {
  id: number;
  analysis_id: number;
  title: string;
  total_items: number;
  completed_items: number;
  progress_percentage: number;
  items: RoadmapItem[];
}

export interface AnalysisResult {
  id: number;
  resume_id: number;
  resume_filename: string;
  candidate_name: string;
  target_role_id: number | null;
  target_role_title: string;
  has_custom_jd: boolean;
  predicted_role: string;
  predicted_role_confidence: number;
  alternative_roles: AlternativeRole[];
  text_similarity_score: number;
  overall_skill_coverage: number;
  mandatory_skill_coverage: number;
  matched_skills: AnalysisSkill[];
  missing_mandatory_skills: AnalysisSkill[];
  missing_preferred_skills: AnalysisSkill[];
  additional_skills: AnalysisSkill[];
  suggestions: Suggestion[];
  roadmap_id: number | null;
  created_at: string;
}

export interface DashboardMetrics {
  total_analyses: number;
  avg_compatibility_score: number;
  most_missing_skills: Array<{ name: string; count: number }>;
  most_matched_skills: Array<{ name: string; count: number }>;
  top_recommended_roles: Array<{ role: string; count: number }>;
  recent_analyses: AnalysisResult[];
  skill_gap_distribution: Array<{ range: string; count: number }>;
}

export interface RoleComparisonItem {
  role: JobRole;
  mandatory_coverage: number;
  overall_coverage: number;
  matched_count: number;
  missing_mandatory_count: number;
  missing_preferred_count: number;
}

export interface ModelMetrics {
  model_name: string;
  accuracy: number;
  macro_f1: number;
  weighted_f1: number;
  precision_macro: number;
  recall_macro: number;
  training_samples: number;
  test_samples: number;
  classes: string[];
}
