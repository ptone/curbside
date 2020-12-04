<script>
    import CustomerSession from './CustomerSession.svelte';
    import { db, arrayAdd } from './firebase';
    import { collectionData } from 'rxfire/firestore';
    import { empty } from 'rxjs';
    import { startWith, map } from 'rxjs/operators';
    import { statuses } from "./statuses.js";
    import { onMount, beforeUpdate } from 'svelte';
    import { tenantNumber, tenantNumberVar } from './settings.js'
    import 'firebase/firestore';



    let queryAll;
    let queryActive;
    let customers = empty().pipe(startWith([]));
    let hideClosed = true;




    onMount(async () => {
        // Notification.requestPermission().then(function(result) {
        //     console.log(result);
        // });
        // queryActive = db.collection('sessions').where('session_active', '==', true).orderBy('last_session_start', 'desc');
        // customers = collectionData(queryActive, 'id').pipe(map(buffer => buffer.reverse()), startWith([]));
        console.log(tenantNumberVar);
        queryAll = db.collection('sessions').where('tenant', '==', tenantNumberVar).orderBy('last_session_start', 'desc').limit(25);
        queryActive = db.collection('sessions').where('tenant', '==', tenantNumberVar).where('session_active', '==', true).orderBy('last_session_start', 'desc');
        customers = collectionData(queryActive, 'id').pipe(map(buffer => buffer.reverse()), startWith([]));
    })

    // function notify(event) {
    //     // Leaving in the session component until more feedback about alert saturation
    //     // doing something more sophisticated here would allow latching on any session's alert
    //     // if (Notification.permission == "granted") {
    //     //     overdueNotification = new Notification('Curbside Customer', { body: "Needs attention" });
    //     // }
    //     // TODO consider whether there should be some latching/deboucing on this audio
    //     // alert.play();
    // }

    function toggleHidden() {
        hideClosed = !hideClosed;
        if (hideClosed) {
            customers = collectionData(queryActive, 'id').pipe(map(buffer => buffer.reverse()), startWith([]));
        } else {
            customers = collectionData(queryAll, 'id').pipe(startWith([]));
        }
    }
    
    function updateStatus(event) {
        const { id, status, close, reply, note } = event.detail;
        let update = { 
            status: status, 
            session_active: !close, 
            // only update from customer SMS
            // last_message_time: new Date()
            };
        // only update last replier if there was a reply
        
        console.log(`in updateStatus reply is ${reply}`);
        console.log(`in updateStatus last_updated_by is ${update.last_updated_by}`);

        if (reply != ''){
            update.last_updated_by =  'system';
        }

        update.messages = arrayAdd({
            note: note || '',
            time: new Date(), //update.last_message_time,
            status: status,
            message: reply || '---'
        });
        db.collection('sessions').doc(id).update(update);
    }

    function customStatus(event) {
        const { id, newStatus } = event.detail;
        db.collection('sessions').doc(id).update({ complete: newStatus });
    }

    function removeItem(event) {
        const { id } = event.detail;
        db.collection('sessions').doc(id).delete();
    }


</script>
<h2>
    <span>
        {#if hideClosed}
        Active
        {:else}
        Last 25
        {/if} Customers {#if tenantNumberVar}[for {tenantNumberVar} ]{/if}
    </span>
    <span>
        <button clas="is-button" on:click={toggleHidden}>
        {#if hideClosed}
        🙈
        {:else}
        🐵
        {/if}
        </button>
    </span>
</h2>


<ul>
	{#each $customers as customer}
        <!-- {#if !hideClosed || customer.session_active} -->
        <CustomerSession {...customer} on:update={updateStatus}/>
        <!-- {/if} -->
	{/each}
</ul>




<style>
    span {
        margin-right: 0px;
    }
    h2 {
        display: flex;
        justify-content: space-between;
    }
</style>