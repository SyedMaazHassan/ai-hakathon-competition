function candidateListApp() {
  return {
    // Data
    searchTerm: '',
    selectedFilter: 'all',
    experienceFilter: 'all',
    sortField: 'created_at',
    sortDirection: 'desc',
    currentPage: 1,
    itemsPerPage: 10,
    
    // Candidates data from Django
    candidates: [],

    // Computed properties
    get filteredCandidates() {
      return this.candidates.filter(candidate => {
        const matchesSearch = candidate.full_name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                             (candidate.email && candidate.email.toLowerCase().includes(this.searchTerm.toLowerCase())) ||
                             (candidate.professional_title && candidate.professional_title.toLowerCase().includes(this.searchTerm.toLowerCase())) ||
                             (candidate.city && candidate.city.toLowerCase().includes(this.searchTerm.toLowerCase()));
       
        const matchesLocation = this.selectedFilter === "all" || 
                               (this.selectedFilter === "local" && candidate.country === "Pakistan") ||
                               (this.selectedFilter === "international" && candidate.country !== "Pakistan");
      
        const matchesExperience = this.experienceFilter === "all" || 
                                 (this.experienceFilter === "entry" && (candidate.total_years_experience || 0) < 2) ||
                                 (this.experienceFilter === "mid" && (candidate.total_years_experience || 0) >= 2 && (candidate.total_years_experience || 0) < 5) ||
                                 (this.experienceFilter === "senior" && (candidate.total_years_experience || 0) >= 5);
       
        return matchesSearch && matchesLocation && matchesExperience;
      }).sort((a, b) => {
        let aValue = a[this.sortField];
        let bValue = b[this.sortField];
       
        if (!aValue && !bValue) return 0;
        if (!aValue) return this.sortDirection === 'asc' ? 1 : -1;
        if (!bValue) return this.sortDirection === 'asc' ? -1 : 1;
       
        if (this.sortField === 'created_at') {
          aValue = new Date(aValue).getTime();
          bValue = new Date(bValue).getTime();
        } else if (this.sortField === 'total_years_experience') {
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
      return Math.ceil(this.filteredCandidates.length / this.itemsPerPage);
    },

    get startIndex() {
      return (this.currentPage - 1) * this.itemsPerPage;
    },

    get paginatedCandidates() {
      return this.filteredCandidates.slice(this.startIndex, this.startIndex + this.itemsPerPage);
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

    getInitials(name) {
      if (!name) return "??";
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    },


    getLocationText(candidate) {
      if (candidate.city && candidate.country) {
        return candidate.city + ', ' + candidate.country;
      }
      return candidate.city || candidate.country || "Not specified";
    },

    formatDate(dateString) {
      if (!dateString) return 'Not specified';
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      }).format(new Date(dateString));
    },

    viewCandidate(candidateId) {
      window.location.href = '/hiring/resumes/' + candidateId + '/';
    },

    jobFitAnalysis(candidateId) {
      // Implement job fit analysis functionality
      console.log('Job fit analysis for candidate:', candidateId);
    },

    editCandidate(candidateId) {
      // Implement edit functionality
      console.log('Edit candidate:', candidateId);
    },

    deleteCandidate(candidateId) {
      // Implement delete functionality
      if (confirm('Are you sure you want to delete this candidate?')) {
        console.log('Delete candidate:', candidateId);
      }
    },

    // Initialize candidates data
    init() {
      // Candidates data will be set from the template
      this.candidates = window.candidatesData || [];
    }
  }
}
