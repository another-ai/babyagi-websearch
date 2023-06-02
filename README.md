# BabyAGI-🦙... runs 100% local as well

This is a side branch of BabyAGI with some enhancements... 🚀

************************************************************

## 🔍 Smart internet search extension
Toplist Google search, subsequent web page scraping and finally LLM powered scrape result summarization (reading of lengthy scrape result in chunks).
  - Works with Google CSE, SERPAPI and browser search
  - Fallback mechanism in case of API rate limit or missing API key (CSE -> SERPAPI -> browser search). Works also w/o any API key with browser search.
  - Adding of a second web page scrape function for retrieval of a more compact and clean extract (used for document embedding, see below)
  - The LLM does reason on its own when internet search is required and in this case verbalizes the task as a concise search request

The scrape result summary LLM has its own model & settings, separate from task process LLM. See .env file for details.

![image](https://github.com/robiwan303/babyagi/blob/main/BabyAGI-SmartSearch.jpeg)

## 👀 Initial internet search & web page scraping
Optional feature to perform a toplist search (with auto-generated search requests, derived from the objective) and subsequent web page scraping at startup. The scrape results with strict filtering for 'clean" content, w/o incomprehensible information as strings of keywords or letter, then get embedded in document vector store (see next chapter), before the task procedure is started.

This shall provide BabyAGI with a preconfigured "memory" with related content and shall help to minimize the need for smart search, since it involves token intensive and time consuming LLM powered scrape result summarization. The manual operation using supplementary scripts scraper.py and ingest.py is automated with this feature (see next chapter).

## 🧠 Document embedding extension
Integration of document embedding and Q&A retrieval functionality from: https://github.com/imartinez/privateGPT.git.
Many thanks to https://github.com/imartinez for the great work!
  - The main functionality from script privateGPT.py has been integrated in BabyAGI
  - The embedded documents are accessed with Q&A retrieval and the answer is added as context for the next task
  - The determination of the optimal search query for the Q&A retrieval is LLM powered, based on the task, context and the objective

Adding of stand-alone scripts as supplementary tools for BabyAGI:
  - scraper.py: Google toplist search and scraping of web pages related to the objective (using a slightly modified version of smart internet search). The results can be added to the document vector store before the task procedure is started with script ingest.py
  - ingest.py: Document loader, documents in subfolder "source_documents" are loaded and embedded in a document embedding vector store (from privateGPT repo with minor changes)
  - qa-retrieval.py: Q&A retrieval with document embedding vector store, useful for evaluation purposes (slightly modified version of privateGPT.py)

All stand-alone scripts use BabyAGI parameters from .env file, see the document embedding extension and the description in comments.
The document embedding LLM has its own model & settings, separate from task process LLM. See .env file for details.

![image](https://github.com/robiwan303/babyagi/blob/main/BabyAGI-DocEmbedding.jpeg)

Important: The document embedding vector store has to be created and filled with at least one entry, before the document embedding feature is enabled!

## 📚 Long-term memory: Automatic appending of web scrape content to document embedding vector store
The intention behind this functionality is to enhance BabyAGI's a long-term memory and compensate for the context limit. Therefore extended result data gets stored, which can be quite large.
Beside the LLM powered web scrape result summary, the raw web page scrape content is stored and embedded in vector store.
The content extraction for the raw scrape data is more strict than the one for result summary creation because the extract must be "clean", hence no incomprehensible data as strings of keywords or characters is included.

The feature can be disabled by a parameter in .env, switching the vector store to "read-only".

Since the raw web scrape can be ten-thousands of characters long, adding it as enriched result to storage did not work (token limit error). So I decided to include this information in the document embedding store. The results storage is enriched by smart search summary and document embedding results, if available.

With enabled document embedding extension the updated vector store then provides context for the next task by Q&A retrieval.

![image](https://github.com/robiwan303/babyagi/blob/main/BabyAGI-Memory.jpeg)

Beside the update of embedding vector store above, the extended result data is written to file, serving as backup. The data is stored in folder "scrape_documents". When the vector store is deleted, the "memory" still exists in this file. The file can be used for embedding again using stand-alone script ingest.py (see document embedding extension).

## 🦙 Full Llama support: 100% local operation possible
By implementing a strategie for applying different context limits to e.g. document embedding, task context or various inputs for the task creation and prioritization agents, and changing the Llama setup a bit, it is possible to have BabyAGI run quite stable with a 7B-Llama.

It is slower as with OpenAI models, but reasonable (on my MacBook M1 with 16GB RAM).
Even more interesting it gets in combination with smart internet search, document embedding and update of vector store with web scrape content...

![image](https://github.com/robiwan303/babyagi/blob/main/BabyAGI-Llama%20Operation.jpeg)

Running continuously with a 7B-Llama,... creating & processing the task list, analysing web scrape results, doing Q&A retrieval with embedded document store, all in parallel and w/o getting stuck in loops or aborting prematurely. 😋

## 🧫 Report creation extension (experimental)

With this extension enabled, the task results and smart search results are getting analyzed for a marker. The marker and what shall be done is defined in a supplementary instruction for the objective, called "ACTION". The functionality is pretty basic up to now, but important results are properly marked, identified and added to the report file. Works also with code!

This feature, when finished, shall create a report, summary or code as output to a file, involving parsing, loading and update of the report file.

************************************************************

## 📖 Tipps, hints & observations for Llama operation
See below some things I did notice during my many hours of testing & tinkering:
  - It can happen that BabyAGI stops after the first cycle due to empty task prioritization list, simply re-start in this case
  - I did observe sporadic error messages regarding token limit for document embedding with a large vector store (several thousand pages). Also here a re-start solves the problem in most cases.
  - The parameter LLAMA_CTX_MAX should be set to 2048, with LLAMA_CONTEXT set to 8000 (value in chars, not tokens).
    - According to what I could find out Llamas should support a context size of 2048 in general, but I am not sure if this is correct. Works at least with wizardLM-7B and vicuna-7B.
    - Reducing LLAMA_CTX_MAX to 1024 makes the task procedure faster, but responses are getting badly truncated
    - Even with LLAMA_CTX_MAX set to 2048 and LLAMA_CONTEXT set to 8000, responses are getting truncated sometimes. But the overall task planning & prioritization process stays on track.
  - The Q&A retrieval with document embedding vector store works best with EMBEDDINGS_CTX_MAX set to 1024. Value of 2048 makes the Q&A retrieval very slow.
  - The same applies for the smart search summary. Set the parameter SUMMARY_CTX_MAX to 1024 and SUMMARY_CONTEXT to 1000 (default is 3000 with OpenAI).
  - The smart search result summary can get lengthy, depending on the scrape size (SCRAPE_LENGTH) and number of top result web pages to be scraped. Therefore I did limit the top result pages to 1 (default is 3 with OpenAI) in code and SCRAPE_LENGTH to 3000 (default is 5000 with OpenAI).
  - The models and configuration for each LLM (task process, smart search and document embedding) can be setup independently, making it possible to use different Llama's for each funtion
  - The fine-tuning parameters for smart context limitation are all setup in .env file, for easy experimation. The pre-defined setup works well with 7B-Llama.

## 🗿 Experience and motivation
The overall speed is a bit slow with a 7B-Llama, but it works. The task processing speed is not so bad at all, what takes time is the summarization of web scrape results, due to the amount of chunks. The smart internet search and document embedding are great improvements in general and help the 7B-Llama not to get stuck. Most important parameter is the context limit (LLAMA_CONTEXT) and token limit (MAX_TOKENS) in .env file.

The document embedding functionality from privateGPT is awesome. Document loading is super quick. The Q&A retrieval with 7B-Llama is a bit slow but acceptable. With the extension enabled and enough related data embedded, the task process with 7B-Llama works very stable. Anyhow, try for yourself...

You might ask the question: "Why use a Llama when OpenAI and its excellent models are available?"

I did tinker a lot with agents like BabyAGI or AutoGPT and its derivates, using mostly gpt-3.5-turbo and rarely gpt-4. But anyhow, with new functions and concepts like smart internet search, involving summarization in chunks by LLM, or document embedding with Q&A retrieval my API rate went ballistic. And that's where I started looking for alternatives. Of course GPT is more powerful and has bigger context length, but using Llamas 100% locally has its own merits.

I am sure I did miss to add some of the new required packages in requirements.txt. Please be advised that you will need to install some libraries manually using "pip install".

## 🐱‍💻 Planned upgrades
  - Enhancement of report creation extension for full report parsing/changing
  - Support of GPT4All models for task procedure and smart search LLM's
  - Algorithm for automatic evaluation of optimal smart context limits for all types of context
  - ...

************************************************************

## 🦙 Llama models
You can find precompiled .bin files of popular Llamas for example in this repo: https://github.com/nomic-ai/gpt4all/tree/main/gpt4all-chat
- https://gpt4all.io/models/ggml-wizardLM-7B.q4_2.bin (md5sum 99e6d129745a3f1fb1121abed747b05a) An non-commercially licensable model based on Llama 7b and trained by Microsoft and Peking University.
- https://gpt4all.io/models/ggml-vicuna-7b-1.1-q4_2.bin (md5sum 29119f8fa11712704c6b22ac5ab792ea) An non-commercially licensable model based on Llama 7b and trained by teams from UC Berkeley, CMU, Stanford, MBZUAI, and UC San Diego.

The models wizardLM-7B and vicuna-7B do work best for me on MacBook M1 with 16GB RAM. Unfortunately I am not able to persuade a 13B model to run with a reasonable token rate. Runs at something like 1 token per minute.

Some popular models like mpt-7B (chat, instruct and storyteller) or the new Guanaco-7B are not working. I think a newer version of Llama-Cpp is required, still need to have a look into this.

********************
... from here onwards the original readme from main branch.
********************

# Translations:

[<img title="عربي" alt="عربي" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/sa.svg" width="30">](docs/README-ar.md)
[<img title="Français" alt="Français" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/fr.svg" width="30">](docs/README-fr.md)
[<img title="Polski" alt="Polski" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/pl.svg" width="30">](docs/README-pl.md)
[<img title="Portuguese" alt="Portuguese" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/br.svg" width="30">](docs/README-pt-br.md)
[<img title="Romanian" alt="Romanian" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/ro.svg" width="30">](docs/README-ro.md)
[<img title="Russian" alt="Russian" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/ru.svg" width="30">](docs/README-ru.md)
[<img title="Slovenian" alt="Slovenian" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/si.svg" width="30">](docs/README-si.md)
[<img title="Spanish" alt="Spanish" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/es.svg" width="30">](docs/README-es.md)
[<img title="Turkish" alt="Turkish" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/tr.svg" width="30">](docs/README-tr.md)
[<img title="Ukrainian" alt="Ukrainian" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/ua.svg" width="30">](docs/README-ua.md)
[<img title="简体中文" alt="Simplified Chinese" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/cn.svg" width="30">](docs/README-cn.md)
[<img title="繁體中文 (Traditional Chinese)" alt="繁體中文 (Traditional Chinese)" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/tw.svg" width="30">](docs/README-zh-tw.md)
[<img title="日本語" alt="日本語" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/jp.svg" width="30">](docs/README-ja.md)
[<img title="한국어" alt="한국어" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/kr.svg" width="30">](docs/README-ko.md)
[<img title="Magyar" alt="Magyar" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/hu.svg" width="30">](docs/README-hu.md)
[<img title="فارسی" alt="فارسی" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/ir.svg" width="30">](docs/README-fa.md)
[<img title="German" alt="German" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/de.svg" width="30">](docs/README-de.md)
[<img title="Indian" alt="Indian" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/in.svg" width="30">](docs/README-in.md)


# Objective

This Python script is an example of an AI-powered task management system. The system uses OpenAI and vector databases such as Chroma or Weaviate to create, prioritize, and execute tasks. The main idea behind this system is that it creates tasks based on the result of previous tasks and a predefined objective. The script then uses OpenAI's natural language processing (NLP) capabilities to create new tasks based on the objective, and Chroma/Weaviate to store and retrieve task results for context. This is a pared-down version of the original [Task-Driven Autonomous Agent](https://twitter.com/yoheinakajima/status/1640934493489070080?s=20) (Mar 28, 2023).

This README will cover the following:

- [How the script works](#how-it-works)

- [How to use the script](#how-to-use)

- [Supported Models](#supported-models)

- [Warning about running the script continuously](#continous-script-warning)

# How It Works<a name="how-it-works"></a>

The script works by running an infinite loop that does the following steps:

1. Pulls the first task from the task list.
2. Sends the task to the execution agent, which uses OpenAI's API to complete the task based on the context.
3. Enriches the result and stores it in [Chroma](https://docs.trychroma.com)/[Weaviate](https://weaviate.io/).
4. Creates new tasks and reprioritizes the task list based on the objective and the result of the previous task.
   </br>

![image](https://user-images.githubusercontent.com/21254008/235015461-543a897f-70cc-4b63-941a-2ae3c9172b11.png)

The `execution_agent()` function is where the OpenAI API is used. It takes two parameters: the objective and the task. It then sends a prompt to OpenAI's API, which returns the result of the task. The prompt consists of a description of the AI system's task, the objective, and the task itself. The result is then returned as a string.

The `task_creation_agent()` function is where OpenAI's API is used to create new tasks based on the objective and the result of the previous task. The function takes four parameters: the objective, the result of the previous task, the task description, and the current task list. It then sends a prompt to OpenAI's API, which returns a list of new tasks as strings. The function then returns the new tasks as a list of dictionaries, where each dictionary contains the name of the task.

The `prioritization_agent()` function is where OpenAI's API is used to reprioritize the task list. The function takes one parameter, the ID of the current task. It sends a prompt to OpenAI's API, which returns the reprioritized task list as a numbered list.

Finally, the script uses Chroma/Weaviate to store and retrieve task results for context. The script creates a Chroma/Weaviate collection based on the table name specified in the TABLE_NAME variable. Chroma/Weaviate is then used to store the results of the task in the collection, along with the task name and any additional metadata.

# How to Use<a name="how-to-use"></a>

To use the script, you will need to follow these steps:

1. Clone the repository via `git clone https://github.com/yoheinakajima/babyagi.git` and `cd` into the cloned repository.
2. Install the required packages: `pip install -r requirements.txt`
3. Copy the .env.example file to .env: `cp .env.example .env`. This is where you will set the following variables.
4. Set your OpenAI API key in the OPENAI_API_KEY and OPENAPI_API_MODEL variables. In order to use with Weaviate you will also need to setup additional variables detailed [here](docs/weaviate.md).
5. Set the name of the table where the task results will be stored in the TABLE_NAME variable.
6. (Optional) Set the name of the BabyAGI instance in the BABY_NAME variable.
7. (Optional) Set the objective of the task management system in the OBJECTIVE variable.
8. (Optional) Set the first task of the system in the INITIAL_TASK variable.
9. Run the script: `python babyagi.py`

All optional values above can also be specified on the command line.

# Running inside a docker container

As a prerequisite, you will need docker and docker-compose installed. Docker desktop is the simplest option https://www.docker.com/products/docker-desktop/

To run the system inside a docker container, setup your .env file as per steps above and then run the following:

```
docker-compose up
```

# Supported Models<a name="supported-models"></a>

This script works with all OpenAI models, as well as Llama and its variations through Llama.cpp. Default model is **gpt-3.5-turbo**. To use a different model, specify it through LLM_MODEL or use the command line.

## Llama

Llama integration requires llama-cpp package. You will also need the Llama model weights. 

- **Under no circumstances share IPFS, magnet links, or any other links to model downloads anywhere in this repository, including in issues, discussions or pull requests. They will be immediately deleted.**

Once you have them, set LLAMA_MODEL_PATH to the path of the specific model to use. For convenience, you can link `models` in BabyAGI repo to the folder where you have the Llama model weights. Then run the script with `LLM_MODEL=llama` or `-l` argument.

# Warning<a name="continous-script-warning"></a>

This script is designed to be run continuously as part of a task management system. Running this script continuously can result in high API usage, so please use it responsibly. Additionally, the script requires the OpenAI API to be set up correctly, so make sure you have set up the API before running the script.

# Contribution

Needless to say, BabyAGI is still in its infancy and thus we are still determining its direction and the steps to get there. Currently, a key design goal for BabyAGI is to be _simple_ such that it's easy to understand and build upon. To maintain this simplicity, we kindly request that you adhere to the following guidelines when submitting PRs:

- Focus on small, modular modifications rather than extensive refactoring.
- When introducing new features, provide a detailed description of the specific use case you are addressing.

A note from @yoheinakajima (Apr 5th, 2023):

> I know there are a growing number of PRs, appreciate your patience - as I am both new to GitHub/OpenSource, and did not plan my time availability accordingly this week. Re:direction, I've been torn on keeping it simple vs expanding - currently leaning towards keeping a core Baby AGI simple, and using this as a platform to support and promote different approaches to expanding this (eg. BabyAGIxLangchain as one direction). I believe there are various opinionated approaches that are worth exploring, and I see value in having a central place to compare and discuss. More updates coming shortly.

I am new to GitHub and open source, so please be patient as I learn to manage this project properly. I run a VC firm by day, so I will generally be checking PRs and issues at night after I get my kids down - which may not be every night. Open to the idea of bringing in support, will be updating this section soon (expectations, visions, etc). Talking to lots of people and learning - hang tight for updates!

# BabyAGI Activity Report

To help the BabyAGI community stay informed about the project's progress, Blueprint AI has developed a Github activity summarizer for BabyAGI. This concise report displays a summary of all contributions to the BabyAGI repository over the past 7 days (continuously updated), making it easy for you to keep track of the latest developments.

To view the BabyAGI 7-day activity report, go here: [https://app.blueprint.ai/github/yoheinakajima/babyagi](https://app.blueprint.ai/github/yoheinakajima/babyagi)

[<img width="293" alt="image" src="https://user-images.githubusercontent.com/334530/235789974-f49d3cbe-f4df-4c3d-89e9-bfb60eea6308.png">](https://app.blueprint.ai/github/yoheinakajima/babyagi)


# Inspired projects

In the short time since it was release, BabyAGI inspired many projects. You can see them all [here](docs/inspired-projects.md).

# Backstory

BabyAGI is a pared-down version of the original [Task-Driven Autonomous Agent](https://twitter.com/yoheinakajima/status/1640934493489070080?s=20) (Mar 28, 2023) shared on Twitter. This version is down to 140 lines: 13 comments, 22 blanks, and 105 code. The name of the repo came up in the reaction to the original autonomous agent - the author does not mean to imply that this is AGI.

Made with love by [@yoheinakajima](https://twitter.com/yoheinakajima), who happens to be a VC (would love to see what you're building!)
