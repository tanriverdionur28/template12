import { useEffect, useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = ({ userEmail, onLogout }) => {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setUserData(response.data);
    } catch (error) {
      console.error("Error fetching user data:", error);
      if (error.response?.status === 401) {
        onLogout();
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_email");
    onLogout();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8 pt-8">
          <div>
            <h1 className="text-3xl font-bold text-white" data-testid="dashboard-title">
              Dashboard
            </h1>
            <p className="text-gray-400 mt-1" data-testid="user-email">
              {userEmail}
            </p>
          </div>
          <Button
            onClick={handleLogout}
            variant="outline"
            data-testid="logout-button"
          >
            Çıkış Yap
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card data-testid="welcome-card">
            <CardHeader>
              <CardTitle>Hoş Geldiniz!</CardTitle>
              <CardDescription>
                Başarıyla giriş yaptınız
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p className="text-sm text-gray-500">Yükleniyor...</p>
              ) : userData ? (
                <div className="space-y-2">
                  <p className="text-sm">
                    <span className="font-semibold">E-posta:</span> {userData.email}
                  </p>
                  <p className="text-sm">
                    <span className="font-semibold">Kayıt Tarihi:</span>{" "}
                    {new Date(userData.created_at).toLocaleDateString("tr-TR")}
                  </p>
                </div>
              ) : (
                <p className="text-sm text-gray-500">Veri yüklenemedi</p>
              )}
            </CardContent>
          </Card>

          <Card data-testid="status-card">
            <CardHeader>
              <CardTitle>Sistem Durumu</CardTitle>
              <CardDescription>Tüm sistemler çalışıyor</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-sm text-gray-700">Aktif</span>
              </div>
            </CardContent>
          </Card>

          <Card data-testid="info-card">
            <CardHeader>
              <CardTitle>Bilgi</CardTitle>
              <CardDescription>Uygulama bilgileri</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-700">
                Bu bir demo dashboard sayfasıdır. İhtiyacınıza göre özelleştirilebilir.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
