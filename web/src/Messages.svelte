<script>
    import { db } from './firebase';
    import { collectionData } from 'rxfire/firestore';
    import { startWith } from 'rxjs/operators';

    export let msgsender;
    export let msgsession_id;

    const mquery = db.collection('customers').doc(msgsender).collection('messages').where('session_id', '==', msgsession_id).orderBy('time');

    const messages = collectionData(mquery, 'id').pipe(startWith([]));

</script>

{ msgsender } { msgsession_id }
<ul>
	{#each $messages as msg}
        <li>{ msg.id } { msg.time.toDate().toLocaleTimeString('en-US') } 
        {#if msg.from==="customer"}<b>{/if}
        { msg.message } {msg.from}
        {#if msg.from === "customer"}</b>{/if}
        </li>
	{/each}
</ul>

<hr>
