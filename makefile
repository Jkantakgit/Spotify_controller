#color codes
GREEN := \033[1;32m
YELLOW := \033[1;33m
NC := \033[0m


.PHONY: all run

all:
	@echo "$(GREEN)Running program$(NC)"
	.\main.pyw