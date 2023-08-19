<script lang="ts">
  import { getGithubVersion } from '$lib/utils/get-github-version';
  import { onMount } from 'svelte';
  import FullScreenModal from './full-screen-modal.svelte';
  import type { ServerVersionResponseDto } from '@api';
  import Button from '../elements/buttons/button.svelte';

  export let serverVersion: ServerVersionResponseDto;

  let showModal = false;
  let githubVersion: string;
  $: serverVersionName = semverToName(serverVersion);

  function semverToName({ major, minor, patch }: ServerVersionResponseDto) {
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
      class="max-w-lg rounded-3xl border bg-immich-bg px-8 py-10 shadow-sm dark:border-immich-dark-gray dark:bg-immich-dark-gray dark:text-immich-dark-fg"
    >
      <p class="mb-4 text-2xl">🎉 NEW VERSION AVAILABLE 🎉</p>

      <div>
        You are running an community build of
        <span class="font-immich-title font-bold text-immich-primary dark:text-immich-dark-primary">IMMICH</span>,
        packaged in a
        <span class="font-medium underline"
          ><a href="https://snapcraft.io/immich-distribution" target="_blank" rel="noopener noreferrer"
            >snap package</a
          >.</span
        >
        The snap package should update automatically in a few days, you can inspect the progress at
        <span class="font-medium underline"
          ><a href="https://github.com/nsg/immich-distribution/labels/new-version" target="_blank" rel="noopener noreferrer"
            >the issue tracker</a
          >.</span>
        If this breaks compability with the mobile client please provide this information, otherwise relax and give us time. Look at the
        <span class="font-medium underline"
          ><a href="https://github.com/immich-app/immich/releases/latest" target="_blank" rel="noopener noreferrer"
            >release notes</a
          ></span
        >
        for news and information of what the new release contains.
      </div>

      <div class="font-sm mt-8">
        <code>Server Version: {serverVersionName}</code>
        <br />
        <code>Latest Version: {githubVersion}</code>
      </div>

      <div class="mt-8 text-right">
        <Button fullwidth on:click={onAcknowledge}>Acknowledge</Button>
      </div>
    </div>
  </FullScreenModal>
{/if}
