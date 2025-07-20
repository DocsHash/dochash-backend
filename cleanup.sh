#!/bin/bash
# Remove old files that are no longer needed

# Old service files
rm -f app/services/blockchain_service.py
rm -f app/services/blockchain_worker.py
rm -f app/services/document_processor.py

# Old model and handler files
rm -f app/models.py
rm -f app/api_handlers.py

# Remove empty directories
rmdir app/services 2>/dev/null || true

echo "Cleanup completed"
