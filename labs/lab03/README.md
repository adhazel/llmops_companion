# Introduction
This lab is a step-by-step instruction on how to replicates the sample documented here [Open Source PromptFlow GitHub Repository / Examples / Flex-Flows / Chat with external functions ](https://github.com/microsoft/promptflow/blob/main/examples/flex-flows/chat-with-functions/README.md). 

This example is derived from an [openai-cookbook example](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_call_functions_with_chat_models.ipynb). 

It highlights functions, the flex flow methodology in a chat scenario with evaluations.

    IMPORTANT: The referenced source files were modified to account for a breaking error with a June 16, 2024 numpy release. For more information, see https://github.com/numpy/numpy/releases. Please use the requirements file here rather than those referenced in the above mentioned source files.

Most of this lab will be accomplished in the provided notebook. 

===================================================
# I: Create environment and install dependencies

1. Open VS Code with the Prompt Flow extension enabled.

1. Execute the below in the terminal window to create the environment. 
    ```
    python -m venv venv3
    ```
1. Execute the below in the terminal window to activate the environment.
    ```
    .\venv3\Scripts\activate
    ```
1. Ensure that the terminal now shows a `(venv3)` prefix.

1. Install requirements via the below command.
    ```
    python -m pip install -r ./labs/lab03/requirements.txt
    ```

# II: Complete steps in the notebook

1. Open the lab03_partb_notebook.ipynb file. Then, from the Command Palette (`Ctrl + Shift + P`), select **Notebook: Select Notebook Kernel**. Select the **venv3** environment. 

1. IMPORTANT: Ensure the correct environment is displayed in the Kernel on the upper right of the ipynb file window and execute the first cell in the notebook.


