<script>
  import IoIosSearch from "svelte-icons/io/IoIosSearch.svelte";
  import { createEventDispatcher } from 'svelte'
  import { query } from '../stores.js'
  let val

  const dispatch = createEventDispatcher()

  function handlekey(e) {
    if (e.keyCode === 13) {
      dispatch('message',{text: 'Go', val})
    }
  }
</script>


<div
  class="relative flex items-center w-full text-gray-400 focus-within:text-gray-400">
  <input
    autocomplete="off"
    type="text"
    placeholder="Enter Search Term"
    class="input input-bordered bg-neutral w-full py-2 font-semibold placeholder-gray-400 rounded-xl"
    bind:value={$query} on:keydown={handlekey}/>
  <button class="btn ml-4 border-gray-600 hover:border-[#3051bf]" on:click={() => {dispatch('message',{text: 'Go', val})}}>
  <!-- <button class="btn ml-4 hover:border-secondary" on:click={message}> -->
    <span class="w-7">
      <IoIosSearch />
    </span>
  </button>
</div>
