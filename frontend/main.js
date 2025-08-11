const { createApp } = Vue;

createApp({
    data() {
        return {
            newListener: {
                email: '',
                searchTerm: ''
            },
            searchEmail: '',
            testEmailAddress: '',
            listeners: [],
            stats: null,
            loading: false,
            notification: null,
            apiBaseUrl: 'http://localhost:5000/api'
        }
    },
    
    mounted() {
        this.loadStats();
    },
    
    methods: {
        async addListener() {
            if (!this.newListener.email || !this.newListener.searchTerm) {
                this.showNotification('Please fill in all fields', 'error');
                return;
            }
            
            this.loading = true;
            
            try {
                const response = await axios.post(`${this.apiBaseUrl}/listeners`, {
                    email: this.newListener.email,
                    search_term: this.newListener.searchTerm
                });
                
                this.showNotification('Listener added successfully! You will receive email notifications when matching items are found.', 'success');
                
                // Clear form
                this.newListener = { email: '', searchTerm: '' };
                
                // Reload stats
                this.loadStats();
                
                // If the search email matches, reload listeners
                if (this.searchEmail === response.data.listener.email) {
                    this.loadListeners();
                }
                
            } catch (error) {
                let message = 'Failed to add listener';
                if (error.response?.data?.error) {
                    message = error.response.data.error;
                }
                this.showNotification(message, 'error');
            } finally {
                this.loading = false;
            }
        },
        
        async loadListeners() {
            if (!this.searchEmail) {
                this.showNotification('Please enter an email address', 'error');
                return;
            }
            
            this.loading = true;
            
            try {
                const response = await axios.get(`${this.apiBaseUrl}/listeners/${encodeURIComponent(this.searchEmail)}`);
                this.listeners = response.data.listeners;
                
                if (this.listeners.length === 0) {
                    this.showNotification('No listeners found for this email address', 'info');
                }
                
            } catch (error) {
                let message = 'Failed to load listeners';
                if (error.response?.data?.error) {
                    message = error.response.data.error;
                }
                this.showNotification(message, 'error');
                this.listeners = [];
            } finally {
                this.loading = false;
            }
        },
        
        async deleteListener(listenerId) {
            if (!confirm('Are you sure you want to remove this listener?')) {
                return;
            }
            
            this.loading = true;
            
            try {
                await axios.delete(`${this.apiBaseUrl}/listeners/${listenerId}`);
                this.showNotification('Listener removed successfully', 'success');
                
                // Remove from local list
                this.listeners = this.listeners.filter(l => l.id !== listenerId);
                
                // Reload stats
                this.loadStats();
                
            } catch (error) {
                let message = 'Failed to remove listener';
                if (error.response?.data?.error) {
                    message = error.response.data.error;
                }
                this.showNotification(message, 'error');
            } finally {
                this.loading = false;
            }
        },
        
        async testEmail() {
            if (!this.testEmailAddress) {
                this.showNotification('Please enter an email address for the test', 'error');
                return;
            }
            
            this.loading = true;
            
            try {
                await axios.post(`${this.apiBaseUrl}/test-email`, {
                    email: this.testEmailAddress
                });
                
                this.showNotification('Test email sent successfully! Check your inbox.', 'success');
                
            } catch (error) {
                let message = 'Failed to send test email';
                if (error.response?.data?.error) {
                    message = error.response.data.error;
                }
                this.showNotification(message, 'error');
            } finally {
                this.loading = false;
            }
        },
        
        async manualCheck() {
            this.loading = true;
            
            try {
                await axios.post(`${this.apiBaseUrl}/manual-check`);
                this.showNotification('Manual auction check started! This will run in the background.', 'info');
                
            } catch (error) {
                let message = 'Failed to start manual check';
                if (error.response?.data?.error) {
                    message = error.response.data.error;
                }
                this.showNotification(message, 'error');
            } finally {
                this.loading = false;
            }
        },
        
        async loadStats() {
            try {
                const response = await axios.get(`${this.apiBaseUrl}/stats`);
                this.stats = response.data;
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        },
        
        showNotification(message, type) {
            this.notification = { message, type };
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                if (this.notification && this.notification.message === message) {
                    this.notification = null;
                }
            }, 5000);
        },
        
        formatDate(dateString) {
            if (!dateString) return 'Unknown';
            
            try {
                const date = new Date(dateString);
                return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            } catch (error) {
                return dateString;
            }
        }
    }
}).mount('#app');
