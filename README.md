# DevCommit

A command-line AI tool for autocommits.

## Features

- Automatic commit generation using AI.
- Easy integration with your Git workflow.
- Customizable options for commit messages.

![DevCommit Demo](https://i.imgur.com/erPaZjc.png)

## Installation

1. **Install DevCommit**  
   Run the following command to install DevCommit:

   ```bash
   pip install devcommit
   ```

2. **Add the `.dcommit` Configuration File**  
   DevCommit uses a configuration file (`.dcommit`) to customize commit settings. Follow these steps to create it:

   - **Option 1: Home Directory**  
     To set up DevCommit globally, create the `.dcommit` file in your home directory:

     ```bash
     echo -e "LOCALE = en\nMAX_NO = 1\nCOMMIT_TYPE = conventional\nMODEL_NAME = gemini-1.5-flash" > ~/.dcommit
     ```

   - **Option 2: Virtual Environment**  
     Alternatively, you can create the `.dcommit` file in your virtual environment’s `config` directory for environment-specific settings:

     ```bash
     mkdir -p $VIRTUAL_ENV/config
     echo -e "LOCALE = en\nMAX_NO = 1\nCOMMIT_TYPE = conventional\nMODEL_NAME = gemini-1.5-flash" > $VIRTUAL_ENV/config/.dcommit
     ```

## Usage

After installation, you can start using DevCommit directly in your terminal:

```bash
devcommit
```
