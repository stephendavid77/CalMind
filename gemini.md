# **Gemini Python Code Guidelines**

These guidelines ensure **clean, maintainable, and resilient Python code** that follows industry best practices.

---

## **1. Design & Architecture**
- Follow the **SOLID principles** for modular, extensible, and testable design.  
- Each **unique feature** should be implemented as a **separate class**.  
- Each **distinct functionality** within a feature should be a **separate method**.  
- Use **dependency injection** or configuration-driven patterns to reduce coupling.  
- Prefer **dataclasses** or **pydantic models** for structured data handling.  

---

## **2. Logging & Monitoring**
- Use the **`logging` module**, not `print`, for all logs.  
- Include enough context to debug issues easily.  
- Logs should:
  - Mark **start and end** of major operations.  
  - Include **identifiers** for jobs, users, or transactions when applicable.  
  - Use **structured messages** for consistent parsing.

### **Logging Levels**
| Level   | Purpose |
|----------|-----------------------------------|
| DEBUG    | Detailed information for development. |
| INFO     | General operational messages. |
| WARNING  | Recoverable issues or unusual states. |
| ERROR    | Non-recoverable issues needing attention. |
| CRITICAL | System-wide failures requiring immediate action. |

### **Logging Example**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info("Starting data processing...")
    try:
        if not data:
            raise ValueError("Data input is empty")
        logger.debug(f"Processing {len(data)} items")
        # Processing logic here
        logger.info("Data processing completed successfully.")
    except ValueError as e:
        logger.error(f"Validation failed: {e}")
    except Exception:
        logger.exception("Unexpected error during data processing")
```

---

## **3. Web Application Development**
- Use **FastAPI** for building efficient and scalable backend APIs.
- Use **React** with **Bootstrap** for creating responsive and mobile-friendly user interfaces.
- Follow a **component-based architecture** in React for reusability and maintainability.
- Use **axios** for making API requests from the frontend.
- Implement **asynchronous task processing** for long-running operations using `FastAPI.BackgroundTasks` or a dedicated task queue like Celery.

---

## **4. Containerization with Docker**
- Use a **multi-stage `Dockerfile`** to create optimized and secure container images.
- Build the frontend and backend in separate stages to keep the final image small.
- Use **`docker-compose`** to manage multi-service applications.
- Define clear and consistent naming conventions for services, containers, and networks.
