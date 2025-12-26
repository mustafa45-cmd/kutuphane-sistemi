/**
 * Akıllı Kütüphane Yönetim Sistemi - Frontend JavaScript
 * 
 * Bu dosya, kullanıcı arayüzü ile backend API arasındaki iletişimi yönetir.
 * 
 * Özellikler:
 * - JWT tabanlı kimlik doğrulama
 * - Kitap arama ve listeleme
 * - Ödünç alma istekleri (öğrenci) ve onaylama (admin)
 * - Kitap iade işlemleri
 * - Cezaları görüntüleme
 * - localStorage ile oturum yönetimi
 */

// API base URL'i
const API_BASE = "http://localhost:5000/api";

// Global state: Mevcut kullanıcının token'ı ve bilgileri
let accessToken = null;
let currentUser = null;

/**
 * JWT token'ı decode eder (expiration kontrolü için)
 * @param {string} token - JWT token string
 * @returns {Object|null} Decode edilmiş payload veya null
 */
function decodeJWT(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

/**
 * Token'ı localStorage'dan yükler ve geçerliliğini kontrol eder
 * Sayfa yüklendiğinde otomatik olarak çağrılır
 */
function loadAuth() {
  const savedToken = localStorage.getItem("accessToken");
  const savedUser = localStorage.getItem("currentUser");
  
  if (savedToken && savedUser) {
    try {
      // Token'ı decode et ve expiration kontrolü yap
      const payload = decodeJWT(savedToken);
      if (payload && payload.exp) {
        const now = Math.floor(Date.now() / 1000);
        if (payload.exp > now) {
          // Token geçerli
          accessToken = savedToken;
          currentUser = JSON.parse(savedUser);
          console.log("[AUTH] Token yüklendi (geçerli):", currentUser);
          // UI'ı güncelle ama veri yükleme (sayfa yüklenirken alert göstermemek için)
          updateUI(false); // false = veri yükle
          return;
        } else {
          console.log("[AUTH] Token süresi dolmuş");
        }
      } else {
        console.log("[AUTH] Token decode edilemedi");
      }
    } catch (e) {
      console.error("[AUTH] Token kontrolü başarısız:", e);
    }
    
    // Token geçersizse temizle
    console.log("[AUTH] Token geçersiz, temizleniyor...");
    clearAuth();
  } else {
    console.log("[AUTH] Kayıtlı token yok");
    clearAuth();
  }
}

/**
 * Token ve kullanıcı bilgilerini kaydeder (hem memory hem localStorage)
 * @param {string} token - JWT access token
 * @param {Object} user - Kullanıcı bilgileri (id, full_name, email, role)
 */
function setAuth(token, user) {
  accessToken = token;
  currentUser = user;
  
  if (token && user) {
    localStorage.setItem("accessToken", token);
    localStorage.setItem("currentUser", JSON.stringify(user));
  } else {
    clearAuth();
  }
  
  updateUI();
}

/**
 * Auth bilgilerini temizler (logout işlemi)
 * Hem memory'den hem localStorage'dan siler
 */
function clearAuth() {
  accessToken = null;
  currentUser = null;
  localStorage.removeItem("accessToken");
  localStorage.removeItem("currentUser");
  updateUI();
}

/**
 * Token'ın geçerli olup olmadığını kontrol eder (expiration kontrolü)
 * @returns {boolean} Token geçerliyse true, değilse false
 */
function isTokenValid() {
  if (!accessToken) return false;
  
  const payload = decodeJWT(accessToken);
  if (!payload || !payload.exp) return false;
  
  const now = Math.floor(Date.now() / 1000);
  return payload.exp > now;
}

/**
 * Kullanıcı durumuna göre UI'ı günceller
 * Giriş yapmış kullanıcılar için: kitap listesi, ödünçler, admin istekleri gösterilir
 * Giriş yapmamış kullanıcılar için: login/register formu gösterilir
 * @param {boolean} skipDataLoad - Veri yükleme işlemini atla (sayfa yüklenirken alert göstermemek için)
 */
function updateUI(skipDataLoad = false) {
  const userInfo = document.getElementById("user-info");
  const logoutBtn = document.getElementById("logout-btn");
  const authSection = document.getElementById("auth-section");
  const searchSection = document.getElementById("search-section");
  const loansSection = document.getElementById("loans-section");
  const requestsSection = document.getElementById("requests-section");
  const penaltiesSection = document.getElementById("penalties-section");
  const adminPenaltiesSection = document.getElementById("admin-penalties-section");
  
  // Token geçerliliğini kontrol et
  if (currentUser && accessToken && isTokenValid()) {
    console.log("[UI] Kullanıcı giriş yapmış:", currentUser);
    userInfo.textContent = `${currentUser.full_name} (${currentUser.role})`;
    if (logoutBtn) logoutBtn.classList.remove("hidden");
    if (authSection) authSection.classList.add("hidden");
    if (searchSection) searchSection.classList.remove("hidden");
    if (loansSection) loansSection.classList.remove("hidden");
    if (penaltiesSection) penaltiesSection.classList.remove("hidden");
    
    // Admin ise istekler ve admin cezalar bölümünü göster
    if (currentUser.role === "admin") {
      if (requestsSection) {
        requestsSection.classList.remove("hidden");
        if (!skipDataLoad) {
          loadRequests().catch(e => console.error("[UI] İstekler yüklenirken hata:", e));
        }
      }
      if (adminPenaltiesSection) {
        adminPenaltiesSection.classList.remove("hidden");
        if (!skipDataLoad) {
          loadAdminPenalties().catch(e => console.error("[UI] Admin cezalar yüklenirken hata:", e));
        }
      }
    } else {
      if (requestsSection) requestsSection.classList.add("hidden");
      if (adminPenaltiesSection) adminPenaltiesSection.classList.add("hidden");
    }
    
    // Verileri yükle (sadece skipDataLoad false ise)
    if (!skipDataLoad) {
      loadBooks().catch(e => {
        console.error("[UI] Kitaplar yüklenirken hata:", e);
        // 401 hatası ise token'ı temizle
        if (e.message && (e.message.includes("401") || e.message.includes("Unauthorized"))) {
          console.log("[UI] Token geçersiz, temizleniyor...");
          clearAuth();
        }
      });
      
      loadLoans().catch(e => {
        console.error("[UI] Ödünçler yüklenirken hata:", e);
        // 401 hatası ise token'ı temizle
        if (e.message && (e.message.includes("401") || e.message.includes("Unauthorized"))) {
          console.log("[UI] Token geçersiz, temizleniyor...");
          clearAuth();
        }
      });
      
      loadPenalties().catch(e => {
        console.error("[UI] Cezalar yüklenirken hata:", e);
      });
    }
  } else {
    console.log("[UI] Kullanıcı giriş yapmamış veya token geçersiz, login formu gösteriliyor");
    userInfo.textContent = "";
    if (logoutBtn) logoutBtn.classList.add("hidden");
    if (authSection) {
      authSection.classList.remove("hidden");
      // Login sekmesine geç ve formları temizle
      const loginTab = document.querySelector('.auth-tab[data-tab="login"]');
      if (loginTab) loginTab.click();
      
      const emailInput = document.getElementById("login-email");
      const passwordInput = document.getElementById("login-password");
      if (emailInput) emailInput.value = "";
      if (passwordInput) passwordInput.value = "";
      
      // Register formunu da temizle
      const registerForm = document.getElementById("register-form");
      if (registerForm) registerForm.reset();
    }
    if (searchSection) searchSection.classList.add("hidden");
    if (loansSection) loansSection.classList.add("hidden");
    if (requestsSection) requestsSection.classList.add("hidden");
    if (penaltiesSection) penaltiesSection.classList.add("hidden");
    if (adminPenaltiesSection) adminPenaltiesSection.classList.add("hidden");
  }
}

// Sayfa yüklendiğinde auth'u yükle ve test kullanıcı butonlarını bağla
document.addEventListener("DOMContentLoaded", () => {
  console.log("[APP] Sayfa yüklendi, auth kontrol ediliyor...");
  
  // Önce login formunu göster
  const authSection = document.getElementById("auth-section");
  if (authSection) {
    authSection.classList.remove("hidden");
  }
  
  // Tab geçişi
  document.querySelectorAll(".auth-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const targetTab = tab.getAttribute("data-tab");
      
      // Tüm tab'ları ve içerikleri deaktif et
      document.querySelectorAll(".auth-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".auth-tab-content").forEach(c => c.classList.remove("active"));
      
      // Seçilen tab'ı aktif et
      tab.classList.add("active");
      document.getElementById(`${targetTab}-tab-content`).classList.add("active");
    });
  });
  
  // "Giriş yapın" linki
  const switchToLogin = document.getElementById("switch-to-login");
  if (switchToLogin) {
    switchToLogin.addEventListener("click", (e) => {
      e.preventDefault();
      document.querySelector('.auth-tab[data-tab="login"]').click();
    });
  }
  
  // Form event listener'ları
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  if (loginForm) {
    loginForm.addEventListener("submit", handleLogin);
  }
  if (registerForm) {
    registerForm.addEventListener("submit", handleRegister);
  }
  
  // Sonra token'ı kontrol et ve yükle
  loadAuth();
  
  // Test kullanıcı bilgilerini doldur butonları
  document.querySelectorAll(".fill-credentials-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const email = btn.getAttribute("data-email");
      const password = btn.getAttribute("data-password");
      
      // Login sekmesine geç
      document.querySelector('.auth-tab[data-tab="login"]').click();
      
      const emailInput = document.getElementById("login-email");
      const passwordInput = document.getElementById("login-password");
      
      if (emailInput && passwordInput) {
        emailInput.value = email;
        passwordInput.value = password;
        // Input'ları vurgula
        emailInput.focus();
        setTimeout(() => passwordInput.focus(), 100);
      }
    });
  });
});

