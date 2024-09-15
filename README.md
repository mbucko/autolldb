# Autolldb
This tool will attempt to debug your coredump autonomously and provide an summary of the bug, as well as a patch to fix it.

## Requirements
```bash
 xcrun python3 -m pip install openai cpython-lldb

```
Also need perplexity API key.

 ## Setup python env 
 ```bash
 source setup_env.sh
 ```

 ## Run Autolldb
 ```python
 xcrun python3 ./autolldb.py --api-key="pplx-123456789"  -e "/Path/to/executable" -c "/Path/to/executable.core" -s "/Path/to/sources/"
 ```