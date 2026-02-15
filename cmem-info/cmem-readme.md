🧠 cmem
Self-Learning Memory for Claude Code
Never lose a conversation. Claude learns from every session.

Semantic search • Auto-synthesis • Knowledge injection • Web GUI • 100% local

License: MIT Node.js


Get Started
npx @colbymchenry/cmem
Interactive installer configures Claude Code automatically

Stop Writing Markdown Files
Everyone tries to solve Claude's memory problem the same way: manually writing markdown files. CLAUDE.md, ARCHITECTURE.md, decision logs, convention docs...

It's tedious. It's incomplete. And you forget to update them.

cmem takes a different approach. Instead of you documenting everything, cmem watches your conversations and automatically extracts the knowledge Claude needs. Architecture decisions, bug patterns, project conventions, anti-patterns—all captured naturally as you work.

Think of it like giving Claude a notebook for each project. Every conversation adds notes. When Claude needs to answer a question, it semantically searches this organized, efficient knowledge base—finding exactly the right context without you lifting a finger.

Traditional approach: You manually write docs → Claude reads them → Docs aren't detailed enough so Claude explores anyway → You forget to update → Outdated docs lead to bad suggestions

cmem approach: You just code → cmem learns from every session → Knowledge stays current and detailed → Claude gives informed answers instantly

What is cmem?
cmem is a self-learning memory system for Claude Code. It:

Backs up every conversation — Never lose work, even if Claude clears storage
Learns from your sessions — Auto-extracts lessons about your projects
Injects relevant knowledge — Claude starts each conversation with context about your codebase
Searches your history — Find past conversations by meaning, not keywords
Rename and favorite sessions - Never lose those valuable sessions between you and Claude
View all sessions by project - Organized chat sessions by what project you were working on
Web GUI — Manage learned knowledge through a beautiful interface
MCP Integration
Using CMEM MCP to fetch conversational data about previous chat sessions

Claude can search through your conversation history and synthesize answers—all without cluttering your main session context.

Query All Conversational History

Session Navigation
Easily navigate between previous chat sessions and pick back up right where you left off

Browse, search, filter, rename, and restore any conversation with the interactive TUI.

Filter by Folder : Rename : Resume Sessions

Open all previous chat sessions in current directory
Open all sessions in current directory

Web GUI
Manage your learned knowledge through a clean web interface.

GUI

cmem gui
Features:

Browse all lessons by project and category
Edit, archive, or delete lessons
View confidence scores and usage stats
Create lessons manually
Filter by category (architecture, bugs, conventions, etc.)
Features
📚 Self-Learning Knowledge Base
cmem automatically extracts reusable lessons from your conversations:

Architecture decisions and their rationale
Anti-patterns — what NOT to do and why
Bug patterns — common issues and root causes
Project conventions — code style, naming, organization
Dependency knowledge — library quirks, version issues
Domain knowledge — business logic, requirements
PNG image

These lessons are automatically surfaced when relevant to your current task

🔍 Semantic Search
Find conversations by meaning, not keywords. "That React hooks discussion" or "the database migration plan" just works.

🤖 Claude Remembers
Via MCP integration, Claude can search your past conversations and learned knowledge:

"What did we decide about auth last week?"
"How do we handle errors in this project?"
"What's the convention for API endpoints?"
💾 Automatic Backup
Every conversation is backed up to ~/.cmem/backups/. Even if Claude Code clears its storage, cmem restores your sessions instantly.

🪝 Hook-Based Integration
cmem integrates with Claude Code via hooks (no background daemon):

UserPromptSubmit — Injects relevant lessons before Claude responds
Stop/PreCompact — Syncs and backs up sessions automatically
📦 100% Local & Private
Everything runs on your machine:

SQLite database with vector embeddings
Local AI embeddings (nomic-embed-text-v1.5)
No cloud services, no API keys required
Quick Start
npx @colbymchenry/cmem
The setup wizard will:

Install cmem globally
Download the embedding model (~130MB, one-time)
Configure MCP server in Claude Code
Set up hooks for automatic sync and learning
Clean up any old daemon from previous versions
Upgrading? Just run the same command — it handles everything automatically.

Requirements
Node.js 18+
Claude Code CLI (for synthesis features)
Usage
cmem                    # Browse sessions in beautiful TUI
cmem --local            # Browse sessions from current folder only
cmem gui                # Launch web-based lesson management UI
cmem stats              # See what's stored
MCP Tools
Claude Code gains these abilities:

Tool	Description
search_and_summarize	AI-synthesized answers from past sessions
search_sessions	Find sessions by semantic similarity
search_lessons	Find learned knowledge for current project
save_lesson	Manually save important knowledge
validate_lesson	Mark a lesson as helpful (boosts confidence)
reject_lesson	Mark a lesson as wrong (reduces confidence)
list_lessons	Browse all lessons for a project
list_sessions	Browse recent sessions
get_session	Retrieve full conversation history
How It Works
Knowledge Injection (Hooks)
When you send a prompt to Claude:

UserPromptSubmit hook triggers
cmem searches for relevant lessons
Matching lessons are injected as <project_knowledge>
Claude sees this context before responding
Session Sync (Hooks)
When a session ends or compacts:

Stop/PreCompact hook triggers
cmem parses and indexes the session
Session is backed up to ~/.cmem/backups/
Session is queued for lesson extraction
Lesson Synthesis
Sessions in the queue are processed by the synthesis engine:

cmem synthesize        # Process pending sessions
cmem synthesize -s     # Show queue status
The synthesis engine uses Claude (via CLI) to analyze sessions and extract reusable lessons.

Lesson Confidence System
Each lesson has a confidence score (0-100%):

Synthesized lessons start at 30-70% based on evidence
Manual lessons start at 60%
Validation boosts confidence by 10%
Rejection reduces confidence by 20%
Very low confidence lessons are auto-archived
Unused lessons decay over time
TUI Keyboard Shortcuts
Key	Action
←/→ or h/l	Switch tabs (Global / Projects)
↑/↓ or j/k	Navigate
Enter	Resume session / Open project
s	Star session (Global) / Sort mode (Projects)
r	Rename session
R	Clear custom name
d	Delete session
/	Search (Global tab)
Esc	Back / Cancel
q	Quit
Data Storage
All data is stored locally in ~/.cmem/:

~/.cmem/
├── sessions.db      # SQLite database (sessions, lessons, embeddings)
├── models/          # Downloaded embedding model (~130MB)
└── backups/         # Full copies of all conversation JSONLs
Plugin Architecture
cmem is designed as a Claude Code plugin:

.claude-plugin/
├── plugin.json      # Plugin manifest
commands/
├── cmem.md          # /cmem slash command
skills/
└── memory-search/
    └── SKILL.md     # Memory search skill
hooks/
└── hooks.json       # UserPromptSubmit, Stop, PreCompact hooks
.mcp.json            # MCP server configuration
Tech Stack
SQLite + sqlite-vec — Embedded vector database
transformers.js + nomic-embed-text-v1.5 — Local AI embeddings
ink — Beautiful terminal UI (React for CLI)
React + Vite + Tailwind — Web GUI
MCP — Model Context Protocol for Claude integration
Claude Code Hooks — Event-driven integration (no daemon)
Upgrading from Previous Versions
If you're upgrading from a version that used the background daemon:

npx @colbymchenry/cmem
The setup wizard will:

Automatically stop and remove the old daemon
Configure the new hook-based system
Your existing sessions and data are preserved
License
MIT