/**
 * API istekleri için genel fetch wrapper fonksiyonu
 * Otomatik olarak Authorization header ekler ve hata yönetimi yapar
 * @param {string} path - API endpoint path'i (örn: "/books")
 * @param {Object} options - Fetch options (method, body, headers, vb.)
 * @returns {Promise<Object>} API response data
 */
async function apiFetch(path, options = {}) {
  // Login ve register endpoint'leri için token gerekmez
  const isAuthEndpoint = path === "/auth/login" || path === "/auth/register";
  
  // Token'ı tekrar yükle (güncel olması için)
  const token = accessToken || localStorage.getItem("accessToken");
  
  const headers = options.headers || {};
  headers["Content-Type"] = "application/json";
  if (token && !isAuthEndpoint) {
    headers["Authorization"] = `Bearer ${token}`;
    console.log(`[API] ${options.method || "GET"} ${path} - Token: ${token.substring(0, 20)}...`);
  } else if (!isAuthEndpoint) {
    console.log(`[API] ${options.method || "GET"} ${path} - No token`);
  }
  
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });
    const data = await res.json().catch(() => ({}));
    
    if (!res.ok) {
      // Token hatası ise auth'u temizle (login/register hariç)
      if (res.status === 401 && !isAuthEndpoint) {
        console.error("[API] 401 Unauthorized - Token invalid or expired");
        // Sadece bir kez alert göster ve auth'u temizle
        if (accessToken || localStorage.getItem("accessToken")) {
          const wasLoggedIn = !!accessToken;
          clearAuth();
          // Alert'i sadece kullanıcı etkileşiminde göster (sayfa yüklenirken değil)
          // ve sadece bir kez göster
          if (wasLoggedIn && !window.sessionExpiredShown) {
            window.sessionExpiredShown = true;
            setTimeout(() => {
              alert("Oturum süreniz doldu. Lütfen tekrar giriş yapın.");
              window.sessionExpiredShown = false;
            }, 100);
          }
        }
      }
      
      const errorMsg = data.message || data.error || `HTTP ${res.status}: ${res.statusText}`;
      console.error("API Error:", { path, status: res.status, data, hasToken: !!token, isAuthEndpoint });
      throw new Error(errorMsg);
    }
    return data;
  } catch (err) {
    if (err.message) {
      throw err;
    }
    console.error("Network Error:", err);
    throw new Error("Sunucuya bağlanılamadı. Lütfen backend'in çalıştığından emin olun.");
  }
}

