# Stack

Here’s a clean, practical tech stack for **el**, aligned with how backend tools and local agents are built today.
Lightweight, reliable, no unnecessary bloat.

### **Core Language**

- **Python 3.12+**
  Good subprocess control, fast prototyping, strong ecosystem.

---

### **System Interaction**

These are the libraries you actually need:

1. **subprocess (std lib)**
   For running commands safely.

2. **psutil**
   - Process inspection
   - CPU/mem info
   - Ports, network connections
     This becomes essential when you build deeper system introspection.

3. **rich** _(or just plain output)_
   For pretty CLI formatting if you want clean tables/logs.
   You can skip it if you prefer minimal output.

---

### **Data & Models**

4. **pydantic**
   For standardized request/response models between skills.
   Keeps interfaces clean.

5. **sqlite3 (std lib)**
   For persistent local state (system index, knowledge, caches).

---

### **Local LLM Runtime**

6. **Ollama**
   Your model runner.
   Integrate via:
   - HTTP API
   - or a lightweight Python wrapper

---

### **Agent Reasoning Layer**

7. **Guidance / simple custom agent loop** _(optional)_
   You _don’t_ need a framework.
   You only need:
   - take user text
   - send to model
   - parse intent
   - dispatch skill
   - return structured result

You can completely avoid heavy agent frameworks like LangChain — unnecessary and restrictive for local system agents.

---

### **Future Extensions (only if needed)**

- **textual** → if you want a full terminal UI later
- **yaml** → config descriptors for skills
- **docker / lxc python drivers** → for container orchestration when you reach that stage

---

### **What You _Don’t_ Need**

- No heavy frameworks
- No web servers
- No async frameworks unless you later add concurrency
- No external databases

Keep it small → fast → secure → local.

---

If you want, the next step is:
**I’ll define exactly which modules import which libs, so the architecture stays clean and modular from day one.**
