// Yemekhane Otomasyonu · API İstemcisi
const API = {
    getToken() {
        return localStorage.getItem('yemekhane_token');
    },

    setToken(token) {
        if (token) {
            localStorage.setItem('yemekhane_token', token);
        } else {
            localStorage.removeItem('yemekhane_token');
        }
    },

    getUser() {
        const u = localStorage.getItem('yemekhane_kullanici');
        return u ? JSON.parse(u) : null;
    },

    setUser(user) {
        if (user) {
            localStorage.setItem('yemekhane_kullanici', JSON.stringify(user));
        } else {
            localStorage.removeItem('yemekhane_kullanici');
        }
    },

    async login(eposta, sifre) {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ eposta, sifre })
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || 'Giriş yapılamadı.');
        }
        this.setToken(data.token);
        this.setUser(data.kullanici);
        return data;
    },

    async logout() {
        const token = this.getToken();
        try {
            if (token) {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
            }
        } finally {
            this.setToken(null);
            this.setUser(null);
        }
    },

    async me() {
        const token = this.getToken();
        if (!token) return null;
        const res = await fetch('/api/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) {
            this.setToken(null);
            this.setUser(null);
            return null;
        }
        return await res.json();
    },

    // Menü Servisi İstekleri
    async getCafeterias() {
        const res = await fetch('/api/cafeterias');
        return await res.json();
    },

    async getMeals() {
        const res = await fetch('/api/meals');
        return await res.json();
    },

    async getTodayMenu(yemekhaneId = 1, ogunId = 2, tarih = null) {
        let url = `/api/menus/today?yemekhane_id=${yemekhaneId}&ogun_id=${ogunId}`;
        if (tarih) url += `&tarih=${tarih}`;
        const headers = {};
        const token = this.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const res = await fetch(url, { headers });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.hata || 'Günün menüsü bulunamadı.');
        }
        return await res.json();
    },

    async getWeekMenu(yemekhaneId = 1, baslangic = null) {
        let url = `/api/menus/week?yemekhane_id=${yemekhaneId}`;
        if (baslangic) url += `&baslangic=${baslangic}`;
        const headers = {};
        const token = this.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const res = await fetch(url, { headers });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.hata || 'Haftalık menü getirilemedi.');
        }
        return await res.json();
    },

    // Rezervasyon & Bakiye Servisi İstekleri
    async makeReservation(menuId, porsiyon = 'tam') {
        const token = this.getToken();
        if (!token) throw new Error('Rezervasyon için giriş yapmalısınız.');
        const res = await fetch('/api/reservations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ menu_id: menuId, porsiyon: porsiyon })
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            throw new Error(data.hata || data.detail || 'Rezervasyon yapılamadı.');
        }
        // Başarılı rezervasyon sonrası yerel kullanıcı bakiyesini güncelle
        const user = this.getUser();
        if (user && data.yeni_bakiye !== undefined) {
            user.bakiye = data.yeni_bakiye;
            this.setUser(user);
        }
        return data;
    },

    async cancelReservation(reservationId) {
        const token = this.getToken();
        if (!token) throw new Error('İptal için giriş yapmalısınız.');
        const res = await fetch(`/api/reservations/${reservationId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            throw new Error(data.hata || data.detail || 'İptal işlemi başarısız.');
        }
        const user = this.getUser();
        if (user && data.yeni_bakiye !== undefined) {
            user.bakiye = data.yeni_bakiye;
            this.setUser(user);
        }
        return data;
    },

    async getMyReservations() {
        const token = this.getToken();
        if (!token) throw new Error('Lütfen giriş yapın.');
        const res = await fetch('/api/reservations/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || 'Rezervasyonlar alınamadı.');
        }
        return await res.json();
    },

    async getBalance() {
        const token = this.getToken();
        if (!token) throw new Error('Lütfen giriş yapın.');
        const res = await fetch('/api/balance', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || 'Bakiye bilgisi alınamadı.');
        }
        const data = await res.json();
        const user = this.getUser();
        if (user) {
            user.bakiye = data.bakiye;
            this.setUser(user);
        }
        return data;
    },

    async topupBalance(tutar) {
        const token = this.getToken();
        if (!token) throw new Error('Lütfen giriş yapın.');
        const res = await fetch('/api/balance/topup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ tutar })
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.hata || data.detail || 'Yükleme başarısız.');
        }
        const user = this.getUser();
        if (user && data.yeni_bakiye !== undefined) {
            user.bakiye = data.yeni_bakiye;
            this.setUser(user);
        }
        return data;
    },

    // Değerlendirme Servisi İstekleri
    async getReviews(menuId) {
        const res = await fetch(`/api/reviews?menu_id=${menuId}`);
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.hata || 'Değerlendirmeler alınamadı.');
        }
        return await res.json();
    },

    async postReview(menuId, puan, yorum = '') {
        const token = this.getToken();
        if (!token) throw new Error('Değerlendirme için giriş yapmalısınız.');
        const res = await fetch('/api/reviews', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ menu_id: menuId, puan, yorum })
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.hata || data.detail || 'Değerlendirme kaydedilemedi.');
        }
        return data;
    },

    // Yönetim Servisi İstekleri
    async getAdminStats() {
        const token = this.getToken();
        if (!token) throw new Error('Yönetici girişi gereklidir.');
        const res = await fetch('/api/admin/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || 'İstatistikler alınamadı.');
        }
        return await res.json();
    },

    async getAdminMenus(tarih = '') {
        const token = this.getToken();
        let url = '/api/admin/menus';
        if (tarih) url += `?tarih=${tarih}`;
        const res = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || data.hata || 'Menüler alınamadı.');
        }
        return await res.json();
    },

    async getAdminMenuDetail(id) {
        const token = this.getToken();
        const res = await fetch(`/api/admin/menus/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || data.hata || 'Menü detayı alınamadı.');
        }
        return await res.json();
    },

    async createAdminMenu(menuData) {
        const token = this.getToken();
        const res = await fetch('/api/admin/menus', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(menuData)
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || data.hata || 'Menü oluşturulamadı.');
        }
        return data;
    },

    async updateAdminMenuPrice(id, ogrenci_fiyati, personel_fiyati) {
        const token = this.getToken();
        const res = await fetch(`/api/admin/menus/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ ogrenci_fiyati, personel_fiyati })
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || data.hata || 'Fiyat güncellenemedi.');
        }
        return data;
    },

    async addAdminMenuItem(menuId, yemekId) {
        const token = this.getToken();
        const res = await fetch(`/api/admin/menus/${menuId}/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ yemek_id: yemekId })
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || data.hata || 'Yemek eklenemedi.');
        }
        return data;
    },

    async removeAdminMenuItem(menuId, yemekId) {
        const token = this.getToken();
        const res = await fetch(`/api/admin/menus/${menuId}/items/${yemekId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || data.hata || 'Yemek çıkarılamadı.');
        }
        return data;
    },

    async getAdminFoods() {
        const token = this.getToken();
        const res = await fetch('/api/admin/foods', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || data.hata || 'Yemekler alınamadı.');
        }
        return await res.json();
    },

    async deleteAdminMenu(id) {
        const token = this.getToken();
        const res = await fetch(`/api/admin/menus/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || data.hata || 'Menü silinemedi.');
        }
        return data;
    },

    async getAdminReservations(tarih = '', durum = '', rol = '') {
        const token = this.getToken();
        let url = '/api/reservations/admin';
        const params = [];
        if (tarih) params.push(`tarih=${tarih}`);
        if (durum) params.push(`durum=${durum}`);
        if (rol) params.push(`rol=${rol}`);
        if (params.length) url += '?' + params.join('&');

        const res = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || data.hata || 'Rezervasyonlar alınamadı.');
        }
        return await res.json();
    },

    async adminCancelReservation(id) {
        const token = this.getToken();
        const res = await fetch(`/api/reservations/admin/${id}/cancel`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || data.hata || 'Rezervasyon iptal edilemedi.');
        }
        return data;
    },

    async getAdminReviews() {
        const token = this.getToken();
        const res = await fetch('/api/reviews?admin=1', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || data.hata || 'Değerlendirmeler alınamadı.');
        }
        return await res.json();
    },

    async getAllergens() {
        const token = this.getToken();
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;
        let url = '/api/allergens';
        if (token) url += `?token=${encodeURIComponent(token)}`;
        let res = await fetch(url, { headers });
        if (!res.ok) {
            res = await fetch('/api/auth/allergens' + (token ? `?token=${encodeURIComponent(token)}` : ''), { headers });
        }
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || data.hata || 'Alerjenler alınamadı.');
        }
        return await res.json();
    },

    async saveAllergens(allergenIds) {
        const token = this.getToken();
        if (!token) throw new Error('Alerjen kaydetmek için giriş yapmalısınız.');
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
        const body = JSON.stringify({ alerjen_idler: allergenIds });
        let url = `/api/allergens?token=${encodeURIComponent(token)}`;
        let res = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: body
        });
        if (!res.ok && (res.status === 401 || res.status === 404)) {
            res = await fetch(`/api/auth/allergens?token=${encodeURIComponent(token)}`, {
                method: 'POST',
                headers: headers,
                body: body
            });
        }
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            throw new Error(data.detail || data.hata || 'Alerjenler kaydedilemedi.');
        }
        // Kullanıcı objesindeki alerjen listesini güncelle
        const user = this.getUser();
        if (user) {
            user.alerjenler = data.kullanici_alerjenleri || allergenIds;
            this.setUser(user);
        }
        return data;
    }
};