/**
 * Login form submit handler
 * Kullanıcı girişi yapar ve token'ı kaydeder
 * @param {Event} event - Form submit event
 */
async function handleLogin(event) {
  event.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  
  if (!email || !password) {
    alert("Lütfen e-posta ve şifre girin");
    return;
  }
  
  try {
    console.log("[LOGIN] Giriş deneniyor:", email);
    
    // Login endpoint'i için token göndermeden istek yap
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });
    
    const data = await res.json().catch(() => ({}));
    
    if (!res.ok) {
      const errorMsg = data.message || data.error || `HTTP ${res.status}: ${res.statusText}`;
      console.error("[LOGIN] Hata:", errorMsg);
      throw new Error(errorMsg);
    }
    
    console.log("[LOGIN] Başarılı:", data.user);
    setAuth(data.access_token, data.user);
    // sessionExpiredShown flag'ini sıfırla
    window.sessionExpiredShown = false;
    alert("Giriş başarılı!");
  } catch (err) {
    console.error("[LOGIN] Hata:", err);
    alert(err.message || "Giriş yapılamadı. Lütfen bilgilerinizi kontrol edin.");
  }
}

/**
 * Register form submit handler
 * Yeni kullanıcı kaydı oluşturur
 * @param {Event} event - Form submit event
 */
