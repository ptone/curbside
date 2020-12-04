import { writable } from 'svelte/store';
import { db, auth } from './firebase';
import { authState } from 'rxfire/auth';
import { doc } from 'rxfire/firestore';
import 'firebase/auth';
import { filter } from 'rxjs/operators';


export const userSettings = writable({});
export const tenantSettings = writable({});
export const systemSettings = writable({});

export const tenantNumber = writable('');
export let tenantNumberVar;

// Listen only for logged in state
const loggedIn$ = authState(auth).pipe(filter(user => !!user));
loggedIn$.subscribe(user => { 
  const userSettingsDoc = db.collection('settings').doc(user.uid);
  doc(userSettingsDoc).subscribe(snapshot => {
    userSettings.set(snapshot.data());
  });

  user.getIdTokenResult().then((idTokenResult) => {
    tenantNumber.set(idTokenResult.claims.curbside_number);
    tenantNumberVar = idTokenResult.claims.curbside_number;
    const tenantSettingsDoc = db.collection('settings').doc(idTokenResult.claims.curbside_number);
    doc(tenantSettingsDoc).subscribe(snapshot => {
      tenantSettings.set(snapshot.data());
    });
  })
});


export function storeUserSettings(data) {
  let uid = auth.currentUser.uid;
  console.log("storeUserSettings");
  console.log(uid);
  console.log(data);
  return db.collection('settings').doc(uid).set(data);
}

export function storetenantSettings(data) {
  return db.collection('settings').doc(tenantNumberVar).update(data);
}