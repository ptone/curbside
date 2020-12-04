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

	<a href="https://docs.google.com/document/d/e/2PACX-1vSDlIw4oP8P67rQhtV0reSYk0pbT7dezvmZbet4xX4AwEJjJU_hZSZ-VmR7J6XCF0sqtYEzKMi_8Qo8/pub">Documentation</a> 

</main>