async function handleRegister(event) {
  event.preventDefault();
  const fullName = document.getElementById("register-name").value.trim();
  const email = document.getElementById("register-email").value.trim();
  const password = document.getElementById("register-password").value;
  const passwordConfirm = document.getElementById("register-password-confirm").value;
  
  // Validasyon
  if (!fullName || !email || !password) {
    alert("Lütfen tüm alanları doldurun");
    return;
  }
  
  if (password.length < 6) {
    alert("Şifre en az 6 karakter olmalıdır");
    return;
  }
  
  if (password !== passwordConfirm) {
    alert("Şifreler eşleşmiyor");
    return;
  }
  
  try {
    console.log("[REGISTER] Kayıt deneniyor:", email);
    
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        full_name: fullName,
        email: email,
        password: password,
      }),
    });
    
    const data = await res.json().catch(() => ({}));
    
    if (!res.ok) {
      const errorMsg = data.message || data.error || `HTTP ${res.status}: ${res.statusText}`;
      console.error("[REGISTER] Hata:", errorMsg);
      throw new Error(errorMsg);
    }
    
    console.log("[REGISTER] Başarılı:", data);
    alert("Kayıt başarılı! Giriş yapabilirsiniz.");
    
    // Giriş sekmesine geç ve bilgileri doldur
    document.querySelector('.auth-tab[data-tab="login"]').click();
    document.getElementById("login-email").value = email;
    document.getElementById("login-password").value = password;
    
    // Formu temizle
    document.getElementById("register-form").reset();
  } catch (err) {
    console.error("[REGISTER] Hata:", err);
    alert(err.message || "Kayıt yapılamadı. Lütfen bilgilerinizi kontrol edin.");
  }
}

/**
 * Kitapları API'den yükler ve tabloda gösterir
 * Admin kullanıcılar için "Ödünç Al", öğrenciler için "İstek Gönder" butonu gösterilir
 */
