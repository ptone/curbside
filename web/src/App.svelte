<script>
	export let name;
	import Login from "./Login.svelte";
	import { statuses } from "./statuses.js";
	import { onMount } from 'svelte';
	// onMount(async () => {
	// });


</script>

<svelte:head>
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.4/css/bulma.min.css" />
	<link href="https://fonts.googleapis.com/icon?family=Material+Icons"
      rel="stylesheet">
</svelte:head>

<style>
	h1 {
	  color: purple;
	}
	main {
	  margin: 20px;
	}
</style>

<main class="content">

	<h1>{name}</h1>

	<Login />

	<a href="https://github.com/ptone/curbside/blob/main/docs/userguide.md">Documentation</a> 

</main>