import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
}

interface Student {
  id: number;
  student_id: string;
  first_name: string;
  last_name: string;
  email: string;
  enrollment_date: string;
}

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tasksResponse, studentsResponse] = await Promise.all([
          axios.get<Task[]>('http://localhost:8000/api/tasks/'),
          axios.get<Student[]>('http://localhost:8000/api/students/')
        ]);
        setTasks(tasksResponse.data);
        setStudents(studentsResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">
          TCU CEAA Dashboard
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Tasks Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">Tasks</h2>
            {tasks.length === 0 ? (
              <p className="text-gray-600">No tasks found.</p>
            ) : (
              <div className="space-y-4">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className={`p-4 rounded-lg border ${
                      task.completed
                        ? 'bg-green-50 border-green-200'
                        : 'bg-yellow-50 border-yellow-200'
                    }`}
                  >
                    <h3 className="font-semibold text-gray-800">{task.title}</h3>
                    <p className="text-gray-600 mt-1">{task.description}</p>
                    <div className="flex justify-between items-center mt-2">
                      <span
                        className={`px-2 py-1 rounded text-sm ${
                          task.completed
                            ? 'bg-green-200 text-green-800'
                            : 'bg-yellow-200 text-yellow-800'
                        }`}
                      >
                        {task.completed ? 'Completed' : 'Pending'}
                      </span>
                      <span className="text-sm text-gray-500">
                        {new Date(task.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Students Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">Students</h2>
            {students.length === 0 ? (
              <p className="text-gray-600">No students found.</p>
            ) : (
              <div className="space-y-4">
                {students.map((student) => (
                  <div
                    key={student.id}
                    className="p-4 rounded-lg border border-blue-200 bg-blue-50"
                  >
                    <h3 className="font-semibold text-gray-800">
                      {student.first_name} {student.last_name}
                    </h3>
                    <p className="text-gray-600">ID: {student.student_id}</p>
                    <p className="text-gray-600">Email: {student.email}</p>
                    <span className="text-sm text-gray-500">
                      Enrolled: {new Date(student.enrollment_date).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
