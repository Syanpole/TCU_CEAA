"""
AI Performance Monitor and Optimizer
Tracks processing times and suggests optimizations
"""
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

class AIPerformanceMonitor:
    """
    Monitor and optimize AI processing performance
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_log_file = 'ai_performance.json'
        self.performance_data = self._load_performance_data()
        
        # Performance targets
        self.targets = {
            'excellent': 0.2,    # Under 200ms
            'good': 0.5,         # Under 500ms  
            'acceptable': 1.0,   # Under 1 second
            'slow': 2.0,         # Under 2 seconds
            'timeout': 3.0       # Over 3 seconds
        }
    
    def _load_performance_data(self) -> Dict:
        """Load existing performance data"""
        try:
            if os.path.exists(self.performance_log_file):
                with open(self.performance_log_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load performance data: {e}")
        
        return {
            'processing_times': [],
            'daily_stats': {},
            'optimization_suggestions': [],
            'last_updated': None
        }
    
    def _save_performance_data(self):
        """Save performance data to file"""
        try:
            with open(self.performance_log_file, 'w') as f:
                json.dump(self.performance_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save performance data: {e}")
    
    def record_processing_time(self, processing_time: float, document_type: str = 'unknown', 
                             file_size: int = 0, success: bool = True) -> Dict[str, Any]:
        """Record a processing time and analyze performance"""
        
        timestamp = datetime.now().isoformat()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Record the processing time
        record = {
            'timestamp': timestamp,
            'processing_time': processing_time,
            'document_type': document_type,
            'file_size': file_size,
            'success': success,
            'performance_rating': self._get_performance_rating(processing_time)
        }
        
        self.performance_data['processing_times'].append(record)
        
        # Update daily stats
        if today not in self.performance_data['daily_stats']:
            self.performance_data['daily_stats'][today] = {
                'total_processed': 0,
                'average_time': 0.0,
                'fastest_time': float('inf'),
                'slowest_time': 0.0,
                'success_rate': 0.0,
                'performance_distribution': {
                    'excellent': 0,
                    'good': 0,
                    'acceptable': 0,
                    'slow': 0,
                    'timeout': 0
                }
            }
        
        daily_stats = self.performance_data['daily_stats'][today]
        daily_stats['total_processed'] += 1
        daily_stats['fastest_time'] = min(daily_stats['fastest_time'], processing_time)
        daily_stats['slowest_time'] = max(daily_stats['slowest_time'], processing_time)
        daily_stats['performance_distribution'][record['performance_rating']] += 1
        
        # Recalculate averages
        today_times = [
            r['processing_time'] for r in self.performance_data['processing_times']
            if r['timestamp'].startswith(today) and r['success']
        ]
        if today_times:
            daily_stats['average_time'] = sum(today_times) / len(today_times)
            daily_stats['success_rate'] = len([r for r in self.performance_data['processing_times'] 
                                             if r['timestamp'].startswith(today) and r['success']]) / daily_stats['total_processed']
        
        # Keep only last 1000 records to avoid file bloat
        if len(self.performance_data['processing_times']) > 1000:
            self.performance_data['processing_times'] = self.performance_data['processing_times'][-1000:]
        
        # Generate optimization suggestions
        self._update_optimization_suggestions()
        
        # Save data
        self.performance_data['last_updated'] = timestamp
        self._save_performance_data()
        
        return {
            'recorded': True,
            'performance_rating': record['performance_rating'],
            'daily_average': daily_stats['average_time'],
            'suggestions': self._get_current_suggestions()
        }
    
    def _get_performance_rating(self, processing_time: float) -> str:
        """Get performance rating for a processing time"""
        if processing_time <= self.targets['excellent']:
            return 'excellent'
        elif processing_time <= self.targets['good']:
            return 'good'
        elif processing_time <= self.targets['acceptable']:
            return 'acceptable'
        elif processing_time <= self.targets['slow']:
            return 'slow'
        else:
            return 'timeout'
    
    def _update_optimization_suggestions(self):
        """Update optimization suggestions based on recent performance"""
        suggestions = []
        
        # Analyze recent performance (last 50 records)
        recent_times = self.performance_data['processing_times'][-50:]
        if not recent_times:
            return
        
        avg_recent = sum(r['processing_time'] for r in recent_times) / len(recent_times)
        slow_count = len([r for r in recent_times if r['performance_rating'] in ['slow', 'timeout']])
        
        # Performance-based suggestions
        if avg_recent > self.targets['good']:
            suggestions.append({
                'type': 'performance',
                'priority': 'high',
                'suggestion': 'Average processing time is slow. Consider implementing caching or reducing image processing complexity.',
                'metric': f'Average: {avg_recent:.2f}s (target: <{self.targets["good"]}s)'
            })
        
        if slow_count > len(recent_times) * 0.2:  # More than 20% slow
            suggestions.append({
                'type': 'reliability',
                'priority': 'medium',
                'suggestion': 'High number of slow processing times detected. Consider adding timeout handling and fallback processing.',
                'metric': f'{slow_count}/{len(recent_times)} slow processes'
            })
        
        # File size analysis
        large_files = [r for r in recent_times if r.get('file_size', 0) > 5 * 1024 * 1024]  # > 5MB
        if large_files:
            suggestions.append({
                'type': 'optimization',
                'priority': 'medium',
                'suggestion': 'Large files detected. Consider implementing automatic image resizing before processing.',
                'metric': f'{len(large_files)} large files processed'
            })
        
        # Success rate analysis
        failed_recent = [r for r in recent_times if not r['success']]
        if len(failed_recent) > len(recent_times) * 0.1:  # More than 10% failures
            suggestions.append({
                'type': 'reliability',
                'priority': 'high',
                'suggestion': 'High failure rate detected. Review error handling and add better fallback mechanisms.',
                'metric': f'{len(failed_recent)}/{len(recent_times)} failed'
            })
        
        self.performance_data['optimization_suggestions'] = suggestions
    
    def _get_current_suggestions(self) -> List[str]:
        """Get current optimization suggestions as simple strings"""
        return [s['suggestion'] for s in self.performance_data.get('optimization_suggestions', [])]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        today = datetime.now().strftime('%Y-%m-%d')
        recent_times = self.performance_data['processing_times'][-100:]  # Last 100 records
        
        if not recent_times:
            return {'error': 'No performance data available'}
        
        # Calculate statistics
        avg_time = sum(r['processing_time'] for r in recent_times) / len(recent_times)
        success_rate = len([r for r in recent_times if r['success']]) / len(recent_times)
        
        # Performance distribution
        distribution = {'excellent': 0, 'good': 0, 'acceptable': 0, 'slow': 0, 'timeout': 0}
        for record in recent_times:
            distribution[record['performance_rating']] += 1
        
        # Daily stats
        daily_stats = self.performance_data['daily_stats'].get(today, {})
        
        report = {
            'overall_performance': {
                'average_processing_time': avg_time,
                'success_rate': success_rate,
                'total_recent_processed': len(recent_times),
                'performance_rating': self._get_performance_rating(avg_time)
            },
            'performance_distribution': distribution,
            'today_stats': daily_stats,
            'optimization_suggestions': self.performance_data.get('optimization_suggestions', []),
            'student_experience': {
                'feels_instant': (distribution['excellent'] + distribution['good']) / len(recent_times),
                'acceptable_speed': (distribution['excellent'] + distribution['good'] + distribution['acceptable']) / len(recent_times),
                'needs_improvement': (distribution['slow'] + distribution['timeout']) / len(recent_times)
            },
            'recommendations': self._generate_recommendations(avg_time, distribution, success_rate)
        }
        
        return report
    
    def _generate_recommendations(self, avg_time: float, distribution: Dict, success_rate: float) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if avg_time < self.targets['excellent']:
            recommendations.append("🎉 Excellent performance! Students will love the instant feedback.")
        elif avg_time < self.targets['good']:
            recommendations.append("✅ Good performance. Consider caching to reach excellent speeds.")
        elif avg_time < self.targets['acceptable']:
            recommendations.append("⚠️ Acceptable but could be faster. Optimize image processing.")
        else:
            recommendations.append("🚨 Performance needs improvement. Students may get impatient.")
        
        if success_rate < 0.9:
            recommendations.append("📊 Consider improving error handling to increase success rate.")
        
        if distribution['timeout'] > distribution['excellent']:
            recommendations.append("⏱️ Too many timeouts. Implement better timeout handling.")
        
        if distribution['excellent'] + distribution['good'] > len(distribution) * 0.8:
            recommendations.append("🌟 Great job! Most processing is fast enough for students.")
        
        return recommendations

# Global monitor instance
performance_monitor = AIPerformanceMonitor()

def track_processing_time(func):
    """Decorator to automatically track processing times"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        error = None
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            processing_time = time.time() - start_time
            
            # Try to extract document info from args
            document_type = 'unknown'
            file_size = 0
            
            # Record the performance
            performance_monitor.record_processing_time(
                processing_time=processing_time,
                document_type=document_type,
                file_size=file_size,
                success=success
            )
    
    return wrapper
