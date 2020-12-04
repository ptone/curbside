<script>
    import Profile from './Profile.svelte';
    import Customers from './Customers.svelte';
    import Settings from './Settings.svelte';
    import Update from './Update.svelte'

    import { auth, googleProvider, emailProvider } from './firebase';
    import { authState } from 'rxfire/auth';

    let user;
    let email;
    let password;
    let loginError = '';

    const unsubscribe = authState(auth).subscribe(u => user = u);

    function loginGoogle() {
        auth.signInWithPopup(googleProvider);
    }

    function loginEmail() {
        console.log("logging in " + email + password);
        auth.signInWithEmailAndPassword(email, password).then(function(u) {
            console.log("sign in promise resolved");
            console.log(u);
            loginError = '';
        })
        .catch(function(error) {
        // Handle Errors here.
        console.log("Login Error");
        var errorCode = error.code;
        var errorMessage = error.message;
        console.log(errorMessage);
        loginError = `Login Error: ${errorMessage}`;
        // ...
        });
        setTimeout(() => {
            console.log("login done");
            console.log(user);
        }, 2000);
        
    }

    function handleKey(e){
        if(e.keyCode === 13){
            e.preventDefault(); // Ensure it is only this code that rusn
            loginEmail();
        }
    }

</script>


<style>
    section {
        background: rgb(235, 235, 235);
        padding: 20px;
    }
    input { display: block }
    .intro {
        /* width: 960px; */
        /* height: 568px; */
        position: relative;
        /* display:block; 
        width: 100%; */
        /* padding-bottom: 56.25%; */
        padding-top: calc(569 / 960 * 100%);
    }

    iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }

    .loginerror {
        color: red;

    }

</style>

<section>
{#if user}
    <Update />
    <Customers />
    <hr />
    <button on:click={ () => auth.signOut() } class="button">Logout {user.email}</button>
    <!-- <a href="[insert a custom support link if you want here]">
    <button class="button">
    🦟 Feedback and Bug Reports
    </button> </a> -->
    <hr />
    <Settings />
{:else}
	<!-- <button on:click={loginGoogle} class="button">
		Signin with Google
	</button>
    <hr> -->
    <div class="intro">
        <iframe src="https://docs.google.com/presentation/d/e/2PACX-1vRMEaFPfyFg2QjoLPXyQUOqPC4vdJvFM0MXoKYcwoK7Uc579TwFLeLtyIE69dX0meHfz1FqAta5-ZFr/embed?start=true&loop=true&delayms=5000" frameborder="0" width="100%" height="100%" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>
    </div>
    <br />
    <hr />
    <h2>Login</h2>
    Email: <input bind:value={email}>
    Password: <input type="password" bind:value={password} on:keypress={handleKey}>
	<button on:click={loginEmail} class="button" >
		Signin with password
	</button>
    {#if loginError}
      <div class="loginerror">{loginError}</div>
    {/if}
{/if}
</section>