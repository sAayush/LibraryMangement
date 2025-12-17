// API Configuration
const API_BASE_URL = window.location.origin + '/api';
let authToken = localStorage.getItem('authToken');
let currentUser = null;

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeAuth();
    loadDashboardData();
});

// Navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link[data-section]');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionName = link.dataset.section;
            showSection(sectionName);
            
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

function showSection(sectionName) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));
    
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
        
        // Load section-specific data
        if (sectionName === 'books') {
            loadBooks();
        } else if (sectionName === 'loans') {
            loadLoans();
        }
    }
}

// Authentication
function initializeAuth() {
    const authBtn = document.getElementById('authBtn');
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const closeBtns = document.querySelectorAll('.close');
    
    // Check if user is logged in
    if (authToken) {
        fetchCurrentUser();
    }
    
    // Auth button click
    authBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (authToken) {
            logout();
        } else {
            loginModal.classList.add('active');
        }
    });
    
    // Close modals
    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            loginModal.classList.remove('active');
            registerModal.classList.remove('active');
        });
    });
    
    // Show register
    document.getElementById('showRegister').addEventListener('click', (e) => {
        e.preventDefault();
        loginModal.classList.remove('active');
        registerModal.classList.add('active');
    });
    
    // Show login
    document.getElementById('showLogin').addEventListener('click', (e) => {
        e.preventDefault();
        registerModal.classList.remove('active');
        loginModal.classList.add('active');
    });
    
    // Login form
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                authToken = data.access;
                localStorage.setItem('authToken', authToken);
                loginModal.classList.remove('active');
                fetchCurrentUser();
                showNotification('Login successful!', 'success');
                loadDashboardData();
            } else {
                showNotification(data.detail || 'Login failed', 'error');
            }
        } catch (error) {
            showNotification('Network error', 'error');
        }
    });
    
    // Register form
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        const password2 = document.getElementById('regPassword2').value;
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password, password2 })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showNotification('Registration successful! Please login.', 'success');
                registerModal.classList.remove('active');
                loginModal.classList.add('active');
            } else {
                const errorMsg = Object.values(data).flat().join(', ');
                showNotification(errorMsg || 'Registration failed', 'error');
            }
        } catch (error) {
            showNotification('Network error', 'error');
        }
    });
}

