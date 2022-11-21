<script>
  import Searchbar from "./components/Searchbar.svelte";
  import Papersummary from "./components/Papersummary.svelte";
  import Article from "./components/Article.svelte";
  import Startpage from "./components/Startpage.svelte";
  import { fade } from "svelte/transition";
  import { pagetexts, query, relaventArticles } from "./stores.js"

  import jURL from './icons/jonathan-sq.png'
  import dURL from './icons/divit-sq.png'
  import sURL from './icons/shivane-sq.png'


  let algoModalOpen = false
  let usModalOpen = false

  let multidoc;
  let multiDocString = ""
  let allDataLoaded = false

  // $: console.log(allDataLoaded)
  let texts

  let summary = undefined;
  let articles
  let startPage = true;

  const controller = new AbortController()


  pagetexts.subscribe(value => {
    // console.log(`store value:`)
    console.log(value)
    texts = value
    if (value) {
      if (value.every(el => el.hasOwnProperty('summary'))) {
        allDataLoaded = true
        // console.log(multiDocString)
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
      if (texts) {
        multiDocString = ""
        multidoc = undefined
        allDataLoaded = false
        texts = undefined
        controller.abort()
      }
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
      signal: controller.signal
    })
    let a = await summary.json()
    if (a.title == "MULTIDOC") {
      multidoc = a.summary
      // console.log(multidoc)
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
    const texts = await fetch(`http://127.0.0.1:5000/info/${query}`, {signal: controller.signal})
    // const texts = await fetch(`http://127.0.0.1:5000/testinfo`)
    let data = await texts.json()
    data.forEach(el => {
      // console.log(el)
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

<div class="modal" class:modal-open={algoModalOpen}>
  <div class="modal-box border border-[#9387fa] w-11/12 max-w-5xl text-gray-400">
    <h3 class="font-bold text-2xl">About The Algorithm</h3>
    <div class="divider my-1"></div>
    <p class="pt-1 py-4">Research-engine.net is powered by 
      <a href="https://en.wikipedia.org/wiki/Web_scraping" target="_blank">web scraping</a>
      and machine learning. When you enter a search query, we find the URLs of the first few relevant results on Google. We also scrape 
      <a href="https://arxiv.org/" target="_blank">ArXiv.org </a>
      and 
      <a href="https://osf.io/preprints/socarxiv" target="_blank">SocArXiv.org</a>
      to find papers on the subject. Then, using Python libraries designed for web scraping, we extract the content of each website and summarize it with 
      <a href="https://en.wikipedia.org/wiki/BERT_(language_model)" target="_blank">BERT</a>
      ,a 
      <a href="https://en.wikipedia.org/wiki/Natural_language_processing" target="_blank">Natural Language Processing</a>
      neural network fine-tuned for text summarization. Using another NLP called 
      <a href="https://github.com/MaartenGr/KeyBERT" target="_blank">KeyBERT</a>
      , we extract the key words and phrases from the text. Finally, we utilize all of the website summaries to create a summary of the topic.</p>
      
      <p>Learn more about NLPs and neural networks:</p>
      <ul>
        <li><a href="https://www.youtube.com/watch?v=aircAruvnKk" target="_blank">What is a neural network?</a></li>
        <li><a href="https://www.youtube.com/watch?v=fOvTtapxa9c" target="_blank">More about Natural Language Processing</a></li>
        <li><a href="https://www.youtube.com/watch?v=xI0HHN5XKDo" target="_blank">More about BERT</a></li>
      </ul>      
    <div class="modal-action mt-3">
      <button class="btn" on:click={() => algoModalOpen = false}>Close</button>
    </div>
  </div>
</div>

<div class="modal" class:modal-open={usModalOpen}>
  <div class="modal-box scrollbar border border-[#9387fa] w-11/12 max-w-5xl text-gray-400">
    <h3 class="font-bold text-2xl">About Us</h3>
    <div class="divider my-1"></div>
    <p>We're a group of high school students in Orange County, CA. We developed research-engine.net with the goal of eliminating the need for searching every webpage to get a basic understanding of a topic.</p>
    <div class="divider my-1"></div>
    <div class="flex flex-col gap-4 sm:flex-row mt-[9px]">
      <div class="flex flex-col items-center w-full sm:w-1/3 rounded-xl bg-neutral">
        <div class="avatar my-3">
          <div class="w-24 rounded-full">
            <img src={jURL} alt="Jonathan DiPinto"/>
          </div>
        </div>
        <div class="divider m-0 mb-1 mx-4"></div>
        <p class="text-lg font-bold">Jonathan DiPinto</p>
        <p class="m-4 text-center">I am an intermediate frontend and backend web developer, and have been coding for fun for the past three years. I am fluent in JavaScript and Python, and I love the ever changing nature of the JavaScript ecosystem.</p>
      </div>
      <div class="flex flex-col items-center w-full sm:w-1/3 rounded-xl bg-neutral">
        <div class="avatar my-3">
          <div class="w-24 rounded-full">
            <img src={dURL} alt="Divit Rawal"/>
          </div>
        </div>
        <div class="divider m-0 mb-1 mx-4"></div>
        <p class="text-lg font-bold">Divit Rawal</p>
        <p class="m-4 text-center">I'm a machine learning hobbyist with a special interest in neural networks and their applications in science. I’m fluent in Python, Java, Flutter, and C++ and love learning more about computer science and it’s applications in my daily life!</p>
      </div>
      <div class="flex flex-col items-center w-full sm:w-1/3 rounded-xl bg-neutral">
        <div class="avatar my-3">
          <div class="w-24 rounded-full">
            <img src={sURL} alt="Shivane Dadi" />
          </div>
        </div>
        <div class="divider m-0 mb-1 mx-4"></div>
        <p class="text-lg font-bold">Shivane Dadi</p>
        <p class="m-4 text-center">I am an independent researcher into intelligent systems specializing in 3d adaptive modeling and natural language processing along with quantum theory. I am well versed in Python, Java, and Swift and hope to broaden my knowledge in computer science in the coming years!</p>
      </div>
    </div>
    <p class="pt-3 break-words">Have feedback? Suggestions? Contact us at <a href="mailto:researchengine.contact@gmail.com" target="_blank">researchengine.contact@gmail.com</a>!</p>
    <p class="break-words">Want to fund? Contact <a href="mailto:researchengine.funding@gmail.com" target="_blank">researchengine.funding@gmail.com</a>. AWS is expensive!</p>
    <div class="modal-action mt-3">
      <button class="btn" on:click={() => usModalOpen = false}>Close</button>
    </div>
  </div>
</div>

<main class="bg-base-100 absolute max-h-screen top-0 bottom-0 left-0 right-0">
  <div class="flex items-center justify-between bg-neutral border border-t-0 border-l-0 border-r-0 border-b-gray-400 h-16 p-2 w-full">
    <span class='w-1/2'>
      <Searchbar val={$query} on:message={handleMessage} />
    </span>
    <span class="flex gap-5 text-gray-400 mx-5">
      <button class="btn modal-button" on:click={() => algoModalOpen = true}>About The Algorithm</button>
      <button class="btn modal-button" on:click={() => usModalOpen = true}>About Us</button>
    </span>
  </div>
  <div class="content flex flex-row w-full p-5">
    <div class="flex flex-col h-full w-1/2">
      {#if multidoc && allDataLoaded}
        <textarea
        class="my-5 bg-neutral scrollbar textarea textarea-bordered h-80 text-gray-400"
        placeholder="Multi doc summary"
        bind:value={multidoc}
        />
      {/if}
      <span class="w-full flex items-center justify-center" />
      <h2 class="font-bold text-3xl flex justify-center text-gray-400">Google Results</h2>
      <div class="divider divider-vertical my-2" />
      {#if !$relaventArticles}
        <p class="font-bold text-xl text-center text-gray-400">
          Enter A Search Term to Begin!
        </p>
      {:else}
        {#if !texts}
          <p class="font-bold text-xl text-center text-gray-400">
            Please allow a few minutes for results to populate
          </p>
        {/if}
      {/if}
      <div class="overflow-auto scrollbar flex-1 relative">
        {#if texts}
          {#await $pagetexts}
            <p>loading</p>
          {:then data}
            {#each data as s}
              <Papersummary
              text={s.text}
              url={s.url}
              title={s.title}
              related={s.keyphrases}
              summary={s.summary} />
            {/each}
          {/await}
        {/if}
      </div>
    </div>
    <hr class="w-2 h-[98%] m-5 bg-neutral border-none rounded-2xl" />
    <div class="flex flex-col h-full overflow-y-auto w-1/2 items-center text-gray-400">
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

  .scrollbar::-webkit-scrollbar-track {
    margin: 15px 0px;
  }

  .content {
    height: calc(100vh - 64px);
  }

  ul li {
    list-style: circle;
    margin-left: 25px;
  }

  .modal a {
    color: lightskyblue;
    text-decoration: underline;
  }

  .modal a:hover {
    color: #9387fa;
  }
</style>
