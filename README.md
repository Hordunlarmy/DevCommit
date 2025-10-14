# DevCommit

A command-line AI tool for autocommits.

## Features

- 🤖 **Multi-AI Provider Support** - Choose from Gemini, Groq, OpenAI, Claude, Ollama, or custom APIs
- 🚀 Automatic commit generation using AI
- 📁 Directory-based commits - create separate commits for each root directory
- 🎯 Interactive mode to choose between global or directory-based commits
- ⚙️ Flexible configuration - use environment variables or .dcommit file
- 🏠 Self-hosted model support - use your own AI infrastructure
- 🆓 Multiple free tier options available

![DevCommit Demo](https://i.imgur.com/erPaZjc.png)

## Installation

1. **Install DevCommit**  
   
   **Option 1: Using pip (local installation)**
   ```bash
   pip install devcommit
   ```
   
   **Option 2: Using pipx (global installation, recommended)**
   ```bash
   # Install pipx if you don't have it
   python3 -m pip install --user pipx
   python3 -m pipx ensurepath
   
   # Install DevCommit globally
   pipx install devcommit
   ```
   > **💡 Why pipx?** pipx installs CLI tools in isolated environments, preventing dependency conflicts while making them globally available.
   
   **All AI providers are included by default!** ✅ Gemini, OpenAI, Groq, Anthropic, Ollama, and Custom API support.

2. **Set Up Configuration (Required: API Key)**  
   DevCommit requires an API key for your chosen AI provider. You can configure it using **any** of these methods:

   **Priority Order:** `.dcommit` file → Environment Variables → Defaults

   ### Option 1: Environment Variables (Quickest)
   ```bash
   # Using Gemini (default)
   export GEMINI_API_KEY='your-api-key-here'
   
   # Or using Groq (recommended for free tier)
   export AI_PROVIDER='groq'
   export GROQ_API_KEY='your-groq-key'
   
   # Add to ~/.bashrc or ~/.zshrc for persistence
   echo "export GEMINI_API_KEY='your-key'" >> ~/.bashrc
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

## AI Provider Support

DevCommit now supports **multiple AI providers**! Choose from:

| Provider | Free Tier | Speed | Quality | Get API Key |
|----------|-----------|-------|---------|-------------|
| 🆓 **Gemini** | 15 req/min, 1M/day | Fast | Good | [Get Key](https://aistudio.google.com/app/apikey) |
| ⚡ **Groq** | Very generous | **Fastest** | Good | [Get Key](https://console.groq.com/keys) |
| 🤖 **OpenAI** | $5 trial | Medium | **Best** | [Get Key](https://platform.openai.com/api-keys) |
| 🧠 **Anthropic** | Limited trial | Medium | Excellent | [Get Key](https://console.anthropic.com/) |
| 🏠 **Ollama** | **Unlimited** | Medium | Good | [Install](https://ollama.ai/) |
| 🔧 **Custom** | Varies | Varies | Varies | Your server |

### Quick Setup Examples

**Using Groq (Recommended for free tier):**
```bash
export AI_PROVIDER=groq
export GROQ_API_KEY='your-groq-api-key'
devcommit
```

**Using Ollama (Local, no API key needed):**
```bash
# Install Ollama: https://ollama.ai/
ollama pull llama3
export AI_PROVIDER=ollama
devcommit
```

**Using Custom API:**
```bash
export AI_PROVIDER=custom
export CUSTOM_API_URL='http://localhost:8000/v1'
export CUSTOM_API_KEY='your-key'
export CUSTOM_MODEL='your-model'
devcommit
```

## Configuration Reference

All configuration can be set via **environment variables** or **`.dcommit` file**:

### AI Provider Settings

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `AI_PROVIDER` | Which AI service to use | `gemini` | `gemini`, `openai`, `groq`, `anthropic`, `ollama`, `custom` |

### Provider-Specific Settings

**Gemini:**
| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `GEMINI_MODEL` | Model name | `gemini-1.5-flash` |

**OpenAI:**
| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_MODEL` | Model name | `gpt-4o-mini` |

**Groq:**
| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key ([Get it here](https://console.groq.com/)) | - |
| `GROQ_MODEL` | Model name | `llama-3.3-70b-versatile` |

**Anthropic:**
| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `ANTHROPIC_MODEL` | Model name | `claude-3-haiku-20240307` |

**Ollama (Local):**
| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model name | `llama3` |

**Custom (OpenAI-compatible):**
| Variable | Description | Default |
|----------|-------------|---------|
| `CUSTOM_API_URL` | API endpoint URL | - |
| `CUSTOM_API_KEY` | API key (optional) | - |
| `CUSTOM_MODEL` | Model name | `default` |

### General Settings

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `LOCALE` | Language for commit messages | `en-US` | Any locale code (e.g., `en`, `es`, `fr`) |
| `MAX_NO` | Number of commit message suggestions | `1` | Any positive integer |
| `COMMIT_TYPE` | Style of commit messages | `general` | `general`, `conventional`, etc. |
| `COMMIT_MODE` | Default commit strategy | `auto` | `auto`, `directory`, `global` |
| `EXCLUDE_FILES` | Files to exclude from diff | `package-lock.json, pnpm-lock.yaml, yarn.lock, *.lock` | Comma-separated file patterns |
| `MAX_TOKENS` | Maximum tokens for AI response | `8192` | Any positive integer |

### Configuration Priority
1. **`.dcommit` file** (highest priority)
2. **Environment variables**
3. **Built-in defaults** (lowest priority)

### Using Environment Variables
```bash
# Basic setup with Gemini (default)
export GEMINI_API_KEY='your-api-key-here'
export COMMIT_MODE='directory'
export COMMIT_TYPE='conventional'

# Or use Groq (faster, free)
export AI_PROVIDER='groq'
export GROQ_API_KEY='your-groq-key'

# Add to ~/.bashrc for persistence
```

### Using .dcommit File
See `.dcommit.example` for a complete configuration template with all providers.

**Note:** The `.dcommit` file is **optional**. DevCommit will work with just environment variables!
