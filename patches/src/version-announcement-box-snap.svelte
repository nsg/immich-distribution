<script lang="ts">
	import { getGithubVersion } from '$lib/utils/get-github-version';
	import { onMount } from 'svelte';
	import FullScreenModal from './full-screen-modal.svelte';
	import type { ServerVersionReponseDto } from '@api';

	export let serverVersion: ServerVersionReponseDto;

	let showModal = false;
	let githubVersion: string;
	$: serverVersionName = semverToName(serverVersion);

	function semverToName({ major, minor, patch }: ServerVersionReponseDto) {
		return `v${major}.${minor}.${patch}`;
	}

	function onAcknowledge() {
		// Store server version to prevent the notification
		// from showing again.
		localStorage.setItem('appVersion', githubVersion);
		showModal = false;
	}

	onMount(async () => {
		try {
			githubVersion = await getGithubVersion();
			if (localStorage.getItem('appVersion') === githubVersion) {
				// Updated version has already been acknowledged.
				return;
			}

			if (githubVersion !== serverVersionName) {
				showModal = true;
			}
		} catch (err) {
			// Only log any errors that occur.
			console.error('Error [VersionAnnouncementBox]:', err);
		}
	});
</script>

{#if showModal}
	<FullScreenModal on:clickOutside={() => (showModal = false)}>
		<div
			class="border bg-immich-bg dark:bg-immich-dark-gray dark:border-immich-dark-gray shadow-sm max-w-lg rounded-3xl py-10 px-8 dark:text-immich-dark-fg "
		>
			<p class="text-2xl mb-4">🎉 NEW VERSION AVAILABLE 🎉</p>

			<div>
				You are running an community build of
				<span class="font-immich-title text-immich-primary dark:text-immich-dark-primary font-bold">IMMICH</span>,
				packaged in a
				<span class="underline font-medium">
					<a href="https://snapcraft.io/immich-distribution" target="_blank" rel="noopener noreferrer">snap package</a>.
				</span>
				The snap package should update automatically in a few days, you can inspect the progress at
				<span class="underline font-medium">
					<a href="https://github.com/nsg/immich-distribution/labels/new-version" target="_blank" rel="noopener noreferrer">the issue tracker</a>.
				</span>
				If this breaks compability with the mobile client please provide this information, otherwise relax and give us time.
				
				Look at the
				<span class="underline font-medium">
					<a href="https://github.com/immich-app/immich/releases/latest" target="_blank" rel="noopener noreferrer">release notes</a>
				</span>
				for news and information of what the new release contains.
			</div>

			<div class="font-sm mt-8">
				<code>Server Version: {serverVersionName}</code>
				<br />
				<code>Latest Version: {githubVersion}</code>
			</div>

			<div class="text-right mt-8">
				<button
					class="transition-colors bg-immich-primary dark:bg-immich-dark-primary hover:bg-immich-primary/75 dark:hover:bg-immich-dark-primary/80 dark:text-immich-dark-gray px-6 py-3 text-white rounded-full shadow-md w-full font-medium"
					on:click={onAcknowledge}>Acknowledge</button
				>
			</div>
		</div>
	</FullScreenModal>
{/if}
