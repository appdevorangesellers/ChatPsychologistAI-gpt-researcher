<div align="center" id="top">

####

[![Website](https://img.shields.io/badge/Official%20Website-platform.sh-teal?style=for-the-badge&logo=world&logoColor=white&color=0891b2)](https://main-bvxea6i-bkwpxl2cinmus.eu.platformsh.site/docs)

</div>

# 🔎 Custom GPT Researcher

Custom GPT Researcher is an autonomous agent designed for comprehensive web and local research on PSYCHOLOGY

## Demo
https://main-bvxea6i-bkwpxl2cinmus.eu.platformsh.site/docs

## Architecture


## Tutorials
 - [How it Works](https://docs.gptr.dev/blog/building-gpt-researcher)
 - [How to Install](https://www.loom.com/share/04ebffb6ed2a4520a27c3e3addcdde20?sid=da1848e8-b1f1-42d1-93c3-5b0b9c3b24ea)
 - [Live Demo](https://www.loom.com/share/6a3385db4e8747a1913dd85a7834846f?sid=a740fd5b-2aa3-457e-8fb7-86976f59f9b8)

## Features

- 📝 Generate research reports using web and local documents.
- 📜 Generate reports exceeding 1000 words.
- 🌐 Aggregate over 20 sources for objective conclusions.
- 📂 Maintains memory and context throughout research.
- 📄 Export reports to .md format.

## 📖 Documentation

See the [Documentation](https://docs.gptr.dev/docs/gpt-researcher/getting-started/getting-started) for:
- Installation and setup guides

## ⚙️ Getting Started

### Installation

1. Install Python 3.11 or later. [Guide](https://www.tutorialsteacher.com/python/install-python).
2. Clone the project and navigate to the directory:

    ```bash
    git clone https://github.com/maihoangbichtram/custom-gpt-researcher.git gpt-researcher
    cd gpt-researcher
    ```

3. Set up API keys by exporting them or storing them in a `.env` file.

    ```bash
    Copy .env.example to .env
    ```

4. Activate the virtual environment

    ```bash
    poetry shell
    ```
4. Install dependencies and start the server:

    ```bash
    poetry lock && poetry install
    python -m uvicorn main:app --reload
    ```

Visit [http://localhost:8000](http://localhost:8000) to start.

For other setups (e.g., Poetry or virtual environments), check the [Getting Started page](https://docs.gptr.dev/docs/gpt-researcher/getting-started/getting-started).


## 📄 Add Local Documents to research

You can instruct the GPT Researcher to run research tasks based on your local documents. Currently supported file formats are: plain text(.txt).

Step 1: Add the env variable `DOC_PATH` pointing to the folder where your documents are located.

```bash
export DOC_PATH="./rag/input"
```


<p align="right">
  <a href="#top">⬆️ Back to Top</a>
</p>
