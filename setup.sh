#!/bin/bash
# Download models and create required directories
mkdir -p storage/uploads storage/jobs storage/output
python scripts/download_models.py
