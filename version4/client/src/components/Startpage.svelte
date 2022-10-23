<script>
  import Searchbar from "./Searchbar.svelte";
</script>

<div class="absolute w-full h-full flex-col flex z-10 items-center justify-center bg-neutral">
  <span class="flex flex-row items-baseline">
    <h2 class="font-bold text-3xl text-gray-400">
      Research Search Engine
    </h2>
  </span>
  <span class="flex justify-center w-3/4 m-5">
    <Searchbar on:message />
  </span>
</div>
