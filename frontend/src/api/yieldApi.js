import axios from "axios";

const API_URL = "http://127.0.0.1:5000/api/yield-predict";

export const predictYield = async (payload) => {
  try {
    const res = await axios.post(API_URL, payload);
    return res.data;
  } catch (error) {
    return error.response?.data || { error: "Server error" };
  }
};
