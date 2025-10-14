# DevCommit

A command-line AI tool for autocommits.

## Features

- Automatic commit generation using AI.
- Easy integration with your Git workflow.
- Customizable options for commit messages.
- Support for directory-based commits - create separate commits for each root directory.
- Interactive mode to choose between global or directory-based commits.

![DevCommit Demo](https://i.imgur.com/erPaZjc.png)

## Installation

1. **Install DevCommit**  
   Run the following command to install DevCommit:

   ```bash
   pip install devcommit
   ```

2. **Set Up Configuration (Required: API Key)**  
   DevCommit requires a Google Gemini API key. You can configure it using **any** of these methods:

   **Priority Order:** `.dcommit` file → Environment Variables → Defaults

   ### Option 1: Environment Variables (Quickest)
   ```bash
   export GEMINI_API_KEY='your-api-key-here'
   
   # Optional: Add to ~/.bashrc or ~/.zshrc for persistence
   echo "export GEMINI_API_KEY='your-api-key-here'" >> ~/.bashrc
   ```

   ### Option 2: .dcommit File (Home Directory)
   ```bash
   cat > ~/.dcommit << 'EOF'
   GEMINI_API_KEY = your-api-key-here
   LOCALE = en
   MAX_NO = 1
   COMMIT_TYPE = conventional
   MODEL_NAME = gemini-1.5-flash
   COMMIT_MODE = auto
   EOF
   ```

   ### Option 3: .dcommit File (Virtual Environment)
   ```bash
   mkdir -p $VIRTUAL_ENV/config
   cat > $VIRTUAL_ENV/config/.dcommit << 'EOF'
   GEMINI_API_KEY = your-api-key-here
   LOCALE = en
   MAX_NO = 1
   COMMIT_TYPE = conventional
   MODEL_NAME = gemini-1.5-flash
   COMMIT_MODE = auto
   EOF
   ```

   **Get your API key:** https://aistudio.google.com/app/apikey

## Usage

After installation, you can start using DevCommit directly in your terminal:

```bash
devcommit
```

### Basic Usage

- **Stage all changes and commit:**
  ```bash
  devcommit --stageAll
  ```

- **Commit staged changes:**
  ```bash
  devcommit
  ```

### Directory-Based Commits

DevCommit supports generating separate commits per root directory, which is useful when you have changes across multiple directories.

#### Configuration Options

You can set your preferred commit mode in the `.dcommit` configuration file using the `COMMIT_MODE` variable:

- **`COMMIT_MODE = auto`** (default): Automatically prompts when multiple directories are detected
- **`COMMIT_MODE = directory`**: Always use directory-based commits for multiple directories
- **`COMMIT_MODE = global`**: Always create one commit for all changes

**Priority order:** CLI flag (`--directory`) → Config file (`COMMIT_MODE`) → Interactive prompt (if `auto`)

#### Command-Line Usage

- **Interactive mode (auto):** When you have changes in multiple directories, DevCommit will automatically ask if you want to:
  - Create one commit for all changes (global commit)
  - Create separate commits per directory

- **Force directory-based commits:**
  ```bash
  devcommit --directory
  # or
  devcommit -d
  ```

When using directory-based commits, you can:
1. Select which directories to commit (use Space to select, Enter to confirm)
2. For each selected directory, review and choose a commit message
3. Each directory gets its own commit with AI-generated messages based on its changes

### Additional Options

- `--excludeFiles` or `-e`: Exclude specific files from the diff
- `--generate` or `-g`: Specify number of commit messages to generate
- `--commitType` or `-t`: Specify the type of commit (e.g., conventional)
- `--stageAll` or `-s`: Stage all changes before committing
- `--directory` or `-d`: Force directory-based commits

### Examples

```bash
# Stage all and commit with directory-based option
devcommit --stageAll --directory

# Commit with specific commit type
devcommit --commitType conventional

# Exclude lock files
devcommit --excludeFiles package-lock.json yarn.lock
```

## Configuration Reference

All configuration can be set via **environment variables** or **`.dcommit` file**:

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `GEMINI_API_KEY` | Your Google Gemini API key **(required)** | - | Your API key |
| `LOCALE` | Language for commit messages | `en-US` | Any locale code (e.g., `en`, `es`, `fr`) |
| `MAX_NO` | Number of commit message suggestions | `1` | Any positive integer |
| `COMMIT_TYPE` | Style of commit messages | `general` | `general`, `conventional`, etc. |
| `MODEL_NAME` | Gemini model to use | `gemini-1.5-flash` | Any Gemini model name |
| `COMMIT_MODE` | Default commit strategy | `auto` | `auto`, `directory`, `global` |
| `EXCLUDE_FILES` | Files to exclude from diff | `package-lock.json, pnpm-lock.yaml, yarn.lock, *.lock` | Comma-separated file patterns |

### Configuration Priority
1. **`.dcommit` file** (highest priority)
2. **Environment variables**
3. **Built-in defaults** (lowest priority)

### Using Environment Variables
```bash
export GEMINI_API_KEY='your-api-key-here'
export COMMIT_MODE='directory'
export COMMIT_TYPE='conventional'
export MAX_NO=3
export EXCLUDE_FILES='*.lock,dist/*,build/*'

# Or add to ~/.bashrc for persistence
```

### Using .dcommit File
```
GEMINI_API_KEY = your-api-key-here
LOCALE = en
MAX_NO = 3
COMMIT_TYPE = conventional
MODEL_NAME = gemini-1.5-flash
COMMIT_MODE = directory
EXCLUDE_FILES = *.lock, dist/*, build/*, node_modules/*
```

**Note:** The `.dcommit` file is **optional**. DevCommit will work with just environment variables!
