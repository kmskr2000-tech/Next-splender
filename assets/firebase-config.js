// Firebase config for multiplayer (poke-splender-c253e project, shared with the original game).
// NOTE: this game uses DB path "ohsp-rooms" (not "pkmspl-rooms"). The Realtime Database rules MUST allow it
// (add this block next to the existing pkmspl-rooms one, or use a new Firebase project):
//     "ohsp-rooms": { ".read": true, "$code": { ".write": true } }
// Realtime Database rules (original):
//   {
//     "rules": {
//       "pkmspl-rooms": {
//         ".read": true,
//         "$code": { ".write": true }
//       }
//     }
//   }
window.__FIREBASE_CONFIG = {
  apiKey: "AIzaSyDPJX9jSvahojG_5LrkQuG-v11IytKbd7E",
  authDomain: "poke-splender-c253e.firebaseapp.com",
  databaseURL: "https://poke-splender-c253e-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "poke-splender-c253e",
  appId: "1:169815564667:web:db0cf7f1bce27eccef5dde",
};
