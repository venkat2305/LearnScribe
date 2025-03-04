## TO DO
- for sending audio to gemini, we can send multiple audio files, we input to the function could be list of audio fils and we send all of them. this might help if we have to truncate the audio. 
- multiple article sources, multiple video sources.
- refactor so that quiz getter is a function in util/quiz.py and it will generate the quiz with all the conditions.
- we are using different models and hosting providers, we need to have them all at once for maintainability
- let's put json structure at a common place to make it reusable
- swagger login is not working fix it. 
- after creating quiz of a youtube video, delete the file.
- 307 Temporary Redirect why are we getting this when we make an api call
- use groq to get responses faster.
- we would use various models, providers for different things, can we manage all of that in a single place or what? how do we handle this? 
- probably use openai client for all, im using groq, google-genai clients.
- at the end, give all the code and compare requirements.txt file, does it has unnecessary packages or not. remove if found.
- we can build a dynamic system, where in for shorter input token count, we will use groq for faster generation and for larger contexts lets use gemini model. 
- let's store input tokens, output tokens and the model and the service in metadata, so we can get proper stats on total tokens used for a particular model.
- when extracting text from a url, we might also need to get the images in that page and feed all the text and the images to ai model to get the response. 
- we probably need to handle response formats, like application/json or markdown or text. for quiz, we need application/json, for summary, we would need to store markdown.
- lets configure the ai functions in such a way that, we can chat with youtbe/article/text or summarize with various templates or generate quizzes. 
- for summary, TLDR. lets get various templates.
- subject wise summaries/quiz grouping
- handwritten notes to text notes. 
- lets store youtube transcripts, article transcripts, 
- for quiz answer explanations, we have to give explanations for say if two choices may appear correct to the user but one of them is wrong, we have to give that explanation to that user. 



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
- The OAuth2PasswordBearer is a dependency that expects an endpoint (tokenUrl) where it will send credentials to get an access token.
- This means that when FastAPI's Swagger UI (or any client) tried to authenticate, it made a POST request to /auth/token to get a token.
How This Works in Swagger UI
When you try to log in using Swagger UI’s "Authorize" button:
1. Swagger UI sends a POST request to the tokenUrl (previously wrong, now corrected).
2. It includes form data (username and password).
3. Your login function processes the credentials and returns an access token.
4. Swagger UI uses the returned token for subsequent API requests.
- Ensure tokenUrl in OAuth2PasswordBearer matches the actual login endpoint.
- OAuth2PasswordBearer only defines where credentials should be sent—it doesn't handle authentication logic itself.
- 



- jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) decodes the JWT token.

- `deprecated="auto"` automatically updates passwords hashed with older algorithms to newer, more secure ones upon verification. after rehashing a password, you must store the new hash in the database



AttributeError in Python
An AttributeError is a common Python exception that occurs when you try to access or modify an attribute that doesn't exist on an object.

Common causes:
Trying to access a method or property that doesn't exist
Misspelling an attribute name
Using a None value and trying to access attributes on it
Using an object of the wrong type
