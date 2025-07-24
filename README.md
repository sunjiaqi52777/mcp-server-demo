### venv
永久设定python环境： $env:UV_PYTHON = "C:\Users\JiaQiSun\AppData\Local\Programs\Python\Python313\python.exe"

```
uv venv .venv
.venv\Scripts\activate
uv pip install -e.
```
或者
```
uv run main.py
```
### MCP Inspector Command
```
npx -y @modelcontextprotocol/inspector
```
Command: python
Args: main.py