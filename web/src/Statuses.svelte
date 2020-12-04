<script>
    import Status from './Status.svelte';
    import { fade, fly } from 'svelte/transition';

    import { db } from './firebase';
    import { collectionData } from 'rxfire/firestore';
    import { empty } from 'rxjs';
    import { startWith } from 'rxjs/operators';
    import { statuses } from "./statuses.js";
    import { tenantNumberVar } from './settings.js';
    import { onMount } from 'svelte';

    let editingID = '';
    let formVisible = false;
    let statusColor = "#155ccf";
    let statusLabel = "arrived";
    let statusResponse = "Thanks for letting us know you are here, will reply shortly";
    let statusIsFinal = false;
    let statusSendImmediately = false;
    let showSettings = false;

    function setDefault() {
      formVisible = false;
      editingID = '';
      statusColor = "#008e00";
      statusLabel = "reply";
      statusResponse = "We got your message";
      statusIsFinal = false;
      statusSendImmediately = false;
    }

    // const query = db.collection('statuses').orderBy('sequence').orderBy('created');
    let query;
    let statusStream = empty().pipe(startWith([]));
    // const statusStream = collectionData(query, 'id').pipe(startWith([]));

    onMount(async () => {
      query = db.collection('statuses').where('tenant', '==', tenantNumberVar).orderBy('sequence').orderBy('created');
      statusStream = collectionData(query, 'id').pipe(startWith([]));
    })

    function update() {
      console.log('update');
      db.collection('statuses').doc(editingID).update({
              color: statusColor || "#ffffff",
              label: statusLabel, 
              response: statusResponse,
              isFinal: statusIsFinal || false,
              sendImmediately: statusSendImmediately || false
      })
      .then((ref) => {
        console.log(`status ${statusLabel} updated`);
      })
      // TODO catch errors
      editingID = '';
      setDefault();
    }

    function add() {
      if (formVisible) {

      console.log("adding");
      console.log(statusLabel);
      db.collection('statuses').add({ 
        label: statusLabel, 
        response: statusResponse, 
        isFinal: statusIsFinal,
        color: statusColor,
        tenant: tenantNumberVar,
        sendImmediately: statusSendImmediately,
        created: Date.now(), 
        sequence: 999 })
      .then((ref) => {
        console.log(ref.id);
        setDefault();
        console.log(`status ${statusLabel} added`);
      })
      .catch((e) => console.log(e));
      formVisible = false;
      
      } else {
        formVisible = true;
      }
    }

    function updateStatus(event) {
        console.log(event);
        const { id } = event.detail;
        db.collection('statuses').doc(id).get().then(function(doc) {
            if (doc.exists) {
              // console.log("Document data:", doc.data());
              const dat = doc.data();
              statusColor = dat.color;
              statusLabel = dat.label;
              statusResponse = dat.response;
              statusIsFinal = dat.isFinal || false;
              statusSendImmediately = dat.sendImmediately || false;
              editingID = id;
              formVisible = true;
                
            } else {
                // doc.data() will be undefined in this case
                console.log("No such document!");
            }
        }).catch(function(error) {
            console.log("Error getting document:", error);
        });
        formVisible = false;
    }

    function removeItem(event) {
        const { id } = event.detail;
        console.log(id);
        db.collection('statuses').doc(id).delete().then(() => {
          console.log(`status ${statusLabel} deleted`);
        });
    }

</script>

<style>
    ul {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        grid-gap: 10px;
        list-style-type: none;
        margin: 0;
        padding: 0;
    }

</style>


<h4>Statuses</h4>
{#if $statuses}
<ul>
	{#each $statusStream as status}
	<!-- {#each $statuses as status} -->
        <Status {...status} on:remove={removeItem} on:edit={updateStatus} />
        <!-- <li> {status.label} {status.response}</li> -->
	{/each}
</ul>
{:else}
No Statuses, add some
{/if}


{#if formVisible}

{#if editingID}
<h5>Edit Status</h5>
{:else}
<h5>Add Status</h5>
{/if}

Label: <input bind:value={statusLabel} /><br/>
Response: <input bind:value={statusResponse} size=80 /><br/>
Color: <input type="color" bind:value={statusColor} /><br/>
<input type="checkbox" bind:checked={statusIsFinal} /> Closes Session
&nbsp;&nbsp;  <input type="checkbox" bind:checked={statusSendImmediately} /> Update Immediately (unable to edit reply)<br />
{/if}

{#if editingID}
<button class="button is-info" on:click={update}>Update Status</button>
<button class="button is-info" on:click={setDefault} >Cancel</button>
{:else}
<button class="button is-info" on:click={add}>Add Status</button> {#if formVisible}<button class="button is-info" on:click={setDefault} >Cancel</button>{/if}
{/if}



<hr>
