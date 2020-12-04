<script>
import Statuses from './Statuses.svelte';
import { onMount, beforeUpdate } from 'svelte';
import { fade, fly } from 'svelte/transition';
import { userSettings, tenantSettings, storeUserSettings, storetenantSettings } from './settings.js'
let havePermission;
let userSettingsLocal = {testChecked: false};
let tenantSettingsLocal;


onMount(() => {
  if (Notification.permission == "granted") {
    havePermission = true;
  }

  const uSub = userSettings.subscribe(value => {
    if (Object.entries(value).length > 0) {
      console.log("update user settings");
      console.log(value);
      userSettingsLocal = value;
    } else {
      console.log("user defaults");
      userSettingsLocal = {
        testChecked: false,
        alertOnArrive: '',
        notifyOnArrive: false, 
        alertOnReply: '',
        notifyOnReply: false,
        alertOnOverdue: '',
        notifyOnOverdue: false,
        overdueDeadline: 120
      }
    }
  })
  const sSub = tenantSettings.subscribe(value => {
    if (value != {}) {
      console.log("update system settings");
      tenantSettingsLocal = value;
    } else {
      tenantSettingsLocal = {
        dndEnabled: false,
        dndMessage: ''
      }
    }
  })
});


function saveUser() {
  setTimeout(() => {
    storeUserSettings(userSettingsLocal); 
  }, 200);
}

function saveSystem() {
  setTimeout(() => {
    storetenantSettings(tenantSettingsLocal);
  }, 200);
}

function toggleSettings(e) {
  showSettings = !showSettings;
}

    function checkNotificationPromise() {
    try {
      Notification.requestPermission().then();
    } catch(e) {
      return false;
    }

    return true;
  }

    function askNotificationPermission() {
        // function to actually ask the permissions
        function handlePermission(permission) {
            // Whatever the user answers, we make sure Chrome stores the information
            if(!('permission' in Notification)) {
            Notification.permission = permission;
            }

            // set the button to shown or hidden, depending on what the user answers
            if(Notification.permission === 'denied' || Notification.permission === 'default') {
              havePermission = false;
            } else {
              havePermission = true;
            }
        }

        // Let's check if the browser supports notifications
        if (!('Notification' in window)) {
            console.log("This browser does not support notifications.");
        } else {
            if(checkNotificationPromise()) {
            Notification.requestPermission()
            .then((permission) => {
                handlePermission(permission);
            })
            } else {
            Notification.requestPermission(function(permission) {
                handlePermission(permission);
            });
            }
        }
    }


let showSettings = false;

</script>

<style>

.pseudobutton {
  cursor:pointer;
}

</style>

<span on:click={toggleSettings} class="material-icons pseudobutton">
settings
</span>


{#if showSettings }
<h3>Settings</h3>
<label>Note: all settings saved automatically on edit</label>
<div transition:fly="{{ y: 900, duration: 500 }}">


<h4>User Options</h4>
<hr />
<b>On Arrival</b><br />



<i>Sound:</i><br />
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnArrive} value='' on:click={saveUser} />
	None
</label>
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnArrive} value='doorbell' on:click={saveUser} />
	Doorbell
</label>
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnArrive} value='bell' on:click={saveUser} />
	Ding
</label>
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnArrive} value='alert' on:click={saveUser} />
	Attention announcement
</label>
<br />

{#if havePermission}
  <label>
  <input type=checkbox bind:checked={userSettingsLocal.notifyOnArrive} on:click={saveUser} /> System notification <br />
  </label>
{:else}
  <div style="color: darkgrey;">
  <i>You must enable notifications before you can change this setting.</i>
  <label>
  <input type=checkbox disabled=true /> System notification <br />
  </label>
  </div>
  <button id="enable" on:click={askNotificationPermission} >Enable notifications</button>
{/if}
<hr />

<b>On Reply</b><br />

<i>Sound:</i><br />
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnReply} value='' on:click={saveUser} />
	None
</label>
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnReply} value='doorbell' on:click={saveUser} />
	Doorbell
</label>
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnReply} value='bell' on:click={saveUser} />
	Ding
</label>
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnReply} value='alert' on:click={saveUser} />
	Attention announcement
</label>
<br />
{#if havePermission}
  <label>
  <input type=checkbox bind:checked={userSettingsLocal.notifyOnReply} on:click={saveUser} /> System notification <br />
  </label>
{:else}
  <div style="color: darkgrey;">
  <i>You must enable notifications before you can change this setting.</i>
  <label>
  <input type=checkbox disabled=true /> System notification <br />
  </label>
  </div>
  <button id="enable" on:click={askNotificationPermission} >Enable notifications</button>
{/if}
<hr />

<b>Overdue settings</b>
<label>
Deadline (in seconds) <input bind:value={userSettingsLocal.overdueDeadline} size=10 on:blur={saveUser} /><br />
<i>After this many seconds, an customer conversation will be considered overdue and display a note with count-up timer.</i>
</label>
<br />

<i>Sound:</i><br />
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnOverdue} value='' on:click={saveUser} />
	None
</label>
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnOverdue} value='doorbell' on:click={saveUser} />
	Doorbell
</label>
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnOverdue} value='bell' on:click={saveUser} />
	Ding
</label>
<label>
	<input type=radio bind:group={userSettingsLocal.alertOnOverdue} value='alert' on:click={saveUser} />
	Attention announcement
</label>
<br />
{#if havePermission}
  <label>
    <input type=checkbox bind:checked={userSettingsLocal.notifyOnOverdue} on:click={saveUser} /> System notification <br />
    <i>System notification on arrival</i>
  </label>
{:else}
  <div style="color: darkgrey;">
  <i>You must enable notifications before you can change this setting.</i>
  <label>
  <input type=checkbox disabled=true /> System notification <br />
  </label>
  </div>
  <button id="enable" on:click={askNotificationPermission} >Enable notifications</button>
{/if}
<hr />

<h4>System Options (all users of a number)</h4>
DND (Do Not Disturb)
<label>
	<input type=radio bind:group={tenantSettingsLocal.dndEnabled} value={true} on:click={saveSystem} />
	On
	<input type=radio bind:group={tenantSettingsLocal.dndEnabled} value={false} on:click={saveSystem} />
	Off
</label>
<i>
an automatic reply will be sent, and no new sessions will be opened (for after hours) <br />
</i>
<label>
DND Message <input bind:value={tenantSettingsLocal.dndMessage} size=60  on:blur={saveSystem} /><br />
</label>
<hr />

<Statuses />
</div>
{/if}