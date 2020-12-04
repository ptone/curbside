<script>
    import { fade, fly } from 'svelte/transition';

    import { createEventDispatcher } from 'svelte';
    import { statuses, getStatusColor, getStatusResponse, statusByLabel } from "./statuses.js";
    import { userSettings } from './settings.js';
    import { onMount, beforeUpdate, afterUpdate } from 'svelte';
    import { sendSMS, getCNAM } from './api.js';


    // TODO ideally this timer could be shared for all on this page - prob via store?
    function msToTime(duration) {
        var milliseconds = parseInt((duration % 1000) / 100),
        seconds = Math.floor((duration / 1000) % 60),
        minutes = Math.floor((duration / (1000 * 60)) % 60),
        hours = Math.floor((duration / (1000 * 60 * 60)) % 24);

        hours = (hours < 10) ? "0" + hours : hours;
        minutes = (minutes < 10) ? "0" + minutes : minutes;
        seconds = (seconds < 10) ? "0" + seconds : seconds;

        return + minutes + ":" + seconds;
    }
    let time = new Date();
    let overdue = false;
    let elapsed;
    let elapsedDisplay;
    let systemNotification;
    let notificationLatch = false;
    let msgCt = 0;

    const alerts = {
        alert: new Audio("https://storage.googleapis.com/curbside-contact-static/alert.mp3"),
        bell: new Audio("https://storage.googleapis.com/curbside-contact-static/bell.wav"),
        doorbell: new Audio("https://storage.googleapis.com/curbside-contact-static/doorbell.wav"),
    }

    function notify() {
        if (Notification.permission == "granted") {
            systemNotification = new Notification('Curbside Customer', { body: "Needs attention" });
            return true;
        }
        return false;
    }

    onMount(() => {
        console.log('session mount statuses');
        console.log(statuses);

        msgCt = messages.length;
        if (status == 'arrived') {
            if ($userSettings.alertOnArrive) {
                alerts[$userSettings.alertOnArrive].play()
            }
            
            if ($userSettings.notifyOnArrive){
                notify();
            }
        }
        console.log(caller_id);
        if (caller_id != "None") {
            console.log("getting caller ID");
            getCNAM(id, sender).then((cid) => {
                // the actual caller_id should be updated in the session doc and propate down
                console.log(cid);
            });
        }

        // TODO make a setting
		const interval = setInterval(() => {
            if (!session_active) {
                return
            }
            // for now disable overdue for anything other than arrived
            // if (!(status == 'arrived')){
            //     return true;
            // }
            // console.log(last_updated_by);
            // console.log($userSettings.overdueDeadline);
            if (last_updated_by != 'customer') {
                overdue = false;
                if (!overdue && notificationLatch) {
                    notificationLatch = false;
                    if (systemNotification) {
                        systemNotification.close();
                    }
                }
                return true;
            }
            time = new Date();
            elapsed = time - last_message_time.toDate();
            let deadlineMS = $userSettings.overdueDeadline * 1000;
            if (elapsed > deadlineMS) {
                overdue = true;
                elapsedDisplay = msToTime(elapsed - deadlineMS);

            } else {
                overdue = false;
            }
            if (overdue && !notificationLatch) {
                
                if ($userSettings.alertOnOverdue) {
                    alerts[$userSettings.alertOnOverdue].play()
                }
                
                if ($userSettings.notifyOnOverdue){
                    notify();
                }
                notificationLatch = true;
            } else {
                if (!overdue && notificationLatch) {
                    notificationLatch = false;
                    if (systemNotification) {
                        systemNotification.close();
                    }
                }
            }
		}, 1000);

		return () => {
			clearInterval(interval);
		};
    });


    beforeUpdate(() => {
        color = getStatusColor(status);
        // console.log(`before update status: ${status}`);
    })
    afterUpdate(() => {
        // console.log(`after update status: ${status}`);
        // console.log(`msg ct: ${msgCt}`);
        let msgLen = messages.length;
        // console.log(`msg len: ${msgLen}`);
        if (status == 'reply' && msgLen > msgCt) {
            const msgOfInterestIndex = msgLen-(msgLen-msgCt);
            // console.log(`msg of interest index: ${msgOfInterestIndex}`);
            const msgOfInterest = messages[msgOfInterestIndex];
            // console.log(`msg of interest : ${msgOfInterest}`);
            if (msgOfInterest.from == 'customer' ) {
                if ($userSettings.alertOnReply) {
                    alerts[$userSettings.alertOnReply].play()
                }
                
                if ($userSettings.notifyOnReply){
                    notify();
                }
            }
        } 

        msgCt = msgLen;

    })

    function snoozeOverdue() {
        last_updated_by = 'system';
        // Note - the last_message_time would not be persisted
        // last_message_time = new Date();
        
    }
    

    const dispatch = createEventDispatcher();
    
	function updateStatus(newStatus, close, reply, note) {
        let e = {
            id: id,
            status: newStatus,
            close: close,
            reply: reply,
            note: note
        };
        if (!(replyMsg || note)) {
            e.note = '';
        }
        console.log("dispatching update");
        dispatch('update', e);
    }

    function endSession() {
		dispatch('update', {
            id: id,
            status: "ended",
            close: true,
            reply: '',
            note: "closed"
        });
    }

    function setMessage(e) {
        replyMsg = getStatusResponse(chosenStatus);
        if (statusByLabel[chosenStatus].sendImmediately) {
            console.log("sendReply from setMessage");
            sendReply();
        } else {
            hideReply = false;
        }
    }

    async function sendReply() {
        if (replyMsg != '') {
            let reply = {msg: replyMsg, recipient: sender, session:session_id, note:note};
            await sendSMS(reply);
            updateStatus(chosenStatus, statusByLabel[chosenStatus].isFinal, replyMsg, note);
        } else {
            updateStatus(chosenStatus, statusByLabel[chosenStatus].isFinal, replyMsg, note);
        }
        note = '';
        replyMsg = '';
        hideReply = true;
        // statusselect.value = 'blank';
        // document.getElementById('statusselect').value = 'blank';
        // let foo = this.getElementsByName('status');
        // console.log(foo);
        // foo.options[0].selected = true;
        statusSelect.options[0].selected = true;
        // s.options[i-1].selected = true;
    }

    function handleKey(e){
        if(e.keyCode === 13){
            e.preventDefault(); // Ensure it is only this code that rusn
            sendReply();
        }
    }

    
    export let id; // document ID
    export let sender;
    // export let first_message;
    // export let last_message;
    export let messages;
    // export let color;
    let color = '#ff3e00';

    export let status;
    export let session_id;
    export let session_active;
    export let last_message_time;
    export let last_updated_by;
    export let caller_id;
    let chosenStatus;
    let replyMsg;
    let note;
    let statusSelect;
    let hideReply = true;
