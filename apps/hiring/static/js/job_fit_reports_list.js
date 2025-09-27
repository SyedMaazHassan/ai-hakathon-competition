function jobFitReportsApp() {
  return {
    // Data
    searchTerm: '',
    statusFilter: 'all',
    sortField: 'created_at',
    sortDirection: 'desc',
    currentPage: 1,
    itemsPerPage: 10,
    
    // Reports data from Django
    reports: [],

    // Computed properties
    get filteredReports() {
      return this.reports.filter(report => {
        const matchesSearch = report.candidate_name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                             (report.job_title && report.job_title.toLowerCase().includes(this.searchTerm.toLowerCase()));
       
        const matchesStatus = this.statusFilter === "all" || report.status === this.statusFilter;
       
        return matchesSearch && matchesStatus;
      }).sort((a, b) => {
        let aValue = a[this.sortField];
        let bValue = b[this.sortField];
       
        if (!aValue && !bValue) return 0;
        if (!aValue) return this.sortDirection === 'asc' ? 1 : -1;
        if (!bValue) return this.sortDirection === 'asc' ? -1 : 1;
       
        if (this.sortField === 'created_at') {
          aValue = new Date(aValue).getTime();
          bValue = new Date(bValue).getTime();
        } else if (this.sortField === 'fit_score') {
          aValue = Number(aValue) || 0;
          bValue = Number(bValue) || 0;
        } else {
          aValue = String(aValue).toLowerCase();
          bValue = String(bValue).toLowerCase();
        }
       
        if (aValue < bValue) return this.sortDirection === 'asc' ? -1 : 1;
        if (aValue > bValue) return this.sortDirection === 'asc' ? 1 : -1;
        return 0;
      });
    },

    get totalPages() {
      return Math.ceil(this.filteredReports.length / this.itemsPerPage);
    },

    get startIndex() {
      return (this.currentPage - 1) * this.itemsPerPage;
    },

    get paginatedReports() {
      return this.filteredReports.slice(this.startIndex, this.startIndex + this.itemsPerPage);
    },

    // Methods
    handleSort(field) {
      if (this.sortField === field) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortField = field;
        this.sortDirection = 'asc';
      }
      this.currentPage = 1;
    },

    handlePageChange(page) {
      this.currentPage = page;
    },

    getPageNumbers() {
      const total = this.totalPages;
      const current = this.currentPage;
      const pages = [];
      
      if (total <= 5) {
        for (let i = 1; i <= total; i++) {
          pages.push(i);
        }
      } else if (current <= 3) {
        for (let i = 1; i <= 5; i++) {
          pages.push(i);
        }
      } else if (current >= total - 2) {
        for (let i = total - 4; i <= total; i++) {
          pages.push(i);
        }
      } else {
        for (let i = current - 2; i <= current + 2; i++) {
          pages.push(i);
        }
      }
      
      return pages;
    },

    formatDate(dateString) {
      if (!dateString) return 'Not specified';
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      }).format(new Date(dateString));
    },

    viewReport(reportId) {
      window.location.href = '/hiring/reports/' + reportId + '/';
    },

    viewCandidate(candidateId) {
      window.location.href = '/hiring/resumes/' + candidateId + '/';
    },

    viewJob(jobId) {
      window.location.href = '/hiring/jobs/' + jobId + '/';
    },

    retryAnalysis(reportId) {
      // Implement retry functionality
      if (confirm('Are you sure you want to retry the analysis for this report?')) {
        console.log('Retry analysis for report:', reportId);
        // Add your retry logic here
      }
    },

    deleteReport(reportId) {
      // Implement delete functionality
      if (confirm('Are you sure you want to delete this report?')) {
        console.log('Delete report:', reportId);
        // Add your delete logic here
      }
    },

    // Initialize reports data
    init() {
      // Reports data will be set from the template
      this.reports = window.reportsData || [];
    }
  }
}