async function fetchCurrentUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/me/`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            document.getElementById('authBtn').textContent = `Logout (${currentUser.username})`;
        } else {
            logout();
        }
    } catch (error) {
        console.error('Error fetching user:', error);
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    document.getElementById('authBtn').textContent = 'Login';
    showNotification('Logged out successfully', 'success');
    loadDashboardData();
}

// Load Dashboard Data
async function loadDashboardData() {
    await Promise.all([
        loadStats(),
        loadBooks()
    ]);
}

async function loadStats() {
    try {
        const headers = authToken ? { 'Authorization': `Bearer ${authToken}` } : {};
        
        // Fetch books
        const booksResponse = await fetch(`${API_BASE_URL}/books/`, { headers });
        const booksData = await booksResponse.json();
        
        const totalBooks = booksData.count || 0;
        const availableBooks = booksData.results?.filter(b => b.is_available).length || 0;
        
        document.getElementById('totalBooks').textContent = totalBooks;
        document.getElementById('availableBooks').textContent = availableBooks;
        
        // Fetch loans (if authenticated)
        if (authToken) {
            const loansResponse = await fetch(`${API_BASE_URL}/loans/my-loans/`, { headers });
            if (loansResponse.ok) {
                const loansData = await loansResponse.json();
                document.getElementById('activeLoans').textContent = loansData.count || 0;
            }
        }
        
        // Fetch users (if admin)
        if (authToken && currentUser?.is_admin) {
            const usersResponse = await fetch(`${API_BASE_URL}/users/`, { headers });
            if (usersResponse.ok) {
                const usersData = await usersResponse.json();
                document.getElementById('totalUsers').textContent = usersData.count || 0;
            }
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Track current search term for pagination
let currentBookSearch = '';

async function loadBooks(page = 1, search = '') {
    currentBookSearch = search; // Store current search
    const container = document.getElementById('booksContainer');
    container.innerHTML = '<p class="loading">Loading books...</p>';
    
    try {
        const headers = authToken ? { 'Authorization': `Bearer ${authToken}` } : {};
        const searchParam = search ? `&search=${encodeURIComponent(search)}` : '';
        const response = await fetch(`${API_BASE_URL}/books/?page=${page}${searchParam}`, { headers });
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            container.innerHTML = data.results.map(book => createBookCard(book)).join('');
            
            // Add borrow button listeners
            container.querySelectorAll('.btn-borrow').forEach(btn => {
                btn.addEventListener('click', () => borrowBook(btn.dataset.bookId));
            });
        } else {
            container.innerHTML = '<p class="loading">No books found</p>';
        }
        
        // Update pagination - pass function that maintains search
        updatePagination('booksPagination', data, page, (p) => loadBooks(p, currentBookSearch));
    } catch (error) {
        container.innerHTML = '<p class="loading">Error loading books</p>';
        console.error('Error loading books:', error);
    }
}

function createBookCard(book) {
    const canBorrow = authToken && book.is_available;
    return `
        <div class="book-card">
            <img src="${book.cover_image || '/static/img/book-placeholder.png'}" 
                 alt="${book.title}" 
                 class="book-cover"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22280%22 height=%22200%22%3E%3Crect fill=%22%232563eb%22 width=%22280%22 height=%22200%22/%3E%3Ctext fill=%22white%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 font-size=%2220%22%3E📚%3C/text%3E%3C/svg%3E'">
            <div class="book-info">
                <h3 class="book-title">${book.title}</h3>
                <p class="book-author">by ${book.author}</p>
                <p class="book-meta">
                    <span class="book-status ${book.is_available ? 'status-available' : 'status-borrowed'}">
                        ${book.is_available ? 'Available' : 'Borrowed'}
                    </span>
                    <span>${book.available_copies}/${book.total_copies} copies</span>
                </p>
                ${canBorrow ? `<button class="btn-borrow" data-book-id="${book.id}">Borrow</button>` : ''}
            </div>
        </div>
    `;
}

async function borrowBook(bookId) {
    if (!authToken) {
        showNotification('Please login to borrow books', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/loans/borrow/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ book: bookId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Book borrowed successfully!', 'success');
            loadBooks();
            loadStats();
        } else {
            const errorMsg = Object.values(data).flat().join(', ');
            showNotification(errorMsg || 'Failed to borrow book', 'error');
        }
    } catch (error) {
        showNotification('Network error', 'error');
    }
}

async function loadLoans(page = 1) {
    if (!authToken) {
        document.getElementById('loansContainer').innerHTML = 
            '<p class="loading">Please login to view loans</p>';
        return;
    }
    
    const container = document.getElementById('loansContainer');
    container.innerHTML = '<p class="loading">Loading loans...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/loans/my-loans/?page=${page}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            container.innerHTML = data.results.map(loan => createLoanCard(loan)).join('');
            
            // Add action button listeners
            container.querySelectorAll('.btn-return').forEach(btn => {
                btn.addEventListener('click', () => returnBook(btn.dataset.loanId));
            });
            container.querySelectorAll('.btn-renew').forEach(btn => {
                btn.addEventListener('click', () => renewLoan(btn.dataset.loanId));
            });
        } else {
            container.innerHTML = '<p class="loading">No active loans</p>';
        }
        
        // Update pagination - pass function reference directly
        updatePagination('loansPagination', data, page, (p) => loadLoans(p));
    } catch (error) {
        container.innerHTML = '<p class="loading">Error loading loans</p>';
        console.error('Error loading loans:', error);
    }
}

function createLoanCard(loan) {
    const dueDate = new Date(loan.due_date).toLocaleDateString();
    const isActive = loan.status === 'ACTIVE';
    
    return `
        <div class="loan-card">
            <div class="loan-info">
                <h4>${loan.book.title}</h4>
                <div class="loan-meta">
                    <span>Due: ${dueDate}</span>
                    <span>Status: ${loan.status}</span>
                    <span>Renewals: ${loan.renewed_count}/${loan.max_renewals}</span>
                </div>
            </div>
            <div class="loan-actions">
                ${isActive ? `
                    <button class="btn-secondary btn-renew" data-loan-id="${loan.id}">Renew</button>
                    <button class="btn-primary btn-return" data-loan-id="${loan.id}">Return</button>
                ` : ''}
            </div>
        </div>
    `;
}

async function returnBook(loanId) {
    try {
        const response = await fetch(`${API_BASE_URL}/loans/${loanId}/return/`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            showNotification('Book returned successfully!', 'success');
            loadLoans();
            loadStats();
        } else {
            showNotification('Failed to return book', 'error');
        }
    } catch (error) {
        showNotification('Network error', 'error');
    }
}

async function renewLoan(loanId) {
    try {
        const response = await fetch(`${API_BASE_URL}/loans/${loanId}/renew/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ days: 14 })
        });
        
        if (response.ok) {
            showNotification('Loan renewed successfully!', 'success');
            loadLoans();
        } else {
            const data = await response.json();
            const errorMsg = Object.values(data).flat().join(', ');
            showNotification(errorMsg || 'Failed to renew loan', 'error');
        }
    } catch (error) {
        showNotification('Network error', 'error');
    }
}

// Pagination
function updatePagination(containerId, data, currentPage, loadFunction) {
    const container = document.getElementById(containerId);
    if (!data.count || data.count <= 10) {
        container.innerHTML = '';
        return;
    }
    
    const totalPages = Math.ceil(data.count / 10);
    container.innerHTML = ''; // Clear existing buttons
    
    // Previous button
    if (data.previous) {
        const prevBtn = document.createElement('button');
        prevBtn.textContent = 'Previous';
        prevBtn.addEventListener('click', () => loadFunction(currentPage - 1));
        container.appendChild(prevBtn);
    }
    
    // Page number buttons
    for (let i = 1; i <= totalPages; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        if (i === currentPage) {
            pageBtn.classList.add('active');
        }
        pageBtn.addEventListener('click', () => loadFunction(i));
        container.appendChild(pageBtn);
    }
    
    // Next button
    if (data.next) {
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Next';
        nextBtn.addEventListener('click', () => loadFunction(currentPage + 1));
        container.appendChild(nextBtn);
    }
}

// Search
document.getElementById('searchBtn')?.addEventListener('click', () => {
    const search = document.getElementById('bookSearch').value;
    loadBooks(1, search);
});

document.getElementById('bookSearch')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const search = e.target.value;
        loadBooks(1, search);
    }
});

// My Loans Button
document.getElementById('myLoansBtn')?.addEventListener('click', () => {
    loadLoans();
});

// Notification System
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

