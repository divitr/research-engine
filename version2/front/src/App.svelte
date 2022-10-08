<script>
  import Skeleton from "svelte-skeleton/Skeleton.svelte";
  import Searchbar from "./components/Searchbar.svelte";
  import Papersummary from "./components/Papersummary.svelte";
  import Article from "./components/Article.svelte";
  import Startpage from "./components/Startpage.svelte";
  import Loading from "./components/Loading.svelte";
  import { fade } from "svelte/transition";
  import { pagetexts,query } from "./stores.js"
  import { onDestroy } from "svelte";

  let multidoc;
  let multiDocString = ""
  let allDataLoaded = false

  $: console.log(allDataLoaded)
  let texts

  let summary = undefined;
  let articles
  let startPage = true;


  pagetexts.subscribe(value => {
    console.log(`store value:`)
    console.log(value)
    texts = value
    if (value) {
      if (value.every(el => el.hasOwnProperty('summary'))) {
        allDataLoaded = true
        console.log(multiDocString)
        getSummary({"url": "", "title": "MULTIDOC", "text": multiDocString})
      }
    }
  })

  relaventArticles.subscribe(val => {articles = val})
  
  // every time a new summary loads in, push it into the summaries list

  async function handleMessage(event) {
    if (event.detail.text == "Go") {
      // resets the articles and summaries for a new search term
      articles = undefined;
      summary = undefined;
      startPage = false;
      relaventArticles.set(await getArticles($query))
      getInfo($query)
    }
  }
  
  async function getSummary(data) {
    const summary = await fetch("http://127.0.0.1:5000/summarize", {
    // const summary = await fetch("http://127.0.0.1:5000/testsummary", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
    let a = await summary.json()
    if (a.title == "MULTIDOC") {
      multidoc = a.summary
      console.log(multidoc)
    } else {
      multiDocString += ` ${a.summary}`
      pagetexts.update(val => {
          val.forEach((el, i) => {
            if (el.title === a.title) {
              val[i] = {...val[i], ...a}
            }
          })
          return val
      })
    }
  }

  async function getArticles(query) {
    if (!query) return;
    let hits = [];
    const relaventPapers = await fetch(
      "https://share.osf.io/api/v2/search/creativeworks/_search",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: {
            bool: {
              must: {
                query_string: {
                  query: query,
                },
              },
              filter: [
                {
                  bool: {
                    should: [
                      {
                        terms: {
                          types: ["preprint"],
                        },
                      },
                      {
                        terms: {
                          sources: ["Thesis Commons"],
                        },
                      },
                    ],
                  },
                },
                {
                  terms: {
                    sources: [
                      "Research Papers in Economics",
                      "Preprints.org",
                      "bioRxiv",
                      "OSF",
                      "arXiv",
                      "PsyArXiv",
                      "SocArXiv",
                    ],
                  },
                },
                {
                  terms: {
                    sources: [
                      "OSF",
                      "AfricArXiv",
                      "AgriXiv",
                      "Arabixiv",
                      "BioHackrXiv",
                      "BodoArXiv",
                      "EarthArXiv",
                      "EcoEvoRxiv",
                      "ECSarXiv",
                      "EdArXiv",
                      "engrXiv",
                      "FocUS Archive",
                      "Frenxiv",
                      "INA-Rxiv",
                      "IndiaRxiv",
                      "LawArXiv",
                      "LIS Scholarship Archive",
                      "MarXiv",
                      "MediArXiv",
                      "MetaArXiv",
                      "MindRxiv",
                      "NutriXiv",
                      "PaleorXiv",
                      "PsyArXiv",
                      "Research AZ",
                      "SocArXiv",
                      "SportRxiv",
                      "Thesis Commons",
                      "arXiv",
                      "bioRxiv",
                      "Preprints.org",
                      "PeerJ",
                      "Cogprints",
                      "Research Papers in Economics",
                    ],
                  },
                },
              ],
            },
          },
          from: 0,
          aggregations: {
            sources: {
              terms: {
                field: "sources",
                size: 500,
              },
            },
          },
        }),
      }
    );
    const data = await relaventPapers.json();
    data.hits.hits.forEach((el, i) => {
      let info = {
        title: el["_source"]["title"],
        date: el["_source"]["date"],
        authors: el["_source"]["contributors"],
        abstract: el["_source"]["description"],
        urls: el["_source"]["identifiers"],
        tags: el["_source"]["tags"],
      };
      hits.push(info);
    });
    return hits;
  }

  async function getInfo(query) {
    const texts = await fetch(`http://127.0.0.1:5000/info/${query}`)
    // const texts = await fetch(`http://127.0.0.1:5000/testinfo`)
    let data = await texts.json()
    data.forEach(el => {
      console.log(el)
      getSummary(el)
    })
    pagetexts.update(old => data)
    getSummary({"url": "", "title": "MULTIDOC", "text": multiDocString})
  }
</script>

{#if startPage}
  <div transition:fade={{ duration: 200 }}>
    <Startpage on:message={handleMessage} />
  </div>
{/if}
<main
  class="flex p-5 flex-row bg-base-100 h-screen w-screen items-center justify-center"
>
  <div class="flex flex-col h-full w-1/2">
    <Searchbar val={$query} on:message={handleMessage} />
    {#if multidoc && allDataLoaded}
      <textarea
        class="my-5 bg-neutral scrollbar textarea textarea-bordered h-80 text-gray-400"
        placeholder="Multi doc summary"
        bind:value={multidoc}
      />
    {/if}
    <span class="w-full flex items-center justify-center" />
    <div class="overflow-auto scrollbar flex-1 relative">
      {#if texts}
        {#await $pagetexts}
          <p>loading</p>
        {:then data}
          {#each data as s}
            <Papersummary
              url={s.url}
              title={s.title}
              related={s.keyphrases}
              summary={s.summary}
            />
          {/each}
        {/await}
      {/if}
    </div>
  </div>
  <hr class="w-2 h-full m-5 bg-neutral border-none rounded-2xl" />
  <div class="flex flex-col h-full w-1/2 items-center text-gray-400">
    <h2 class="font-bold text-3xl">Relevant Papers</h2>
    <div class="divider divider-vertical my-2" />
    <div class="overflow-y-auto w-full scrollbar relative">
      {#if !$relaventArticles}
        <p class="font-bold text-xl text-center">
          Enter A Search Term to Begin!
        </p>
      {:else}
        {#if $relaventArticles.length}
          {#each $relaventArticles as hit}
            <Article
              paperurl={hit.urls}
              paperTitle={hit.title}
              authors={hit.authors}
              abstract={hit.abstract}
            />
          {/each}
        {:else}
          <p>No Results for "{$query}"</p>
        {/if}
      {/if}
    </div>
  </div>
</main>

<style lang="postcss" global>
  @tailwind base;
  @tailwind components;
  @tailwind utilities;

  .scrollbar::-webkit-scrollbar {
    width: 5px;
    height: 5px;
    margin-left: 5px;
  }

  .scrollbar::-webkit-scrollbar-thumb {
    border-radius: 100vh;
    border: 3px solid #a8a8a8;
  }
</style>
