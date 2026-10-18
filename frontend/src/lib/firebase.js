import { initializeApp, getApps } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSy-Mock-Key",
  authDomain: "fmstar-studio-ai.firebaseapp.com",
  projectId: "fmstar-studio-ai",
  storageBucket: "fmstar-studio-ai.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123:web:abc"
};

// تهيئة Firebase بأمان
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
export const db = getFirestore(app);
export const storage = getStorage(app);
