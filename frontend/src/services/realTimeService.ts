class RealTimeService {
  private intervals: Map<string, NodeJS.Timeout> = new Map();
  private listeners: Map<string, Set<Function>> = new Map();

  // Subscribe to real-time updates for a specific data type
  subscribe(dataType: string, callback: Function, intervalMs: number = 5000) {
    // Add callback to listeners
    if (!this.listeners.has(dataType)) {
      this.listeners.set(dataType, new Set());
    }
    this.listeners.get(dataType)!.add(callback);

    // Start polling if not already started for this data type
    if (!this.intervals.has(dataType)) {
      const interval = setInterval(() => {
        this.fetchAndNotify(dataType);
      }, intervalMs);
      this.intervals.set(dataType, interval);
    }

    // Initial fetch
    this.fetchAndNotify(dataType);
  }

  // Unsubscribe from real-time updates
  unsubscribe(dataType: string, callback: Function) {
    const listeners = this.listeners.get(dataType);
    if (listeners) {
      listeners.delete(callback);
      
      // If no more listeners, stop polling
      if (listeners.size === 0) {
        const interval = this.intervals.get(dataType);
        if (interval) {
          clearInterval(interval);
          this.intervals.delete(dataType);
        }
        this.listeners.delete(dataType);
      }
    }
  }

  // Fetch data and notify all listeners
  private async fetchAndNotify(dataType: string) {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const API_BASE = window.location.protocol + '//' + window.location.hostname + ':8000/api';
      let url = '';
      switch (dataType) {
        case 'student-dashboard':
          url = `${API_BASE}/dashboard/student/`;
          break;
        case 'admin-dashboard':
          url = `${API_BASE}/dashboard/admin/`;
          break;
        case 'documents':
          url = `${API_BASE}/documents/`;
          break;
        case 'grades':
          url = `${API_BASE}/grades/`;
          break;
        case 'applications':
          url = `${API_BASE}/applications/`;
          break;
        default:
          return;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const listeners = this.listeners.get(dataType);
        if (listeners) {
          listeners.forEach(callback => callback(data));
        }
      }
    } catch (error) {
      console.error(`Error fetching ${dataType}:`, error);
    }
  }

  // Trigger immediate update for a data type
  triggerUpdate(dataType: string) {
    this.fetchAndNotify(dataType);
  }

  // Clean up all intervals
  cleanup() {
    this.intervals.forEach(interval => clearInterval(interval));
    this.intervals.clear();
    this.listeners.clear();
  }

  // Manual trigger for when we know data has changed
  notifyDataChange(dataType: string) {
    // Immediate update
    this.fetchAndNotify(dataType);
    
    // Also trigger related updates
    if (dataType === 'documents' || dataType === 'grades' || dataType === 'applications') {
      this.fetchAndNotify('student-dashboard');
      this.fetchAndNotify('admin-dashboard');
    }
  }
}

export const realTimeService = new RealTimeService();
