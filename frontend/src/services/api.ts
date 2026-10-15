// Provide typed HTTP methods for communicating with the Flask backend API.
import axios from 'axios';
import type {
  JobRole,
  Skill,
  ResumeData,
  AnalysisResult,
  Roadmap,
  RoadmapItem,
  DashboardMetrics,
  RoleComparisonItem,
  ModelMetrics,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const api = {
  // Health
  checkHealth: async () => {
    const res = await apiClient.get('/health');
    return res.data;
  },

  // Roles & Skills
  getRoles: async (): Promise<JobRole[]> => {
    const res = await apiClient.get('/roles');
    return res.data.roles;
  },

  getSkills: async (): Promise<Skill[]> => {
    const res = await apiClient.get('/skills');
    return res.data.skills;
  },

  // Resumes
  uploadResume: async (file: File): Promise<{ resume: ResumeData; extracted_skills: Skill[] }> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post('/resumes', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  getResume: async (resumeId: number): Promise<{ resume: ResumeData; skills: Skill[] }> => {
    const res = await apiClient.get(`/resumes/${resumeId}`);
    return res.data;
  },

  deleteResume: async (resumeId: number) => {
    const res = await apiClient.delete(`/resumes/${resumeId}`);
    return res.data;
  },

  updateExtractedSkills: async (resumeId: number, skills: Skill[]) => {
    const res = await apiClient.put(`/resumes/${resumeId}/skills`, { skills });
    return res.data;
  },

  // Analysis
  runAnalysis: async (payload: {
    resume_id: number;
    target_role_id?: number;
    custom_job_description?: string;
    confirmed_skills?: string[];
  }): Promise<AnalysisResult> => {
    const res = await apiClient.post('/analysis', payload);
    return res.data.analysis;
  },

  getAnalysis: async (analysisId: number): Promise<AnalysisResult> => {
    const res = await apiClient.get(`/analysis/${analysisId}`);
    return res.data.analysis;
  },

  getAnalysisHistory: async (page = 1, perPage = 10): Promise<{ analyses: AnalysisResult[]; total: number }> => {
    const res = await apiClient.get('/analysis', { params: { page, per_page: perPage } });
    return res.data;
  },

  deleteAnalysis: async (analysisId: number) => {
    const res = await apiClient.delete(`/analysis/${analysisId}`);
    return res.data;
  },

  // Role Comparison
  compareRoles: async (resumeId: number, roleIds: number[]): Promise<{ comparisons: RoleComparisonItem[] }> => {
    const res = await apiClient.post('/roles/compare', { resume_id: resumeId, role_ids: roleIds });
    return res.data;
  },

  // Roadmap
  getRoadmap: async (analysisId: number): Promise<Roadmap> => {
    const res = await apiClient.get(`/roadmaps/${analysisId}`);
    return res.data.roadmap;
  },

  updateRoadmapItemStatus: async (
    roadmapId: number,
    itemId: number,
    status: 'not_started' | 'in_progress' | 'completed'
  ): Promise<RoadmapItem> => {
    const res = await apiClient.patch(`/roadmaps/${roadmapId}/items/${itemId}`, { status });
    return res.data.item;
  },

  // Metrics & Reports
  getDashboardMetrics: async (): Promise<DashboardMetrics> => {
    const res = await apiClient.get('/metrics/dashboard');
    return res.data;
  },

  getModelMetrics: async (): Promise<ModelMetrics> => {
    const res = await apiClient.get('/models/metrics');
    return res.data.metrics;
  },

  getReportPdfUrl: (analysisId: number): string => {
    return `${API_BASE_URL}/reports/${analysisId}/pdf`;
  },

  getReportJson: async (analysisId: number) => {
    const res = await apiClient.get(`/reports/${analysisId}/json`);
    return res.data;
  },
};

export default api;
