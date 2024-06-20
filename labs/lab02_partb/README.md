# Introduction
This lab is a step-by-step instruction on how to replicates the sample documented here [Open Source PromptFlow GitHub Repository / Examples / Flows / Chat / Chat with PDF](https://github.com/microsoft/promptflow/blob/08cc0d48b0409cd8ab60983d8297a1642c65d972/examples/flows/chat/chat-with-pdf/README.md). See also the [end to end tutorial](https://github.com/microsoft/promptflow/blob/08cc0d48b0409cd8ab60983d8297a1642c65d972/examples/tutorials/e2e-development/chat-with-pdf.md).

    IMPORTANT: The referenced source files were modified to account for a breaking error with a June 16, 2024 numpy release. For more information, see https://github.com/numpy/numpy/releases. Please use the requirements file here rather than those referenced in the above mentioned source files.

# I: Create environment and install dependencies

1. Open VS Code with the Prompt Flow extension enabled.

1. Execute the below in the terminal window to create the environment. 
    ```
    python -m venv venv2b
    ```
1. Execute the below in the terminal window to activate the environment.
    ```
    .\venv2b\Scripts\activate
    ```
1. Ensure that the terminal now shows a `(venv2b)` prefix.

1. Install requirements via the below command.
    ```
    python -m pip install -r ./labs/lab02_partb/requirements.txt
    ```

# II: The GPT Model Connection and Exploration
The GPT model connection named "open_ai_connection", created as part of lab 1, will be used for this lab.

Should you need to edit the connection or perform other explorations...

1. Open the lab02_partb_notebook.ipynb file. Then, from the Command Palette (`Ctrl + Shift + P`), select **Notebook: Select Notebook Kernel**. Select the **venv2b** environment. 

1. IMPORTANT: Ensure the correct environment is displayed in the Kernel on the upper right of the ipynb file window and execute the first cell in the notebook.

1. Run code as needed.

# III: Create a dag chat flow

1. Create a new folder `./labs/lab02_partb/dagflow_chatondata`. Right click the folder name and select **New flow in this directory**. Then, select **Empty flow**.

1. The `flow.dag.yaml` file was created. Open it and click the **Visual Editor** link in the file to open the visual editor.

1. In the upper left side, check **Enable chat mode**.

1. Set **Inputs** values as shown below. In the config object, replace the relevant values (e.g., deployment names) as needed.

    | Name  | Type | Default value | Chat input | Chat history |
    | --- | --- | --- | --- | --- |
    | `chat_history` | list | `[]` | clear | selected |
    | `pdf_url` | string | `https://arxiv.org/pdf/1810.04805.pdf` | clear | clear |
    | `question` | string | `what is BERT?` | selected | clear |
    | `config` | object | `{ EMBEDDING_MODEL_DEPLOYMENT_NAME: text-embedding-ada-002, CHAT_MODEL_DEPLOYMENT_NAME: gpt-4-1106, PROMPT_TOKEN_LIMIT: 3000, MAX_COMPLETION_TOKENS: 1024, VERBOSE: true, CHUNK_SIZE: 1024, CHUNK_OVERLAP: 64}` | clear | clear |

1. Skip the **Outputs** for now; we'll come back to these.

1. In the top left corner of the file, click the **+ Python** button (depending on screen size, this may show as a single **+** button). Enter `setup_env` and select **New file**. Notice that a new file is created using this same name.

1. Open the `setup_env.py` file and replace the contents with the below. 

    ```
    import os
    from typing import Union

    from promptflow.core import tool
    from promptflow.connections import AzureOpenAIConnection, OpenAIConnection

    from chat_with_pdf.utils.lock import acquire_lock

    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/chat_with_pdf/"


    @tool
    def setup_env(connection: Union[AzureOpenAIConnection, OpenAIConnection], config: dict):
        if not connection or not config:
            return

        if isinstance(connection, AzureOpenAIConnection):
            os.environ["OPENAI_API_TYPE"] = "azure"
            os.environ["OPENAI_API_BASE"] = connection.api_base
            os.environ["OPENAI_API_KEY"] = connection.api_key
            os.environ["OPENAI_API_VERSION"] = connection.api_version

        if isinstance(connection, OpenAIConnection):
            os.environ["OPENAI_API_KEY"] = connection.api_key
            if connection.organization is not None:
                os.environ["OPENAI_ORG_ID"] = connection.organization

        for key in config:
            os.environ[key] = str(config[key])

        with acquire_lock(BASE_DIR + "create_folder.lock"):
            if not os.path.exists(BASE_DIR + ".pdfs"):
                os.mkdir(BASE_DIR + ".pdfs")
            if not os.path.exists(BASE_DIR + ".index/.pdfs"):
                os.makedirs(BASE_DIR + ".index/.pdfs")

        return "Ready"
    ```
    Note that this file uses a module that comes with the respository. Take a moment to explore the chat_with_pdf module.

1. Save the file and go back to the `flow.dag.yaml` file. On the setup_env node, update the following attributes: 

    | Name  | Value |
    | --- | --- |
    | `connection` | `open_ai_connection` |
    | `config` | `${inputs.config}` |

1. In the top left corner of the file, click the **+ Python** button (depending on screen size, this may show as a single **+** button). Enter `download_tool` and select **New file**. Notice that a new file is created using this same name.

1. Open the `download_tool.py` file and replace the contents with the below. 

    ```
    from promptflow.core import tool
    from chat_with_pdf.download import download


    @tool
    def download_tool(url: str, env_ready_signal: str) -> str:
        return download(url)
    ```

1. Save the file and go back to the `flow.dag.yaml` file. On the download_tool node, update the following attributes: 

    | Name  | Value |
    | --- | --- |
    | `url` | `${inputs.pdf_url}` |
    | `env_ready_signal` | `${setup_env.output}` |

1. In the top left corner of the file, click the **+ Python** button (depending on screen size, this may show as a single **+** button). Enter `build_index_tool` and select **New file**. Notice that a new file is created using this same name.

1. Open the `build_index_tool.py` file and replace the contents with the below. 

    ```
    from promptflow.core import tool
    from chat_with_pdf.build_index import create_faiss_index


    @tool
    def build_index_tool(pdf_path: str) -> str:
        return create_faiss_index(pdf_path)
    ```

1. Save the file and go back to the `flow.dag.yaml` file. On the build_index_tool node, update the following attributes: 

    | Name  | Value |
    | --- | --- |
    | `pdf_path` | `${download_tool.output}` |

1. In the top left corner of the file, click the **+ Python** button (depending on screen size, this may show as a single **+** button). Enter `rewrite_question_tool` and select **New file**. Notice that a new file is created using this same name.

1. Open the `rewrite_question_tool.py` file and replace the contents with the below. 

    ```
    from promptflow.core import tool
    from chat_with_pdf.rewrite_question import rewrite_question


    @tool
    def rewrite_question_tool(question: str, history: list, env_ready_signal: str):
        return rewrite_question(question, history)
    ```

1. Save the file and go back to the `flow.dag.yaml` file. On the rewrite_question_tool node, update the following attributes: 

    | Name  | Value |
    | --- | --- |
    | `question` | `${inputs.question}` |
    | `history` | `${inputs.chat_history}` |
    | `env_ready_signal` | `${setup_env.output}` |

1. In the top left corner of the file, click the **+ Python** button (depending on screen size, this may show as a single **+** button). Enter `find_context_tool` and select **New file**. Notice that a new file is created using this same name.

1. Open the `find_context_tool.py` file and replace the contents with the below. 

    ```
    from promptflow.core import tool
    from chat_with_pdf.find_context import find_context


    @tool
    def find_context_tool(question: str, index_path: str):
        prompt, context = find_context(question, index_path)

        return {"prompt": prompt, "context": [c.text for c in context]}
    ```

1. Save the file and go back to the `flow.dag.yaml` file. On the find_context_tool node, update the following attributes: 

    | Name  | Value |
    | --- | --- |
    | `question` | `${rewrite_question_tool.output}` |
    | `index_path` | `${build_index_tool.output}` |


1. In the top left corner of the file, click the **+ Python** button (depending on screen size, this may show as a single **+** button). Enter `qna_tool` and select **New file**. Notice that a new file is created using this same name.

1. Open the `qna_tool.py` file and replace the contents with the below. 

    ```
    from promptflow.core import tool
    from chat_with_pdf.qna import qna


    @tool
    def qna_tool(prompt: str, history: list):
        stream = qna(prompt, convert_chat_history_to_chatml_messages(history))

        answer = ""
        for str in stream:
            answer = answer + str + ""

        return {"answer": answer}


    def convert_chat_history_to_chatml_messages(history):
        messages = []
        for item in history:
            messages.append({"role": "user", "content": item["inputs"]["question"]})
            messages.append({"role": "assistant", "content": item["outputs"]["answer"]})

        return messages
    ```

1. Save the file and go back to the `flow.dag.yaml` file. On the qna_tool node, update the following attributes: 

    | Name  | Value |
    | --- | --- |
    | `pronpt` | `${find_context_tool.output.prompt}` |
    | `history` | `${inputs.chat_history}` |

1. In the code editor for the `flow.dag.yaml` file, add the following two lines to the bottom: 

    ```
    environment:
      python_requirements_txt: ../requirements.txt
    ```

1. Set **Outputs** values as shown below. In the config object, replace the relevant values (e.g., deployment names) as needed.

    | Name  | Reference | Chat output |
    | --- | --- | --- |
    | `answer` | `${qna_tool.output.answer}` | selected | 
    | `context` | `${find_context_tool.output.context}` | cleared |

1. Click the double-right arrow Run All icon or press `Shift + f5` to run the flow.

Congradulations! You have created your first end-to-end dag, chat flow from scratch using the Prompt flow for VS Code extension.
