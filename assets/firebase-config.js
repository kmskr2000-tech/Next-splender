// Firebase config for multiplayer (dedicated "next-splender" project, separate from the original game).
// DB path: "ohsp-rooms". Realtime Database rules:
//   {
//     "rules": {
//       "ohsp-rooms": {
//         ".read": true,
//         "$code": { ".write": true, ".validate": "$code.matches(/^[A-HJKMNP-Z2-9]{6}$/)" }
//       }
//     }
//   }
window.__FIREBASE_CONFIG = {
  apiKey: "AIzaSyDcldz4LmkM1XGID9zLDsOk_PHQGWwwPSg",
  authDomain: "next-splender.firebaseapp.com",
  databaseURL: "https://next-splender-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "next-splender",
  appId: "1:1087721820665:web:be847a7a7c87ff5c75ed28",
};
