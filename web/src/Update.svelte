<script>
    import { db } from './firebase';
    import { doc } from 'rxfire/firestore';
    import { onMount, beforeUpdate } from 'svelte';

    let loadTime = Date.now();
    let refreshNow = false;

    onMount(async () => {
      doc(db.collection('settings').doc('system')).subscribe(snapshot => {
        const sysSettings = snapshot.data();
        const releaseDate = sysSettings.release_stable.toDate();
        // TODO make channel specific
        if (releaseDate > loadTime) {
          console.log("app update available");
          refreshNow = true;
        }
      });
    })

    function refresh() {
      window.location.reload();
    }
</script>

{#if refreshNow}
  <button on:click={refresh} class="button is-warning is-light">An updated version is available, click to refresh</button>
{/if}