async function loadBooks() {
  const q = document.getElementById("search-query").value || "";
  try {
    const books = await apiFetch(`/books/?q=${encodeURIComponent(q)}`);
    const tbody = document.querySelector("#books-table tbody");
    tbody.innerHTML = "";
    books.forEach((b) => {
      const tr = document.createElement("tr");
      const isAdmin = currentUser && currentUser.role === "admin";
      const buttonText = isAdmin ? "Ödünç Al" : "İstek Gönder";
      const buttonClass = b.available_copies <= 0 ? "disabled" : "";
      
      tr.innerHTML = `
        <td>${b.title}</td>
        <td>${b.author}</td>
        <td>${b.category}</td>
        <td>${b.available_copies}</td>
        <td>
          <button class="${buttonClass}" ${b.available_copies <= 0 ? "disabled" : ""} data-book-id="${b.id}">
            ${buttonText}
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
    tbody.querySelectorAll("button[data-book-id]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (btn.disabled) return;
        const bookId = parseInt(btn.getAttribute("data-book-id"), 10);
        try {
          const isAdmin = currentUser && currentUser.role === "admin";
          const response = await apiFetch("/loans/", {
            method: "POST",
            body: JSON.stringify({ book_id: bookId, days: 14 }),
          });
          
          if (isAdmin) {
            alert("Kitap ödünç verildi!");
          } else {
            alert("Ödünç alma isteği gönderildi! Admin onayı bekleniyor.");
          }
          await loadBooks();
          await loadLoans();
          if (currentUser && currentUser.role === "admin") {
            await loadRequests();
          }
        } catch (err) {
          alert(err.message);
        }
      });
    });
  } catch (err) {
    alert(err.message);
  }
}

/**
 * Kullanıcının ödünç aldığı kitapları yükler ve tabloda gösterir
 * İade edilebilir kitaplar için "İade Et" butonu gösterilir
 */
async function loadLoans() {
  try {
    const loans = await apiFetch("/loans/my");
    const tbody = document.querySelector("#loans-table tbody");
    tbody.innerHTML = "";
    
    if (loans.length === 0) {
      tbody.innerHTML = "<tr><td colspan='5' style='text-align: center;'>Henüz ödünç işleminiz yok</td></tr>";
      return;
    }
    
    loans.forEach((l) => {
      const tr = document.createElement("tr");
      const canReturn = l.status === "borrowed" && !l.return_date;
      
      // Gecikme kontrolü
      const dueDate = new Date(l.due_date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const daysUntilDue = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
      const isOverdue = daysUntilDue < 0 && l.status === "borrowed";
      const isWarning = daysUntilDue <= 3 && daysUntilDue >= 0 && l.status === "borrowed";
      
      let statusText = {
        "requested": "Beklemede",
        "approved": "Onaylandı",
        "borrowed": isOverdue ? `⚠️ Geç (${Math.abs(daysUntilDue)} gün)` : isWarning ? `⚠️ Yaklaşıyor (${daysUntilDue} gün)` : "Ödünç Alındı",
        "returned": "İade Edildi",
        "late": "Geç İade",
        "rejected": "Reddedildi"
      }[l.status] || l.status;
      
      // Gecikme durumunda kırmızı, uyarı durumunda sarı
      const rowClass = isOverdue ? "overdue-row" : isWarning ? "warning-row" : "";
      
      tr.className = rowClass;
      tr.innerHTML = `
        <td>${l.book_title || ""}</td>
        <td>${l.loan_date}</td>
        <td>${l.due_date}</td>
        <td>${statusText}</td>
        <td>
          ${canReturn ? `<button data-loan-id="${l.id}">İade Et</button>` : ""}
        </td>
      `;
      tbody.appendChild(tr);
    });
    tbody.querySelectorAll("button[data-loan-id]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const loanId = parseInt(btn.getAttribute("data-loan-id"), 10);
        try {
          await apiFetch(`/loans/${loanId}/return`, { method: "POST" });
          alert("Kitap iade edildi!");
          await loadBooks();
          await loadLoans();
          await loadPenalties();
          if (currentUser && currentUser.role === "admin") {
            await loadRequests();
            await loadAdminPenalties();
          }
        } catch (err) {
          alert(err.message);
        }
      });
    });
  } catch (err) {
    alert(err.message);
  }
}

/**
 * Bekleyen ödünç alma isteklerini yükler (sadece admin)
 * Admin bu istekleri onaylayabilir veya reddedebilir
 */
async function loadRequests() {
  // Sadece admin için
  if (!currentUser || currentUser.role !== "admin") return;
  
  try {
    const requests = await apiFetch("/loans/requests");
    const requestsSection = document.getElementById("requests-section");
    if (!requestsSection) return;
    
    const requestsTable = document.getElementById("requests-table");
    if (!requestsTable) return;
    const tbody = requestsTable.querySelector("tbody");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    
    if (requests.length === 0) {
      tbody.innerHTML = "<tr><td colspan='6' style='text-align: center;'>Bekleyen istek yok</td></tr>";
      return;
    }
    
    requests.forEach((req) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${req.user_name || ""}</td>
        <td>${req.user_email || ""}</td>
        <td>${req.book_title || ""}</td>
        <td>${req.book_available}</td>
        <td>${req.request_date}</td>
        <td>
          <button class="approve-btn" data-request-id="${req.id}">Onayla</button>
          <button class="reject-btn" data-request-id="${req.id}">Reddet</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
    
    tbody.querySelectorAll("button.approve-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const requestId = parseInt(btn.getAttribute("data-request-id"), 10);
        try {
          await apiFetch(`/loans/${requestId}/approve`, { method: "POST" });
          alert("İstek onaylandı!");
          await loadBooks();
          await loadRequests();
          await loadAdminPenalties();
        } catch (err) {
          alert(err.message);
        }
      });
    });
    
    tbody.querySelectorAll("button.reject-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const requestId = parseInt(btn.getAttribute("data-request-id"), 10);
        if (!confirm("Bu isteği reddetmek istediğinize emin misiniz?")) return;
        try {
          await apiFetch(`/loans/${requestId}/reject`, { method: "POST" });
          alert("İstek reddedildi!");
          await loadRequests();
        } catch (err) {
          alert(err.message);
        }
      });
    });
  } catch (err) {
    console.error("İstekler yüklenirken hata:", err);
  }
}

/**
 * Kullanıcının cezalarını yükler ve gösterir
 */
async function loadPenalties() {
  try {
    const penalties = await apiFetch("/loans/penalties");
    const tbody = document.querySelector("#penalties-table tbody");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    
    // Aktif ceza sayısını hesapla
    let activePenalties = 0;
    let activePenaltyDays = 0;
    
    if (penalties.length === 0) {
      tbody.innerHTML = "<tr><td colspan='5' style='text-align: center;'>Ceza kaydınız bulunmamaktadır</td></tr>";
      document.getElementById("total-penalty-amount").textContent = "Yok";
      return;
    }
    
    penalties.forEach((p) => {
      if (p.is_active) {
        activePenalties++;
        activePenaltyDays = Math.max(activePenaltyDays, p.days_remaining);
      }
      
      const statusText = p.is_active 
        ? `<span style="color: red;">⛔ Aktif (${p.days_remaining} gün kaldı)</span>`
        : '<span style="color: green;">✅ Bitti</span>';
      
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${p.book_title || ""}</td>
        <td>${p.days_late} gün</td>
        <td><strong>${p.is_active ? `${p.days_remaining} gün daha kitap alamazsınız` : 'Ceza süresi doldu'}</strong></td>
        <td>${statusText}</td>
        <td>${new Date(p.penalty_end_date).toLocaleDateString('tr-TR')}</td>
      `;
      tbody.appendChild(tr);
    });
    
    // Özet bilgiyi güncelle
    const totalElement = document.getElementById("total-penalty-amount");
    if (totalElement) {
      if (activePenalties > 0) {
        totalElement.textContent = `${activePenaltyDays} gün daha kitap alamazsınız`;
        totalElement.parentElement.style.background = "#fee2e2";
        totalElement.parentElement.style.borderLeftColor = "#ef4444";
      } else {
        totalElement.textContent = "Aktif ceza yok";
        totalElement.parentElement.style.background = "#fef3c7";
        totalElement.parentElement.style.borderLeftColor = "#f59e0b";
      }
    }
  } catch (err) {
    console.error("Cezalar yüklenirken hata:", err);
  }
}

