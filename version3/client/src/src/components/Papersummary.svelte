<script>
  export let url, title, summary, related
</script>

<div class="flex flex-col text-gray-400 w-[98%] bg-neutral rounded-2xl my-4 p-4">
  <a href={url} target="_blank" class="font-extrabold text-blue-500 break-words underline underline-offset-2">{title}</a>
  <div class="divider divider-vertical bg-neutral my-2"></div>

  {#if summary}
    <p class="">{summary}</p>
  {:else}
    <p class="">Loading summary...</p>
  {/if}

  <div class="divider divider-vertical bg-neutral my-2"></div>

  {#if summary}
    <div class="flex flex-col sm:flex-row">
      {#each related as similar, i}
        <button class="btn grid mx-2 cursor-ointer flex-grow h-10 card bg-base-300 rounded-box place-items-center" on:click={() => window.open(`https://www.google.com/search?q=${similar}`,'_blank')}>{similar}</button>
        {#if i+1 !== related.length}
          <!-- <div class="divider my-1 dividerp-vertical sm:divider-horizontal sm:mx-1"></div>  -->
        {/if}
      {/each}
    </div>
  {:else}
    <p class="">Loading related...</p>
  {/if}
  
  
</div>