</script>

<style>
    .is-complete {
        text-decoration: line-through;
        color: green;
    }

    li {
        display: flex;
        font-size: 1.2em;
        font-weight: bold;
        border-bottom: 1px;
        border-color: black;
        background-color: white;
        margin-bottom: 5px;
        padding: 5px;
    }

    .session {
        border-bottom: 1px;
        border-color: black;
    }

    .messages>li {
        font-size: .8em;
        font-weight: normal;
        padding: 2px;

    }

    span {
        margin-right: auto;
    }

	.status {
		color: var(--theme-status-color);
	}

    .response-form {
        font-size: .9em;
        font-weight: normal;

    }
</style>


<li class="session" in:fly="{{ x: 900, duration: 500 }}" out:fade>

    <span>
        <h2>
            { sender.replace(/[^0-9 ]/g, "").replace(/^1/g, "") }
        </h2>
        {#if caller_id != "None"}<h4>[ {caller_id } ]</h4>{/if}
        <div>
            <h2 style="color: {color}">{ status }</h2>
            {#if overdue }
                    <h1 style="color: red;">
                        <button on:click={snoozeOverdue} >😴</button> Overdue: {elapsedDisplay}!
                    </h1>
            {/if}
        </div>
    </span>
    <span>
    <ul class="messages">
	{#each messages as msg}
        <li in:fly="{{ x: 900, duration: 500 }}">

        { msg.time.toDate().toLocaleTimeString('en-US') }
        <div>
        &nbsp;<i>={msg.status}=</i>
        
        </div>
        {#if msg.from=="customer"}
        &nbsp;<div style="color: #155ccf;"><b>{ msg.message }</b></div>
        {:else}
        &nbsp;<div>{ msg.message }</div>
        {/if}
        {#if msg.note}
        &nbsp;[{msg.note}]
        {/if}
        </li>
	{/each}
    </ul>
    internal note <input bind:value={note} size=10 on:keypress={handleKey} /> 
    <select name="status" id="statusselect" bind:value={chosenStatus} on:change={setMessage} bind:this={statusSelect}>
        <option value="blank">--Please choose an option--</option>
        {#each $statuses as status}
        <option value={ status.label}>{status.label}</option>
        {/each}
    </select>
    <br />
    <div class="response-form" hidden={hideReply}>
        reply: <input bind:value={replyMsg} size=40 on:keypress={handleKey}/>
        <button class="is-button" on:click={sendReply}> ↩️ Send</button>
    </div>
    </span>
	<button class="is-button" on:click={endSession}>
		✅
	</button>

</li>