/**
 * Admin için tüm cezaları yükler ve gösterir
 */
async function loadAdminPenalties() {
  if (!currentUser || currentUser.role !== "admin") return;
  
  try {
    const penalties = await apiFetch("/admin/penalties");
    const tbody = document.querySelector("#admin-penalties-table tbody");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    
    if (penalties.length === 0) {
      tbody.innerHTML = "<tr><td colspan='8' style='text-align: center;'>Ceza kaydı bulunmamaktadır</td></tr>";
      return;
    }
    
    penalties.forEach((p) => {
      const statusText = p.is_active 
        ? `<span style="color: red;">⛔ Aktif (${p.days_remaining} gün kaldı)</span>`
        : '<span style="color: green;">✅ Bitti</span>';
      
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${p.user_name || ""}</td>
        <td>${p.user_email || ""}</td>
        <td>${p.book_title || ""}</td>
        <td>${p.days_late} gün</td>
        <td><strong>${p.is_active ? `${p.days_remaining} gün daha kitap alamaz` : 'Ceza süresi doldu'}</strong></td>
        <td>${statusText}</td>
        <td>${new Date(p.penalty_end_date).toLocaleDateString('tr-TR')}</td>
        <td>
          ${p.is_active ? `<button class="mark-paid-btn" data-penalty-id="${p.id}">Cezayı Kaldır</button>` : ""}
        </td>
      `;
      tbody.appendChild(tr);
    });
    
    // "Cezayı kaldır" butonları
    tbody.querySelectorAll("button.mark-paid-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const penaltyId = parseInt(btn.getAttribute("data-penalty-id"), 10);
        if (!confirm("Bu cezayı kaldırmak istediğinize emin misiniz?")) return;
        
        try {
          await apiFetch(`/admin/penalties/${penaltyId}/remove`, { method: "POST" });
          alert("Ceza kaldırıldı!");
          await loadAdminPenalties();
          await loadPenalties();
        } catch (err) {
          alert(err.message);
        }
      });
    });
  } catch (err) {
    console.error("Admin cezalar yüklenirken hata:", err);
  }
}

document.getElementById("search-button").addEventListener("click", loadBooks);

// Çıkış butonu
document.getElementById("logout-btn").addEventListener("click", () => {
  if (confirm("Çıkış yapmak istediğinize emin misiniz?")) {
    clearAuth();
    alert("Çıkış yapıldı");
  }
});




