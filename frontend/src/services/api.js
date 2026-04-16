import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/accounts/auth/refresh/`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', response.data.access_token);
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: (username, password) => api.post('/accounts/auth/login/', { username, password }),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
  getCurrentUser: () => api.get('/accounts/users/me/'),
};

export const userService = {
  getUsers: (params) => api.get('/accounts/users/', { params }),
  createUser: (data) => api.post('/accounts/users/', data),
  updateUser: (id, data) => api.patch(`/accounts/users/${id}/`, data),
  deleteUser: (id) => api.delete(`/accounts/users/${id}/`),
  changePassword: (data) => api.post('/accounts/users/change_password/', data),
};

export const studentService = {
  getStudents: (params) => api.get('/students/', { params }),
  getStudent: (id) => api.get(`/students/${id}/`),
  createStudent: (data) => api.post('/students/', data),
  updateStudent: (id, data) => api.patch(`/students/${id}/`, data),
  deleteStudent: (id) => api.delete(`/students/${id}/`),
  getMyProfile: () => api.get('/students/my_profile/'),
  getFaculties: (params) => api.get('/faculties/', { params }),
  createFaculty: (data) => api.post('/faculties/', data),
  getDepartments: (params) => api.get('/departments/', { params }),
  createDepartment: (data) => api.post('/departments/', data),
  getProgrammes: (params) => api.get('/programmes/', { params }),
  createProgramme: (data) => api.post('/programmes/', data),
};

export const academicService = {
  getSessions: (params) => api.get('/academic/sessions/', { params }),
  createSession: (data) => api.post('/academic/sessions/', data),
  getCurrentSession: () => api.get('/academic/sessions/current/'),
  getSemesters: (params) => api.get('/academic/semesters/', { params }),
  createSemester: (data) => api.post('/academic/semesters/', data),
  getActiveSemester: () => api.get('/academic/semesters/active/'),
  getCourses: (params) => api.get('/academic/courses/', { params }),
  createCourse: (data) => api.post('/academic/courses/', data),
  getCourseAllocations: (params) => api.get('/academic/course-allocations/', { params }),
  createCourseAllocation: (data) => api.post('/academic/course-allocations/', data),
  getCourseRegistrations: (params) => api.get('/academic/course-registrations/', { params }),
  registerCourses: (data) => api.post('/academic/course-registrations/register_courses/', data),
  getMyCourses: (semesterId) => api.get('/academic/course-registrations/my_courses/', { params: { semester_id: semesterId } }),
  getResults: (params) => api.get('/academic/results/', { params }),
  createResult: (data) => api.post('/academic/results/', data),
  getMyResults: (semesterId) => api.get('/academic/results/my_results/', { params: { semester_id: semesterId } }),
  calculateGPA: (studentId, semesterId) => api.get('/academic/results/calculate_gpa/', { params: { student_id: studentId, semester_id: semesterId } }),
  getExamSittings: (params) => api.get('/academic/exam-sittings/', { params }),
  createExamSitting: (data) => api.post('/academic/exam-sittings/', data),
  generateSeating: (data) => api.post('/academic/exam-sittings/generate_seating/', data),
};

export const financeService = {
  getFeeTypes: () => api.get('/finance/fee-types/'),
  createFeeType: (data) => api.post('/finance/fee-types/', data),
  getFeeStructures: (params) => api.get('/finance/fee-structures/', { params }),
  createFeeStructure: (data) => api.post('/finance/fee-structures/', data),
  getInvoices: (params) => api.get('/finance/invoices/', { params }),
  createInvoice: (data) => api.post('/finance/invoices/', data),
  generateInvoices: (data) => api.post('/finance/invoices/generate_invoices/', data),
  getMyInvoices: () => api.get('/finance/invoices/my_invoices/'),
  getPayments: (params) => api.get('/finance/payments/', { params }),
  createPayment: (data) => api.post('/finance/payments/', data),
  initiatePayment: (data) => api.post('/finance/payments/initiate_payment/', data),
  getMyPayments: () => api.get('/finance/payments/my_payments/'),
  getScholarships: () => api.get('/finance/scholarships/'),
  createScholarship: (data) => api.post('/finance/scholarships/', data),
  getFinanceDashboard: () => api.get('/finance/student-scholarships/dashboard/'),
};

export const libraryService = {
  getBooks: (params) => api.get('/library/books/', { params }),
  createBook: (data) => api.post('/library/books/', data),
  getAuthors: () => api.get('/library/authors/'),
  getCategories: () => api.get('/library/categories/'),
  getLoans: (params) => api.get('/library/loans/', { params }),
  createLoan: (data) => api.post('/library/loans/', data),
};

export const hostelService = {
  getHostels: () => api.get('/hostel/'),
  createHostel: (data) => api.post('/hostel/', data),
  getRooms: (params) => api.get('/hostel/rooms/', { params }),
  createRoom: (data) => api.post('/hostel/rooms/', data),
  getAssignments: (params) => api.get('/hostel/assignments/', { params }),
  createAssignment: (data) => api.post('/hostel/assignments/', data),
};

export const hrService = {
  getEmployees: (params) => api.get('/hr/employees/', { params }),
  createEmployee: (data) => api.post('/hr/employees/', data),
  getDepartments: () => api.get('/hr/departments/'),
  getLeaveTypes: () => api.get('/hr/leave-types/'),
  getLeaveRequests: (params) => api.get('/hr/leave-requests/', { params }),
  getPayrolls: (params) => api.get('/hr/payrolls/', { params }),
};

export const nucService = {
  getAccreditations: (params) => api.get('/nuc/accreditations/', { params }),
  createAccreditation: (data) => api.post('/nuc/accreditations/', data),
  getReports: (params) => api.get('/nuc/reports/', { params }),
  getGraduations: (params) => api.get('/nuc/graduations/', { params }),
  createGraduation: (data) => api.post('/nuc/graduations/', data),
};

export const notificationService = {
  getNotifications: () => api.get('/notifications/'),
  getUnreadCount: () => api.get('/notifications/unread_count/'),
  markAsRead: (id) => api.post(`/notifications/${id}/mark_read/`),
  markAllAsRead: () => api.post('/notifications/mark_all_read/'),
  getAnnouncements: (params) => api.get('/notifications/announcements/', { params }),
  createAnnouncement: (data) => api.post('/notifications/announcements/', data),
};

export default api;
