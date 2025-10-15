class Dashboard {
    constructor() {
        this.tickets = [];
        this.filteredTickets = [];
        this.selectedTickets = new Set();
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.filters = {
            category: '',
            team: ''
        };
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.updateStats();
    }

    setupEventListeners() {
        // Main action buttons
        document.getElementById('fetch-tickets-btn').addEventListener('click', () => {
            this.fetchTickets();
        });

        document.getElementById('sync-to-clickup-btn').addEventListener('click', () => {
            this.syncToClickUp();
        });

        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.refreshTable();
        });

        // Select all functionality
        document.getElementById('select-all-checkbox').addEventListener('change', (e) => {
            this.selectAll(e.target.checked);
        });

        document.getElementById('select-all-btn').addEventListener('click', () => {
            const allSelected = this.selectedTickets.size === this.tickets.length;
            this.selectAll(!allSelected);
            document.getElementById('select-all-checkbox').checked = !allSelected;
        });

        // Sorting
        document.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', () => {
                this.sortTable(header.dataset.sort);
            });
        });

        // Edit category modal
        document.getElementById('cancel-edit-btn').addEventListener('click', () => {
            this.closeEditModal();
        });

        document.getElementById('save-edit-btn').addEventListener('click', () => {
            this.saveEditCategory();
        });

        // Close modal when clicking outside
        document.getElementById('edit-category-modal').addEventListener('click', (e) => {
            if (e.target.id === 'edit-category-modal') {
                this.closeEditModal();
            }
        });

        // Filter functionality
        document.getElementById('category-filter').addEventListener('change', (e) => {
            this.filters.category = e.target.value;
            this.applyFilters();
        });

        document.getElementById('team-filter').addEventListener('change', (e) => {
            this.filters.team = e.target.value;
            this.applyFilters();
        });

        document.getElementById('clear-filters-btn').addEventListener('click', () => {
            this.clearFilters();
        });

        // Team stat card clicks
        document.querySelectorAll('.team-stat-card').forEach(card => {
            card.addEventListener('click', () => {
                const team = card.dataset.team;
                this.filterByTeam(team);
            });
        });

        // Knowledge base upload
        document.getElementById('upload-kb-btn').addEventListener('click', () => {
            this.openUploadModal();
        });

        document.getElementById('cancel-upload-btn').addEventListener('click', () => {
            this.closeUploadModal();
        });

        document.getElementById('upload-kb-file-btn').addEventListener('click', () => {
            this.uploadKnowledgeBase();
        });

        // Close upload modal when clicking outside
        document.getElementById('upload-kb-modal').addEventListener('click', (e) => {
            if (e.target.id === 'upload-kb-modal') {
                this.closeUploadModal();
            }
        });
    }

    async fetchTickets() {
        const button = document.getElementById('fetch-tickets-btn');
        const overlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Fetching...';
        overlay.classList.remove('hidden');
        loadingText.textContent = 'Fetching tickets...';

        try {
            const previewMode = document.getElementById('preview-mode').checked;
            
            if (previewMode) {
                // Load from mock data
                const response = await fetch('/static/mock_tickets.json');
                const mockTickets = await response.json();
                this.processTickets(mockTickets);
            } else {
                // Load from Zoho API
                const response = await fetch('/api/tickets/fetch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ hours_back: 24 })
                });
                const result = await response.json();
                
                if (result.success) {
                    this.processTickets(result.tickets);
                } else {
                    throw new Error(result.message || 'Failed to fetch tickets');
                }
            }

            this.showSuccess('Tickets fetched successfully!');
            document.getElementById('sync-to-clickup-btn').disabled = false;

        } catch (error) {
            console.error('Fetch error:', error);
            this.showError('Failed to fetch tickets: ' + error.message);
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-download mr-2"></i>Fetch Tickets';
            overlay.classList.add('hidden');
        }
    }

    async processTickets(rawTickets) {
        // Categorize tickets using backend API
        const overlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        
        overlay.classList.remove('hidden');
        loadingText.textContent = 'Categorizing tickets...';
        
        try {
            // Send tickets to backend for categorization
            const response = await fetch('/api/categorize-tickets', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tickets: rawTickets })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.tickets = result.categorized_tickets.map(ticket => ({
                    ...ticket,
                    clickup_task_id: null,
                    status: 'Pending',
                    selected: false
                }));
            } else {
                // Fallback to client-side categorization
                this.tickets = rawTickets.map(ticket => {
                    const category = this.categorizeTicket(ticket);
                    const team = this.getTeamForCategory(category);
                    
                    return {
                        ...ticket,
                        predicted_category: category,
                        team: team,
                        clickup_task_id: null,
                        status: 'Pending',
                        selected: false
                    };
                });
            }
        } catch (error) {
            console.error('Backend categorization failed, using fallback:', error);
            // Fallback to client-side categorization
            this.tickets = rawTickets.map(ticket => {
                const category = this.categorizeTicket(ticket);
                const team = this.getTeamForCategory(category);
                
                return {
                    ...ticket,
                    predicted_category: category,
                    team: team,
                    clickup_task_id: null,
                    status: 'Pending',
                    selected: false
                };
            });
        } finally {
            overlay.classList.add('hidden');
        }

        // Remove duplicates
        this.tickets = this.removeDuplicates(this.tickets);
        
        // Initialize filtered tickets
        this.filteredTickets = [...this.tickets];
        
        this.renderTable();
        this.updateStats();
    }

    categorizeTicket(ticket) {
        const text = `${ticket.subject} ${ticket.description}`.toLowerCase();
        
        // Enhanced categorization rules based on knowledge base
        if (text.includes('platform') || text.includes('system') || text.includes('technical') || text.includes('bug') || text.includes('error') || text.includes('crash')) {
            return 'Platform Issues';
        }
        if (text.includes('facilities') || text.includes('room') || text.includes('equipment') || text.includes('projector') || text.includes('wifi')) {
            return 'Facilities';
        }
        if (text.includes('timing') || text.includes('schedule') || text.includes('delay') || text.includes('late') || text.includes('early')) {
            return 'Session Timing Issues';
        }
        if (text.includes('qa') || text.includes('quality') || text.includes('testing') || text.includes('report')) {
            return 'Tech QA Report Issue';
        }
        if (text.includes('on-ground') || text.includes('physical') || text.includes('venue') || text.includes('location')) {
            return 'Other On-Ground Issues';
        }
        if (text.includes('student portal') || text.includes('student login') || text.includes('student access')) {
            return 'Student Portal';
        }
        if (text.includes('scheduling') || text.includes('calendar') || text.includes('appointment') || text.includes('booking')) {
            return 'Scheduling Issue';
        }
        if (text.includes('session handling') || text.includes('class management') || text.includes('session conduct')) {
            return 'Session Handling Issues';
        }
        if (text.includes('quiz') || text.includes('assessment') || text.includes('test') || text.includes('exam') || text.includes('score')) {
            return 'Quiz Issues';
        }
        if (text.includes('portal') && (text.includes('login') || text.includes('access'))) {
            return 'Portal Access';
        }
        if (text.includes('content bundle') || text.includes('curriculum') || text.includes('course')) {
            return 'Content Bundle';
        }
        if (text.includes('content access') || text.includes('material') || text.includes('resource')) {
            return 'Content Access';
        }
        if (text.includes('role') || text.includes('flag') || text.includes('permission')) {
            return 'Feature Flags / Roles Adding';
        }
        if (text.includes('unlock') || text.includes('locked') || text.includes('unit not available')) {
            return 'Units Unlock';
        }
        if (text.includes('instructor') || text.includes('mentor') || text.includes('teacher')) {
            return 'Instructor Categories Adding';
        }
        if (text.includes('data mismatch') || text.includes('looker') || text.includes('studio') || text.includes('analytics')) {
            return 'Data mismatching in lookers studio';
        }
        
        return 'Learning Portal Issues';
    }

    getTeamForCategory(category) {
        const teamMappings = {
            'Platform Issues': 'Product/Tech',
            'Facilities': 'Facilities',
            'Session Timing Issues': 'Curriculum/Content',
            'Tech QA Report Issue': 'Product/Tech',
            'Other On Ground Issues': 'Facilities',
            'Student Portal': 'Product/Tech',
            'Scheduling Issue': 'Curriculum/Content',
            'Session Handling Issues': 'Instructor'
        };
        return teamMappings[category] || 'Product/Tech';
    }

    removeDuplicates(tickets) {
        const seen = new Map();
        const unique = [];
        
        for (const ticket of tickets) {
            const key = `${ticket.subject.toLowerCase()}-${ticket.email}`;
            if (!seen.has(key)) {
                seen.set(key, true);
                unique.push(ticket);
            }
        }
        
        return unique;
    }

    renderTable() {
        const tbody = document.getElementById('tickets-table');
        tbody.innerHTML = '';

        if (this.tickets.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="px-6 py-8 text-center text-gray-500">
                        <i class="fas fa-inbox text-4xl mb-4 text-gray-300"></i>
                        <p>No tickets loaded. Click "Fetch Tickets" to get started.</p>
                    </td>
                </tr>
            `;
            return;
        }

        if (this.filteredTickets.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="px-6 py-8 text-center text-gray-500">
                        <i class="fas fa-filter text-4xl mb-4 text-gray-300"></i>
                        <p>No tickets match the current filters.</p>
                        <button onclick="dashboard.clearFilters()" class="mt-2 text-blue-600 hover:text-blue-800">Clear Filters</button>
                    </td>
                </tr>
            `;
            return;
        }

        this.filteredTickets.forEach((ticket, filteredIndex) => {
            // Find the original index in the full tickets array
            const originalIndex = this.tickets.findIndex(t => t.id === ticket.id);
            const row = document.createElement('tr');
            row.className = this.getRowClass(ticket.team);
            
            row.innerHTML = `
                <td class="px-4 py-3">
                    <input type="checkbox" class="ticket-checkbox rounded" data-index="${originalIndex}" ${ticket.selected ? 'checked' : ''}>
                </td>
                <td class="px-4 py-3 text-sm font-medium text-gray-900">${ticket.id}</td>
                <td class="px-4 py-3 text-sm text-gray-900 max-w-xs truncate" title="${ticket.subject}">${ticket.subject}</td>
                <td class="px-4 py-3 text-sm text-gray-600 max-w-xs truncate" title="${ticket.description}">${ticket.description}</td>
                <td class="px-4 py-3 text-sm text-gray-900">${ticket.predicted_category}</td>
                <td class="px-4 py-3 text-sm font-medium ${this.getTeamColor(ticket.team)}">${ticket.team}</td>
                <td class="px-4 py-3 text-sm text-gray-600">${ticket.clickup_task_id || '-'}</td>
                <td class="px-4 py-3">${this.getStatusBadge(ticket.status)}</td>
                <td class="px-4 py-3">
                    <button class="text-blue-600 hover:text-blue-800 text-sm edit-category-btn" data-index="${originalIndex}">
                        <i class="fas fa-edit mr-1"></i>Edit
                    </button>
                </td>
            `;

            tbody.appendChild(row);
        });

        // Add event listeners for checkboxes and edit buttons
        document.querySelectorAll('.ticket-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.toggleTicketSelection(index, e.target.checked);
            });
        });

        document.querySelectorAll('.edit-category-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const index = parseInt(e.target.closest('button').dataset.index);
                this.openEditModal(index);
            });
        });
    }

    getRowClass(team) {
        const baseClass = 'hover:bg-gray-50';
        switch (team) {
            case 'Product/Tech': return `${baseClass} team-product-tech`;
            case 'Curriculum/Content': return `${baseClass} team-curriculum`;
            case 'Instructor': return `${baseClass} team-instructor`;
            case 'Facilities': return `${baseClass} bg-purple-50`;
            default: return `${baseClass} uncategorized`;
        }
    }

    getTeamColor(team) {
        switch (team) {
            case 'Product/Tech': return 'text-blue-700';
            case 'Curriculum/Content': return 'text-green-700';
            case 'Instructor': return 'text-orange-700';
            case 'Facilities': return 'text-purple-700';
            default: return 'text-red-700';
        }
    }

    getStatusBadge(status) {
        const badges = {
            'Pending': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Pending</span>',
            'Synced': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Synced</span>',
            'Failed': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Failed</span>'
        };
        return badges[status] || badges['Pending'];
    }

    toggleTicketSelection(index, selected) {
        this.tickets[index].selected = selected;
        if (selected) {
            this.selectedTickets.add(index);
        } else {
            this.selectedTickets.delete(index);
        }
        this.updateSelectionCount();
    }

    selectAll(selected) {
        this.selectedTickets.clear();
        
        // Only select/deselect filtered tickets
        this.filteredTickets.forEach(ticket => {
            const originalIndex = this.tickets.findIndex(t => t.id === ticket.id);
            this.tickets[originalIndex].selected = selected;
            if (selected) {
                this.selectedTickets.add(originalIndex);
            }
        });
        
        document.querySelectorAll('.ticket-checkbox').forEach(checkbox => {
            checkbox.checked = selected;
        });
        
        this.updateSelectionCount();
    }

    updateSelectionCount() {
        document.getElementById('selected-count').textContent = this.selectedTickets.size;
        this.updateFilteredStats();
    }

    updateStats() {
        const teamCounts = { 
            'Product/Tech': 0, 
            'Curriculum/Content': 0, 
            'Instructor': 0, 
            'Facilities': 0
        };
        
        this.tickets.forEach(ticket => {
            if (teamCounts.hasOwnProperty(ticket.team)) {
                teamCounts[ticket.team]++;
            }
        });

        document.getElementById('total-tickets').textContent = this.tickets.length;
        document.getElementById('product-tech-count').textContent = teamCounts['Product/Tech'];
        document.getElementById('curriculum-count').textContent = teamCounts['Curriculum/Content'];
        document.getElementById('instructor-count').textContent = teamCounts['Instructor'];
        document.getElementById('facilities-count').textContent = teamCounts['Facilities'];
    }

    sortTable(column) {
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }

        this.filteredTickets.sort((a, b) => {
            let aVal = a[column] || '';
            let bVal = b[column] || '';
            
            if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }

            if (this.sortDirection === 'asc') {
                return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
            } else {
                return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
            }
        });

        this.renderTable();
    }

    openEditModal(index) {
        const ticket = this.tickets[index];
        document.getElementById('edit-ticket-id').value = ticket.id;
        document.getElementById('edit-ticket-subject').value = ticket.subject;
        document.getElementById('edit-category-select').value = ticket.predicted_category;
        document.getElementById('edit-category-modal').style.display = 'block';
        document.getElementById('edit-category-modal').dataset.ticketIndex = index;
    }

    closeEditModal() {
        document.getElementById('edit-category-modal').style.display = 'none';
    }

    saveEditCategory() {
        const index = parseInt(document.getElementById('edit-category-modal').dataset.ticketIndex);
        const newCategory = document.getElementById('edit-category-select').value;
        
        this.tickets[index].predicted_category = newCategory;
        this.tickets[index].team = this.getTeamForCategory(newCategory);
        
        // Reapply filters to update the filtered list
        this.applyFilters();
        this.updateStats();
        this.closeEditModal();
        this.showSuccess('Category updated successfully!');
    }

    applyFilters() {
        this.filteredTickets = this.tickets.filter(ticket => {
            const categoryMatch = !this.filters.category || ticket.predicted_category === this.filters.category;
            const teamMatch = !this.filters.team || ticket.team === this.filters.team;
            return categoryMatch && teamMatch;
        });
        
        this.renderTable();
        this.updateFilteredStats();
    }

    clearFilters() {
        this.filters.category = '';
        this.filters.team = '';
        
        document.getElementById('category-filter').value = '';
        document.getElementById('team-filter').value = '';
        
        this.filteredTickets = [...this.tickets];
        this.renderTable();
        this.updateStats();
        this.showSuccess('Filters cleared!');
    }

    filterByTeam(team) {
        this.filters.team = team;
        this.filters.category = ''; // Clear category filter
        
        document.getElementById('team-filter').value = team;
        document.getElementById('category-filter').value = '';
        
        this.applyFilters();
        this.showSuccess(`Filtered by ${team} team`);
    }

    updateFilteredStats() {
        // Update the selection count based on filtered tickets
        const filteredSelected = Array.from(this.selectedTickets).filter(index => {
            const ticket = this.tickets[index];
            return this.filteredTickets.some(ft => ft.id === ticket.id);
        });
        
        document.getElementById('selected-count').textContent = filteredSelected.length;
        
        // Update the select all checkbox state
        const selectAllCheckbox = document.getElementById('select-all-checkbox');
        if (this.filteredTickets.length === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else {
            const allFilteredSelected = this.filteredTickets.every(ticket => {
                const originalIndex = this.tickets.findIndex(t => t.id === ticket.id);
                return this.selectedTickets.has(originalIndex);
            });
            const someFilteredSelected = this.filteredTickets.some(ticket => {
                const originalIndex = this.tickets.findIndex(t => t.id === ticket.id);
                return this.selectedTickets.has(originalIndex);
            });
            
            selectAllCheckbox.checked = allFilteredSelected;
            selectAllCheckbox.indeterminate = someFilteredSelected && !allFilteredSelected;
        }
    }

    async syncToClickUp() {
        const selectedIndices = Array.from(this.selectedTickets);
        if (selectedIndices.length === 0) {
            this.showError('Please select tickets to sync');
            return;
        }

        const button = document.getElementById('sync-to-clickup-btn');
        const overlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Syncing...';
        overlay.classList.remove('hidden');
        loadingText.textContent = 'Syncing to ClickUp...';

        try {
            const previewMode = document.getElementById('preview-mode').checked;
            
            if (previewMode) {
                // Simulate sync in preview mode
                await this.simulateSync(selectedIndices);
            } else {
                // Real sync to ClickUp
                await this.realSync(selectedIndices);
            }

            this.showSuccess(`Successfully synced ${selectedIndices.length} tickets!`);
            this.selectedTickets.clear();
            this.updateSelectionCount();
            document.getElementById('select-all-checkbox').checked = false;

        } catch (error) {
            console.error('Sync error:', error);
            this.showError('Failed to sync tickets: ' + error.message);
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-upload mr-2"></i>Sync to ClickUp';
            overlay.classList.add('hidden');
        }
    }

    async simulateSync(selectedIndices) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        selectedIndices.forEach(index => {
            this.tickets[index].clickup_task_id = `TASK-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
            this.tickets[index].status = 'Synced';
            this.tickets[index].selected = false;
        });
        
        this.renderTable();
    }

    async realSync(selectedIndices) {
        const ticketsToSync = selectedIndices.map(index => this.tickets[index]);
        
        const response = await fetch('/api/sync-tickets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tickets: ticketsToSync })
        });

        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || 'Sync failed');
        }

        // Update tickets with results
        result.results.forEach((syncResult, i) => {
            const index = selectedIndices[i];
            if (syncResult.success) {
                this.tickets[index].clickup_task_id = syncResult.task_id;
                this.tickets[index].status = 'Synced';
            } else {
                this.tickets[index].status = 'Failed';
            }
            this.tickets[index].selected = false;
        });
        
        this.renderTable();
    }

    refreshTable() {
        this.applyFilters();
        this.updateStats();
        this.showSuccess('Table refreshed!');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    async openUploadModal() {
        document.getElementById('upload-kb-modal').style.display = 'block';
        await this.loadCurrentKnowledgeBase();
    }

    closeUploadModal() {
        document.getElementById('upload-kb-modal').style.display = 'none';
        document.getElementById('kb-file-input').value = '';
    }

    async loadCurrentKnowledgeBase() {
        try {
            const response = await fetch('/api/knowledge-base');
            const data = await response.json();
            
            const preview = document.getElementById('current-kb-preview');
            if (data.success && data.knowledge_base) {
                let html = '<table class="text-xs w-full"><tr><th>Category</th><th>Team</th><th>Keywords</th></tr>';
                data.knowledge_base.forEach(entry => {
                    html += `<tr><td>${entry.category}</td><td>${entry.team}</td><td>${entry.keyword_count} keywords</td></tr>`;
                });
                html += '</table>';
                preview.innerHTML = html;
            } else {
                preview.innerHTML = 'No knowledge base loaded';
            }
        } catch (error) {
            document.getElementById('current-kb-preview').innerHTML = 'Error loading knowledge base';
        }
    }

    async uploadKnowledgeBase() {
        const fileInput = document.getElementById('kb-file-input');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showError('Please select a CSV file');
            return;
        }

        const overlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        
        overlay.classList.remove('hidden');
        loadingText.textContent = 'Uploading knowledge base...';

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/knowledge-base/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccess(`Knowledge base updated with ${result.categories_count} categories`);
                this.closeUploadModal();
                
                // Refresh tickets if any are loaded
                if (this.tickets.length > 0) {
                    this.showSuccess('Re-categorizing existing tickets with new knowledge base...');
                    this.processTickets(this.tickets.map(t => ({
                        id: t.id,
                        subject: t.subject,
                        description: t.description,
                        status: t.status,
                        priority: t.priority,
                        created_time: t.created_time,
                        modified_time: t.modified_time,
                        contact_id: t.contact_id,
                        email: t.email
                    })));
                }
            } else {
                throw new Error(result.message || 'Upload failed');
            }

        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Failed to upload knowledge base: ' + error.message);
        } finally {
            overlay.classList.add('hidden');
        }
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        }`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} mr-2"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize dashboard when DOM is loaded
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new Dashboard();
});