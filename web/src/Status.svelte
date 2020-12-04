<script>
    import { fade, fly } from 'svelte/transition';

    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();
    
    function remove() {
      console.log("dispatch remove");
      console.log(id); 
      dispatch('remove', { id });
	}

  function editStatus() {
    dispatch('edit', {
      id
    });
  }
	function toggleStatus() {
    let newStatus = !complete;
		dispatch('toggle', {
            id,
            newStatus
        });
    }
    
    export let id; // document ID
    export let label;
    export let color;
    export let isFinal;
    export let response;
    // export let sequence; 
    // export let created;
    export let sendImmediately;
</script>

<style>
    .is-complete {
        text-decoration: line-through;
        color: green;
    }


    li {
        /* display: flex; */
        font-size: 1.1em;
        font-weight: normal;
        /* justify-content: space-between; */
        border-bottom: 1px solid black;
        list-style-type: none;
    }

    span {
        margin-right: auto;
    }

    .status-info {
        width: 300px;
        text-align: left;
    }

    /* span .is-button {
        margin-right: auto;
    } */
</style>


<li out:fade>
    <span>
        <button class="is-button" on:click={editStatus}> ✏️ </button>
        <button class="is-button" on:click={remove}> ❌ </button>
    </span>
    <span class="status-info" style="color: {color};">
        { label }
    </span>
</li>
<li out:fade>
    <span class="status-info">
        <i>{ response }</i> 
    </span>
</li>
<li out:fade>
    <span>
         <input type="checkbox" bind:checked={isFinal} onclick="return false;"/> Closes Session<br />
         <input type="checkbox" bind:checked={sendImmediately} onclick="return false;"/> Update Immediately<br />
    </span>


</li>