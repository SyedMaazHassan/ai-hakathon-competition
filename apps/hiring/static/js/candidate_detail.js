function candidateDetailApp() {
  return {
    // Data
    candidateData: {},

    // Methods
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

    formatDate(dateObj) {
      if (!dateObj) return 'Not specified';
      
      // Handle different date formats
      if (typeof dateObj === 'string') {
        return new Intl.DateTimeFormat('en-US', {
          month: 'short',
          year: 'numeric'
        }).format(new Date(dateObj));
      }
      
      if (dateObj.year) {
        let dateStr = '';
        if (dateObj.month) {
          const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
          dateStr = monthNames[dateObj.month - 1] + ' ';
        }
        dateStr += dateObj.year;
        return dateStr;
      }
      
      return dateObj.original || 'Not specified';
    },

    formatDateRange(startDate, endDate, isCurrent) {
      let start = this.formatDate(startDate);
      let end = isCurrent ? 'Present' : this.formatDate(endDate);
      
      if (start === 'Not specified' && end === 'Not specified') {
        return 'Not specified';
      }
      
      return start + ' - ' + end;
    },

    // Initialize candidate data
    init() {
      this.candidateData = window.candidateDetailData || {};
    }
  }
}
