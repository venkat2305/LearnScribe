## learnings

### config.py
They’re relying on Pydantic’s BaseSettings to automatically read environment variables into the class attributes. Once load_dotenv() populates the process environment, Pydantic will match each attribute with its corresponding environment variable name and load those values directly into the Settings class. This way, there’s no need for explicit os.getenv() calls in the code.




### mongodb.py
Why you'd choose `motor.motor_asyncio.AsyncIOMotorClient` over `pymongo.MongoClient`, especially with FastAPI:

**Why Async (AsyncIOMotorClient)?**

*   **Concurrency & Responsiveness:** Synchronous clients block, making your app slow under load. Async clients handle multiple requests concurrently, improving performance.
    *   *Example:* With 10 simultaneous users, an async client handles them concurrently, while a synchronous client makes them wait in line.
*   **I/O Bound:** Database operations are I/O bound, perfect for async.
*   **FastAPI Integration:** AsyncIOMotorClient leverages FastAPI's async capabilities for optimal performance.

**Why Not Synchronous (MongoClient)?**

*   Using `pymongo.MongoClient` with FastAPI forces operations into separate threads, adding overhead.

**Summary:**

*   `pymongo.MongoClient` (Synchronous): Simple, but blocks. Fine for basic scripts.
*   `motor.motor_asyncio.AsyncIOMotorClient` (Asynchronous): Complex initially, but high performance for concurrent web apps like those built with FastAPI.

### docker-compose.yml
1️⃣ Understanding ports: "8000:8000"
Format: host_port:container_port
Example: "8001:8000" → Access http://localhost:8001, which maps to 8000 inside the container.
Effect: Allows external access to the FastAPI app.

2️⃣ Dockerfile vs. command in docker-compose.yml
Dockerfile builds the image, but command in docker-compose.yml overrides the default command inside the container.
Example:
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] in Dockerfile
If command: is set in docker-compose.yml, it takes priority.


### auth.py
- FastAPI uses OAuth2PasswordBearer to extract the token from the Authorization header. It is typically used for Bearer token authentication.
passlib.context.CryptContext is used for hashing passwords and verifying them.
- The code makes use of asynchronous database calls (await db.users.find_one) to ensure non-blocking interactions with the database. This helps improve the performance of the application when dealing with I/O-bound tasks.

- jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) decodes the JWT token.

- `deprecated="auto"` automatically updates passwords hashed with older algorithms to newer, more secure ones upon verification. after rehashing a password, you must store the new hash in the database
