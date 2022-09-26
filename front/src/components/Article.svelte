<svelte:head>
  <script type="text/x-mathjax-config">
    MathJax.Hub.Config({
      tex2jax: {
        inlineMath: [
          ["$", "$"],
          ["\\(", "\\)"],
        ],
        processEscapes: true,
      },
    });
  </script>

  <script
    type="text/javascript"
    src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
  </script>
</svelte:head>

<script>
  export let paperurl, paperTitle, authors, abstract;

  var urlReg = new RegExp(
    /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/
  );
  let urls = [...new Set(paperurl)];
  urls.forEach((el, i) => {
    if (!urlReg.test(el)) {
      urls = urls.filter((item) => item !== el);
    }
  });
</script>


<div
  class="flex flex-col text-gray-400 w-[98%] bg-neutral rounded-2xl my-4 p-4"
>
  {#each urls as url, i}
    {#if i === 0}
      <a
        href={url}
        target="_blank"
        class="font-extrabold text-blue-500 hover:text-blue-700 underline underline-offset-2"
      >
        {paperTitle}
      </a>
    {:else}
      <a
        href={url}
        target="_blank"
        class="font-light text-blue-500 hover:text-blue-700 underline underline-offset-2"
      >
        Mirror {i}
      </a>
    {/if}
  {/each}
  {#if urls.length === 0}
    <p class="font-extrabold">
      {paperTitle}
    </p>
    <p>No valid URL</p>
  {/if}
  <div class="flex flex-col flex-wrap mt-4 md:flex-row">
    {#each authors as author}
      <a
        class="badge flex text-center cursor-pointer badge-outline hover:badge-outline hover:badge-secondary my-1 h-min md:mr-2"
        href="https://www.google.com/search?q={author}"
        target="_blank"
      >
        {author}
      </a>
    {/each}
  </div>
  <div class="divider divider-vertical bg-neutral my-2" />
  <p>{abstract}</p>
</div>
