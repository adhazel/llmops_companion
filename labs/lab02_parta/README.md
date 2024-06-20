# Introduction
This lab is a step-by-step instruction on how to replicates the sample documented here [Open Source PromptFlow GitHub Repository / Examples / Flows / Standard / Web Classification Example](https://github.com/microsoft/promptflow/blob/main/examples/flows/standard/web-classification/README.md).

# I: Create environment and install dependencies

1. Open VS Code with the Prompt Flow extension enabled.

1. Execute the below in the terminal window to create the environment. 
    ```
    python -m venv venv2a
    ```
1. Execute the below in the terminal window to activate the environment.
    ```
    .\venv2a\Scripts\activate
    ```
1. Ensure that the terminal now shows a `(venv2a)` prefix.
1. Install requirements via the below command.
    ```
    python -m pip install -r ./labs/lab02_parta/requirements.txt
    ```

# II: Create the GPT Model Connection

1. Open the lab02_parta_notebook.ipynb file. Then, from the Command Palette (`Ctrl + Shift + P`), select **Notebook: Select Notebook Kernel**. Select the **venv2a** environment. 

1. Ensure the correct environment is displayed in the Kernel on the upper right of the ipynb file window and execute the first cell in the notebook.

1. Complete the instructions and run the cells in the **Create GPT Model Connection** section.

# III: Create a .env file

Rename the included `.env.sample` file located in this directory to `.env` and replace all placeholder text with your own values.

# III: Create a dag standard flow

1. Create a new folder `./labs/lab02_parta/dagflow_classification`. Right click the folder name and select **New flow in this directory**. Then, select **Empty flow**.

1. The `flow.dag.yaml` file was created. Open it and click the **Visual Editor** link in the file to open the visual editor.

1. Click the **+ Add input** button and add a parameter called `url` with the default value of `https://www.microsoft.com/en-us/store/collections/xboxseriessconsoles?icid=CNav_Xbox_Series_S`.

1. Add 2 outputs. The **Reference** values will be set at a later time. Name the outputs `category` and `evidence`.

1. With the flow.dag.yaml file open, in the **PromptFlow** extension sidebar, under **Tools**, hover over **Python** and click the **+** button. When prompted, enter `fetch_text_content_from_url` and select **New File**.

1. A Python node will appear with the message `Generating tool metadata` under the title. Wait until this changes to a link to a python file with the name matching the tool name. Then, click the link to open the python file.

1. Paste the below code into the `fetch_text_content_from_url.py` file. 
    ```
    from promptflow.core import tool
    import requests
    import bs4


    @tool
    def fetch_text_content_from_url(url: str):
        # Send a request to the URL
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # Parse the HTML content using BeautifulSoup
                soup = bs4.BeautifulSoup(response.text, 'html.parser')
                soup.prettify()
                return soup.get_text()[:2000]
            else:
                msg = f"Get url failed with status code {response.status_code}.\nURL: {url}\nResponse: " \
                    f"{response.text[:100]}"
                print(msg)
                return "No available content"
        except Exception as e:
            print("Get url failed with error: {}".format(e))
            return "No available content"
    ```
    Note the @tool decorator before the function definition. In general, the use of a decorator such as @tool in Python is a way to modify or extend the behavior of functions or methods. Decorators are a powerful feature that allow you to wrap another function in order to extend its behavior without permanently modifying it.This decorator is part of the PromptFlow library's API and is used to register functions with the library and to apply specific behaviors to these functions.

1. Save the `fetch_text_content_from_url.py` file. Open the `flow.dag.yaml` file and note that the fetch_text_content_from_url node now shows `url` as the input **Name**. Click in the **Value** field and select the `$(inputs.url)` value that appears.

1. In the top left corner of the file, click the **+ LLM** button (depending on screen size, this may show as a single **+** button). Enter `summarize_text_content` and select **New file**. Notice that a new file is created using this same name.

1. Open the `summarize_text_content.jinja2` file and replace the contents with the below.

    Learn more about Jinja at [Jinja GitHub Repository](https://jinja.palletsprojects.com/en/3.1.x/), [Jinja Documentation](https://jinja.palletsprojects.com/en/3.1.x/), and the Jinja references on [Microsoft Learn: Prompt tool for flows in Azure AI Studio](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/prompt-flow-tools/prompt-tool).

    ```
    system:
    Please summarize the following text in one paragraph. 100 words.
    Do not add any information that is not in the text.

    user:
    Text: {{text}}
    Summary: 
    ```

1. Set node values as shown below.
    | Attribute  | Value |
    | --- | --- |
    | connection | `open_ai_connection` |
    | api | **chat** |
    | deployment_name | [Your Azure OpenAI GPT* Model Deployment Name] |
    | temperature | `0.2` |
    | max_tokens | `128` |
    | response_format | **{"type":"text"}** |
    | inputs > text | **${fetch_text_content_from_url.output}** |

1. In the top left corner of the file, click the **+ Python** button (depending on screen size, this may show as a single **+** button). Enter `prepare_examples` and select **New file**. Notice that a new file is created using this same name.

1. Open the `prepare_examples.py` file and replace the contents with the below.
    ```
    from promptflow.core import tool

    @tool
    def prepare_examples():
        return [
            {
                "url": "https://play.google.com/store/apps/details?id=com.spotify.music",
                "text_content": "Spotify is a free music and podcast streaming app with millions of songs, albums, and "
                                "original podcasts. It also offers audiobooks, so users can enjoy thousands of stories. "
                                "It has a variety of features such as creating and sharing music playlists, discovering "
                                "new music, and listening to popular and exclusive podcasts. It also has a Premium "
                                "subscription option which allows users to download and listen offline, and access "
                                "ad-free music. It is available on all devices and has a variety of genres and artists "
                                "to choose from.",
                "category": "App",
                "evidence": "Both"
            },
            {
                "url": "https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw",
                "text_content": "NFL Sunday Ticket is a service offered by Google LLC that allows users to watch NFL "
                                "games on YouTube. It is available in 2023 and is subject to the terms and privacy policy "
                                "of Google LLC. It is also subject to YouTube's terms of use and any applicable laws.",
                "category": "Channel",
                "evidence": "URL"
            },
            {
                "url": "https://arxiv.org/abs/2303.04671",
                "text_content": "Visual ChatGPT is a system that enables users to interact with ChatGPT by sending and "
                                "receiving not only languages but also images, providing complex visual questions or "
                                "visual editing instructions, and providing feedback and asking for corrected results. "
                                "It incorporates different Visual Foundation Models and is publicly available. Experiments "
                                "show that Visual ChatGPT opens the door to investigating the visual roles of ChatGPT with "
                                "the help of Visual Foundation Models.",
                "category": "Academic",
                "evidence": "Text content"
            },
            {
                "url": "https://ab.politiaromana.ro/",
                "text_content": "There is no content available for this text.",
                "category": "None",
                "evidence": "Both"
            }
        ]
    ```

1. In the top left corner of the file, click the **+ LLM** button (depending on screen size, this may show as a single **+** button). Enter `classify_with_llm` and select **New file**. Notice that a new file is created using this same name.

1. Open the `classify_with_llm.jinja2` file and replace the contents with the below.

    ```
    system:
    Your task is to classify a given url into one of the following categories:
    Movie, App, Academic, Channel, Profile, PDF or None based on the text content information.
    The classification will be based on the url, the webpage text content summary, or both.

    user:
    The selection range of the value of "category" must be within "Movie", "App", "Academic", "Channel", "Profile", "PDF" and "None".
    The selection range of the value of "evidence" must be within "Url", "Text content", and "Both".
    Here are a few examples:
    {% for ex in examples %}
    URL: {{ex.url}}
    Text content: {{ex.text_content}}
    OUTPUT:
    {"category": "{{ex.category}}", "evidence": "{{ex.evidence}}"}

    {% endfor %}

    For a given URL and text content, classify the url to complete the category and indicate evidence:
    URL: {{url}}
    Text content: {{text_content}}.
    OUTPUT:
    ```

1. Set node values as shown below.
    | Attribute  | Value |
    | --- | --- |
    | connection | `open_ai_connection` |
    | api | **chat** |
    | deployment_name | [Your Azure OpenAI GPT* Model Deployment Name] |
    | temperature | `0.2` |
    | max_tokens | `128` |
    | response_format | **{"type":"text"}** |
    | inputs > url | `${inputs.url}` |
    | inputs > examples | `${prepare_examples.output}` |
    | inputs > text_content | `summarize_text_content.output` |

1. In the top left corner of the file, click the **+ Python** button (depending on screen size, this may show as a single **+** button). Enter `convert_to_dict` and select **New file**. Notice that a new file is created using this same name.

1. Open the `convert_to_dict.py` file and replace the contents with the below.

    ```
    from promptflow.core import tool
    import json


    @tool
    def convert_to_dict(input_str: str):
        try:
            return json.loads(input_str)
        except Exception as e:
            print("input is not valid, error: {}".format(e))
            return {
                "category": "None",
                "evidence": "None"
            }

    ```

1. Set the input value for **input_str** to `${classify_with_llm.output}`.

1. Click the double-right arrow **Run All** icon or press `Shift + f5` to run the flow. Note that an error appears in the Terminal window. This is expected as we haven't yet set the Output values we created earlier. Scroll up in the flow and enter the below values in Outputs.

    | Name  | Reference |
    | --- | --- |
    | category | `${convert_to_dict.output.category}` |
    | evidence | `${convert_to_dict.output.evidence}` |

1. Click the double-right arrow **Run All** icon or press `Shift + f5` to run the flow.

1. Alternatively, you could have ran the following to test: 

    ```
    # --- Cell 1
    %bash
    cd ./labs/lab02_parta/dagflow_classification
    # --- Cell 2
    %bash #note that you can replace 'python' below with the full python.exe path from your virtual environment
    python -m promptflow._cli._pf.entry flow test --flow ./labs/lab02_parta/dagflow_classification --user-agent "myname"

    ```

Congradulations! You have created your first end-to-end flow from scratch using the Prompt flow for VS Code extension.

# IV: Test flow
1. Open the lab02_parta_notebook.ipynb file. Then, from the Command Palette (`Ctrl + Shift + P`), select **Notebook: Select Notebook Kernel**. Select the **venv2a** environment. 

1. Ensure the correct environment is displayed in the Kernel on the upper right of the ipynb file window and execute the first cell in the notebook.

1. Complete the instructions and run the cells in the **Testing the flow** section.

# V: Wrapping Up

1. Save any files.

1. Close the notebook file.

1. Execute the below in the terminal window to deactivate the environment.
    ```
    deactivate
    ```
