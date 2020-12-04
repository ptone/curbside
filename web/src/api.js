import { getToken } from './firebase';
import { db } from './firebase';

async function getAuth() {
  let t = await getToken();
  console.log(t);
  var myHeaders = new Headers({
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + t
  });
  return myHeaders;
}


async function sendSMS(reply) {
  let myHeaders = await getAuth();
  let response = await fetch(`/send`, {
    method: 'POST',
    body: JSON.stringify(reply),  
    headers: myHeaders
  });
  let myJson = await response.json();
  console.log(myJson);
  return myJson
}

async function getCNAM(session, sender) {
  let cid = db.collection('caller_ids').doc(sender).get().then(async function(doc) {
    if (doc.exists) {
        console.log("Document data:", doc.data());
        const cnam = doc.data().cnam;
        if (cnam == 'none') {
          cnam = false;
        }
        db.collection('sessions').doc(session).update({
          'caller_id': cnam
        })
        return cnam
    } else {
        // doc.data() will be undefined in this case
        console.log("No such document!");
        let myHeaders = await getAuth();
        const apiReq = {
          sender: sender,
          session: session
        }
        let response = await fetch(`/cnam`, {
          method: 'POST',
          body: JSON.stringify(apiReq),  
          headers: myHeaders
        });
        let myJson = await response.json();
        console.log(myJson);
        return myJson.cnam
    }
    }).catch(function(error) {
        console.log("Error getting document:", error);
    });

}

export { sendSMS, getCNAM }
