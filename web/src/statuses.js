import { writable } from 'svelte/store'
import { db, auth } from './firebase';
import { collectionData } from 'rxfire/firestore';
import { authState } from 'rxfire/auth';
import { empty } from 'rxjs';
import { filter, startWith } from 'rxjs/operators';
import 'firebase/auth'

export let statuses = empty().pipe(startWith([]));


export let statusByLabel = {};

export function getStatusColor(label) {
  if (statusByLabel[label]) {
    return statusByLabel[label].color;
  } else {
    return 'black';
  }
}

export function getStatusResponse(label) {
  return statusByLabel[label].response;
}

const loggedIn$ = authState(auth).pipe(filter(user => !!user));
loggedIn$.subscribe(user => {
  user.getIdTokenResult().then((idTokenResult) => {
    const statusQuery = db.collection('statuses').where('tenant', '==', idTokenResult.claims.curbside_number || '').orderBy('sequence').orderBy('created')
    const statusesObs = collectionData(statusQuery, 'id')
    statuses = statusesObs.pipe(startWith([]));
    statusesObs.subscribe((statusData) => {
      console.log(statusData);
      statusByLabel = {};
      for (const stat of statusData) {
        statusByLabel[stat.label] = stat;
      }
    })
  })
});