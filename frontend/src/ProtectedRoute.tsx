
import { Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import type { JSX } from "react";
import axios from "axios";

const base_url = import.meta.env.VITE_BASE_URL || "http://localhost:8000";   

export default function ProtectedRoute({ children }: { children: JSX.Element }) {
    const [loading, setLoading] = useState(true);
    const [authenticated, setAuthenticated] = useState(false);


    useEffect(() => {
        const checkAuth = async () => {
            try {
                await axios.get(`${base_url}/me`, {
                    withCredentials: true,
                });

                setAuthenticated(true);

            } catch (error) {
                // access token failed → try refresh
                try {
                    console.log("Access token expired or invalid. Attempting to refresh...");
                    await axios.post(`${base_url}/refresh`, {}, {
                        withCredentials: true,
                    });
                    console.log("Access token refreshed successfully. Verifying...");
                    // try /me again AFTER refresh
                    await axios.get(`${base_url}/me`, {
                        withCredentials: true,
                    });

                    setAuthenticated(true);

                } catch (refreshError) {
                    console.error("Failed to refresh access token.", refreshError);
                    setAuthenticated(false);
                }
            } finally {
                setLoading(false);
            }
        };

        checkAuth();
    }, []);

    if (loading) return <div>Loading...</div>;

    if (!authenticated) {
        return <Navigate to="/" replace />;
    }

    return children;
}

