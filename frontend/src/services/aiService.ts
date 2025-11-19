/**
 * 🤖 AI Service Integration
 * Comprehensive AI System Frontend Integration
 * Connects to Django backend AI algorithms and provides real-time processing
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || window.location.protocol + '//' + window.location.hostname + ':8000/api';

// Types for AI system
export interface AIAnalysisResult {
  document_id: number;
  processing_timestamp: string;
  algorithms_results: {
    document_validator?: AIAlgorithmResult;
    cross_document_matcher?: AIAlgorithmResult;
    grade_verifier?: AIAlgorithmResult;
    face_verifier?: AIAlgorithmResult;
    fraud_detector?: AIAlgorithmResult;
  };
  overall_analysis: {
    name: string;
    overall_confidence: number;
    total_algorithms_run: number;
    successful_algorithms: number;
    recommendation: 'approved' | 'manual_review' | 'rejected';
  };
}

export interface AIAlgorithmResult {
  name: string;
  confidence: number;
  error?: string;
  [key: string]: any;
}

export interface AIStatus {
  document_id: number;
  status: string;
  ai_completed: boolean;
  confidence_score: number;
  auto_approved: boolean;
  analysis_notes: string;
  key_information: any;
  recommendations: string[];
  extracted_text: string;
  last_updated: string | null;
}

export interface AIDashboardStats {
  success: boolean;
  ai_statistics: {
    total_processed: number;
    auto_approval_rate: number;
    average_confidence: number;
    confidence_distribution: {
      high_confidence: number;
      medium_confidence: number;
      low_confidence: number;
    };
    processing_efficiency: number;
  };
  recent_activities: Array<{
    timestamp: string;
    action: string;
    description: string;
    user: string;
    details: any;
  }>;
  system_status: {
    ai_enabled: boolean;
    algorithms_available: number;
    processing_queue: number;
  };
}

export interface AIAnalysisResponse {
  success: boolean;
  results: AIAnalysisResult;
  document_status: string;
  auto_approved: boolean;
  message?: string;
  error?: string;
}

export interface AIBatchResponse {
  success: boolean;
  results: Array<{
    document_id: number;
    status: string;
    confidence?: number;
    error?: string;
  }>;
  message: string;
}

class AIService {
  private axios: any;

  constructor() {
    this.axios = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add token to requests
    this.axios.interceptors.request.use((config: any) => {
      const token = localStorage.getItem('token');
      if (token && config.headers) {
        config.headers.Authorization = `Token ${token}`;
      }
      return config;
    });
  }

  /**
   * 🤖 Core AI Document Analysis
   * Runs all 6 AI algorithms on uploaded documents:
   * 1. Document Validator - OCR with Pytesseract + pattern matching
   * 2. Cross-Document Matcher - Fuzzy string matching with Levenshtein/Jaro-Winkler
   * 3. Grade Verifier - GWA calculation + suspicious pattern detection
   * 4. Face Verifier - OpenCV face detection with graceful fallbacks
   * 5. Fraud Detector - Metadata analysis + tampering detection
   * 6. AI Verification Manager - Orchestrates all algorithms with weighted scoring
   */
  async analyzeDocument(documentId: number): Promise<AIAnalysisResponse> {
    try {
      const response = await this.axios.post('/ai/analyze-document/', {
        document_id: documentId
      });
      return response.data as AIAnalysisResponse;
    } catch (error: any) {
      console.error('AI Document Analysis Error:', error);
      throw new Error(error.response?.data?.error || 'AI analysis failed');
    }
  }

  /**
   * 🔍 Get AI Analysis Status
   * Returns real-time status and results of AI processing
   */
  async getAnalysisStatus(documentId: number): Promise<AIStatus> {
    try {
      const response = await this.axios.get(`/ai/status/${documentId}/`);
      return response.data as AIStatus;
    } catch (error: any) {
      console.error('AI Status Check Error:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch AI status');
    }
  }

  /**
   * 📊 AI Dashboard Statistics
   * Returns comprehensive AI system performance metrics
   */
  async getDashboardStats(): Promise<AIDashboardStats> {
    try {
      const response = await this.axios.get('/ai/dashboard-stats/');
      return response.data as AIDashboardStats;
    } catch (error: any) {
      console.error('AI Dashboard Stats Error:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch AI statistics');
    }
  }

  /**
   * 🚀 Batch AI Processing
   * Process multiple documents through AI algorithms
   */
  async batchProcess(documentIds: number[]): Promise<AIBatchResponse> {
    try {
      const response = await this.axios.post('/ai/batch-process/', {
        document_ids: documentIds
      });
      return response.data as AIBatchResponse;
    } catch (error: any) {
      console.error('AI Batch Processing Error:', error);
      throw new Error(error.response?.data?.error || 'Batch processing failed');
    }
  }

  /**
   * 🎯 AI Confidence Level Interpretation
   * Provides human-readable confidence interpretations
   */
  interpretConfidence(confidence: number): {
    level: 'high' | 'medium' | 'low' | 'critical';
    label: string;
    color: string;
    description: string;
  } {
    if (confidence >= 0.85) {
      return {
        level: 'high',
        label: 'High Confidence',
        color: '#10b981', // green
        description: 'AI is highly confident in the analysis. Document likely authentic.'
      };
    } else if (confidence >= 0.65) {
      return {
        level: 'medium',
        label: 'Medium Confidence',
        color: '#f59e0b', // yellow
        description: 'AI has moderate confidence. Manual review recommended.'
      };
    } else if (confidence >= 0.35) {
      return {
        level: 'low',
        label: 'Low Confidence',
        color: '#ef4444', // red
        description: 'AI has low confidence. Careful manual review required.'
      };
    } else {
      return {
        level: 'critical',
        label: 'Critical Issues',
        color: '#dc2626', // dark red
        description: 'AI detected potential issues. Document may be problematic.'
      };
    }
  }

  /**
   * 🔄 Real-time AI Processing Monitor
   * Polls AI status until processing is complete
   */
  async monitorProcessing(documentId: number, onUpdate?: (status: AIStatus) => void): Promise<AIStatus> {
    const pollInterval = 2000; // 2 seconds
    const maxAttempts = 30; // 60 seconds max
    let attempts = 0;

    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          attempts++;
          const status = await this.getAnalysisStatus(documentId);
          
          if (onUpdate) {
            onUpdate(status);
          }

          // Check if processing is complete
          if (status.ai_completed || status.status !== 'ai_processing') {
            resolve(status);
            return;
          }

          // Check max attempts
          if (attempts >= maxAttempts) {
            reject(new Error('AI processing timeout'));
            return;
          }

          // Continue polling
          setTimeout(poll, pollInterval);
        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  }

  /**
   * 📈 AI Performance Analytics
   * Calculate AI system performance metrics
   */
  calculatePerformanceMetrics(stats: AIDashboardStats) {
    const { ai_statistics } = stats;
    const total = ai_statistics.confidence_distribution.high_confidence + 
                  ai_statistics.confidence_distribution.medium_confidence + 
                  ai_statistics.confidence_distribution.low_confidence;

    return {
      accuracy_rate: ai_statistics.auto_approval_rate,
      processing_rate: ai_statistics.processing_efficiency,
      high_confidence_ratio: total > 0 ? (ai_statistics.confidence_distribution.high_confidence / total * 100) : 0,
      average_confidence_percentage: ai_statistics.average_confidence * 100,
      system_efficiency: (ai_statistics.auto_approval_rate + ai_statistics.processing_efficiency) / 2
    };
  }

  /**
   * 🎨 Get Algorithm Status Icon
   * Returns appropriate icon and color for algorithm results
   */
  getAlgorithmStatusIcon(algorithmResult: AIAlgorithmResult): {icon: string; color: string; status: string} {
    if (algorithmResult.error) {
      return { icon: '❌', color: '#dc2626', status: 'error' };
    }
    
    const confidence = algorithmResult.confidence;
    if (confidence >= 0.8) {
      return { icon: '✅', color: '#10b981', status: 'excellent' };
    } else if (confidence >= 0.6) {
      return { icon: '✔️', color: '#f59e0b', status: 'good' };
    } else if (confidence >= 0.4) {
      return { icon: '⚠️', color: '#ef4444', status: 'warning' };
    } else {
      return { icon: '🚫', color: '#dc2626', status: 'critical' };
    }
  }

  /**
   * 📋 Generate AI Analysis Report
   * Creates a comprehensive report of AI analysis results
   */
  generateAnalysisReport(results: AIAnalysisResult): string {
    const report = [];
    report.push('🤖 AI DOCUMENT ANALYSIS REPORT');
    report.push('='.repeat(50));
    report.push(`📅 Analysis Date: ${new Date(results.processing_timestamp).toLocaleString()}`);
    report.push(`📄 Document ID: ${results.document_id}`);
    report.push(`🎯 Overall Confidence: ${(results.overall_analysis.overall_confidence * 100).toFixed(1)}%`);
    report.push(`✅ Recommendation: ${results.overall_analysis.recommendation.toUpperCase()}`);
    report.push('');
    
    report.push('🔍 ALGORITHM RESULTS:');
    report.push('-'.repeat(30));
    
    Object.entries(results.algorithms_results).forEach(([key, result]) => {
      if (result) {
        const icon = this.getAlgorithmStatusIcon(result).icon;
        const confidence = result.error ? 'ERROR' : `${(result.confidence * 100).toFixed(1)}%`;
        report.push(`${icon} ${result.name}: ${confidence}`);
        if (result.error) {
          report.push(`   Error: ${result.error}`);
        }
      }
    });
    
    report.push('');
    report.push('📊 SUMMARY:');
    report.push(`• Algorithms Run: ${results.overall_analysis.total_algorithms_run}`);
    report.push(`• Successful: ${results.overall_analysis.successful_algorithms}`);
    report.push(`• Success Rate: ${(results.overall_analysis.successful_algorithms / results.overall_analysis.total_algorithms_run * 100).toFixed(1)}%`);
    
    return report.join('\n');
  }
}

export const aiService = new AIService();
export default aiService;