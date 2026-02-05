import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Profile.css";

/* 🔧 BACKEND BASE URL
   Replace with your deployed backend URL on Render */
const AUTH_ME_API =
  "https://ai-powered-precision-agriculture-advisor.onrender.com/api/auth/me";


const Profile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Decide avatar based on gender or name
  const getAvatar = (name, gender) => {
    if (gender) {
      if (gender.toLowerCase() === "female") {
        return "https://cdn-icons-png.flaticon.com/512/2922/2922561.png";
      }
      return "https://cdn-icons-png.flaticon.com/512/2922/2922510.png";
    }

    // fallback name-based detection
    const femaleNames = [
      "ananya", "isha", "shruti", "punya",
      "aishu", "priya", "sneha", "deepa", "radhika"
    ];

    if (femaleNames.includes(name?.toLowerCase())) {
      return "https://cdn-icons-png.flaticon.com/512/2922/2922561.png";
    }

    return "https://cdn-icons-png.flaticon.com/512/2922/2922510.png";
  };

  // Fetch user profile
  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      setLoading(false);
      return;
    }

    fetch(AUTH_ME_API, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        setProfile(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="profile-loading">Loading...</div>;
  if (!profile) return <div className="profile-error">Profile not found.</div>;

  return (
    <div className="profile-container">
      <div className="profile-card">

        <div className="profile-header">
          <img
            src={getAvatar(profile.name, profile.gender)}
            alt="User Avatar"
            className="profile-avatar"
          />
          <h2>{profile.name}</h2>
          <p className="profile-email">{profile.email}</p>
        </div>

        <div className="profile-details">
          <h3>User Details</h3>
          <p><strong>Phone:</strong> {profile.phone}</p>
          <p><strong>State:</strong> {profile.state}</p>
          <p><strong>District:</strong> {profile.district}</p>
          <p><strong>Farm Size:</strong> {profile.farmSize} acres</p>
        </div>

        <div className="profile-actions">
          <button
            className="btn-dashboard"
            onClick={() => navigate("/dashboard")}
          >
            ⬅ Back to Dashboard
          </button>

          <button
            className="btn-logout"
            onClick={() => {
              localStorage.removeItem("token");
              navigate("/login");
            }}
          >
            🚪 Logout
          </button>
        </div>

      </div>
    </div>
  );
};

export default Profile;
