// import firebaseConfig from './fbconfig';
import {firebaseConfig} from './fbconfig';
import firebase from 'firebase/app';// rollup bundle issue with ESM import
import 'firebase/auth';
import 'firebase/firestore';

// const devConfig  = {
//   apiKey: "AIzaSyAMgZoDGGJ4xa9j5INTkPqy3_9EfqHgYMo",
//   authDomain: "curbside-contact-dev.firebaseapp.com",
//   databaseURL: "https://curbside-contact-dev.firebaseio.com",
//   projectId: "curbside-contact-dev",
//   storageBucket: "curbside-contact-dev.appspot.com",
//   messagingSenderId: "623158898306",
//   appId: "1:623158898306:web:f7e76d0f3243973e250e9b"
// };

// TODO figure out a better way to toggle dev
// maybe https://linguinecode.com/post/how-to-add-environment-variables-to-your-svelte-js-app

firebase.initializeApp(firebaseConfig);
// firebase.initializeApp(devConfig);

export const auth = firebase.auth();
export const googleProvider = new firebase.auth.GoogleAuthProvider();
export const emailProvider = new firebase.auth.EmailAuthProvider();

export const db = firebase.firestore();

export async function getToken() {
  if (auth.currentUser) {
    return await auth.currentUser.getIdToken();
  } else {
    return ""
  }
}



export const arrayAdd = firebase.firestore.FieldValue.arrayUnion;

