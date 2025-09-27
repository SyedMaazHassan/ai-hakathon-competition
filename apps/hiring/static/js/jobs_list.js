function jobListApp() {
  return {
    // Data
    searchTerm: '',
    selectedFilter: 'all',
    seniorityFilter: 'all',
    sortField: 'created_at',
    sortDirection: 'desc',
    currentPage: 1,
    itemsPerPage: 10,
    
    // Jobs data from Django
    jobs: [],

    // Computed properties
    get filteredJobs() {
      return this.jobs.filter(job => {
        const matchesSearch = job.title.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                             (job.company_name && job.company_name.toLowerCase().includes(this.searchTerm.toLowerCase())) ||
                             (job.location_city && job.location_city.toLowerCase().includes(this.searchTerm.toLowerCase()));
       
        const matchesEmploymentType = this.selectedFilter === "all" || job.employment_type === this.selectedFilter;
        const matchesSeniority = this.seniorityFilter === "all" || job.seniority === this.seniorityFilter;
       
        return matchesSearch && matchesEmploymentType && matchesSeniority;
      }).sort((a, b) => {
        let aValue = a[this.sortField];
        let bValue = b[this.sortField];
       
        if (!aValue && !bValue) return 0;
        if (!aValue) return this.sortDirection === 'asc' ? 1 : -1;
        if (!bValue) return this.sortDirection === 'asc' ? -1 : 1;
       
        if (this.sortField === 'created_at') {
          aValue = new Date(aValue).getTime();
          bValue = new Date(bValue).getTime();
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
      return Math.ceil(this.filteredJobs.length / this.itemsPerPage);
    },

    get startIndex() {
      return (this.currentPage - 1) * this.itemsPerPage;
    },

    get paginatedJobs() {
      return this.filteredJobs.slice(this.startIndex, this.startIndex + this.itemsPerPage);
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

    getEmploymentTypeColor(type) {
      switch (type) {
        case "full_time": return "bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800";
        case "part_time": return "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800";
        case "contract": return "bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-800";
        case "freelance": return "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950 dark:text-purple-300 dark:border-purple-800";
        default: return "bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600";
      }
    },

    getSeniorityColor(seniority) {
      switch (seniority) {
        case "entry": return "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800";
        case "mid": return "bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-800";
        case "senior": return "bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800";
        case "lead": return "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950 dark:text-purple-300 dark:border-purple-800";
        default: return "bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600";
      }
    },

    getLocationText(job) {
      if (job.location_city && job.location_country) {
        return job.location_city + ', ' + job.location_country;
      }
      return job.location_city || job.location_country || "Remote";
    },

    formatDate(dateString) {
      if (!dateString) return 'Not specified';
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      }).format(new Date(dateString));
    },

    viewJob(jobId) {
      window.location.href = '/hiring/jobs/' + jobId + '/';
    },

    editJob(jobId) {
      // Implement edit functionality
      console.log('Edit job:', jobId);
    },

    deleteJob(jobId) {
      // Implement delete functionality
      if (confirm('Are you sure you want to delete this job?')) {
        console.log('Delete job:', jobId);
      }
    },

    // Initialize jobs data
    init() {
      // Jobs data will be set from the template
      this.jobs = window.jobsData || [];
    }
  }
}
