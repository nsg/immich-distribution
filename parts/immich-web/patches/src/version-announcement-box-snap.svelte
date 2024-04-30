<script lang="ts">
  import { websocketStore } from '$lib/stores/websocket';
  import type { ServerVersionResponseDto } from '@immich/sdk';
  import Button from '../elements/buttons/button.svelte';
  import FullScreenModal from './full-screen-modal.svelte';

  let showModal = false;

  const { release } = websocketStore;

  const semverToName = ({ major, minor, patch }: ServerVersionResponseDto) => `v${major}.${minor}.${patch}`;

  $: releaseVersion = $release && semverToName($release.releaseVersion);
  $: serverVersion = $release && semverToName($release.serverVersion);
  $: $release?.isAvailable && handleRelease();

  const onAcknowledge = () => {
    localStorage.setItem('appVersion', releaseVersion);
    showModal = false;
  };

  const handleRelease = () => {
    try {
      if (localStorage.getItem('appVersion') === releaseVersion) {
        return;
      }

      showModal = true;
    } catch (error) {
      console.error('Error [VersionAnnouncementBox]:', error);
    }
  };
</script>

{#if showModal}
  <FullScreenModal id="new-version-modal" title="🎉 NEW VERSION AVAILABLE" onClose={() => (showModal = false)}>
    <div>

      You are running an community build of IMMICH, packaged in a
      <span class="font-medium underline">
        <a href="https://snapcraft.io/immich-distribution" target="_blank" rel="noopener noreferrer">snap package</a>
      </span>
      The snap package should update automatically in a few days, you can inspect the progress at

      <span class="font-medium underline">
        <a href="https://github.com/nsg/immich-distribution/labels/new-version" target="_blank" rel="noopener noreferrer">the issue tracker</a>.
      </span>

      If this breaks compability with the mobile client please provide this information, otherwise relax and give us time. Look at the
      <span class="font-medium underline">
        <a href="https://github.com/immich-app/immich/releases/latest" target="_blank" rel="noopener noreferrer">release notes</a>
      </span>
      for news and information of what the new release contains.
    </div>

    <div class="font-sm mt-8">
      <code>Server Version: {serverVersion}</code>
      <br />
      <code>Latest Version: {releaseVersion}</code>
    </div>

    <svelte:fragment slot="sticky-bottom">
      <Button fullwidth on:click={onAcknowledge}>Acknowledge</Button>
    </svelte:fragment>
  </FullScreenModal>
{/if}
