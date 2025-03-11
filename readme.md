## TO DO
High
- qa, we can manually add questions, generate answers for it and store it in our db. folders for a topic. we can manually add questions and answers as well in a folder. markdown note editor. 
- 307 Temporary Redirect why are we getting this when we make an api call
- for manual quiz generation we can use groq.
- setup backend url in frontend properly, for local and prod.
- read about redux-toolkit, how does it work. can we have two stores in a single application
- ngnix.conf for docker
- edit summary
- do proper indexing, for date desc index.
- sidebar more maintainable, like we should make it from an array. 
- we have to make sure the options are difficult. like, it shouldn't be like odd one out, somewhat similar somewhat tricky.
- and correct choice should be jumbled in order
- remove quiz topic for yt. check all fields input, remove unnecessary.
- number of questions is wrong in my quizzes page. 
- handle multiple quiz results for a single quiz if the user attempted multiple times. 
- add CORS middleware to enable cross-origin requests. needed to send cookies to the server : is this true? 
- seperate rapid api keys for prod and stage. 
- change favicon
- default number of questions, default prompt, etc we can store in settings via redux and store it in users, we can send them with quiz creation request.
- remove access token from local and put it in memory only.
- generate strctured notes for all the wrong answered questions for that quiz.
- llama-3.2-90b-vision-preview use it for images.
- after sometime, it automatically logging out and if we open `https://learn-scribe-seven.vercel.app/login` directly, we get
404: NOT_FOUND
Code: NOT_FOUND
ID: bom1::78lzm-1741459500931-9941ec04b3bf

but if we open `https://learn-scribe-seven.vercel.app`, it goes to login page(above url only) and then we can login.

Medium
- we are using different models and hosting providers, we need to have them all at one place for easier maintainability
- let's put json structure at a common place to make it reusable
- lets store youtube transcripts, article transcripts
- google signin
- talk to youtube vid, article and store that conversation thread.
- for summary, TLDR. lets get various templates.
- different providers, different model id's, different functions, we have to handle all of these. 
- re-enable ts checking package.json : // "build": "tsc -b && vite build",
- create explanations, for wrong answered questions for a quiz or a lot of wrong answered questions in a strcutured way with examples. a proper notes and then be able to generate quiz from it.

Low

Done
- store refresh token in http cookie and token in session storage.
- after creating quiz of a youtube video, delete the file.


All
- for sending audio to gemini, we can send multiple audio files, we input to the function could be list of audio files and we send all of them. this might help if we have to truncate the audio. 
- multiple article sources, multiple video sources.
- refactor so that quiz getter is a function in util/quiz.py and it will generate the quiz with all the conditions.



- probably use openai client for all, im using groq, google-genai clients.
- at the end, give all the code and compare requirements.txt file, does it has unnecessary packages or not. remove if found.
- we can build a dynamic system, where in for shorter input token count, we will use groq for faster generation and for larger contexts lets use gemini model.

- when extracting text from a url, we might also need to get the images in that page and feed all the text and the images to ai model to get the response. 
- we probably need to handle response formats, like application/json or markdown or text. for quiz, we need application/json, for summary, we would need to store markdown.
- lets configure the ai functions in such a way that, we can chat with youtbe/article/text or summarize with various templates or generate quizzes. 

- subject wise summaries/quiz grouping. folders
- handwritten notes to text structured notes.

- for quiz answer explanations, we have to give explanations for say if two choices may appear correct to the user but one of them is wrong, we have to give that explanation to that user.
- handle secure authentication flow


- PDF/Document Scanner – Extract text from PDFs/images using OCR (Tesseract).
- definitely upload images/pdfs to R2 object storage.
- Reads long articles and extracts key insights.
- Lets users organize and tag notes for later use.
- we can have an account page, where we will have something about the user info like mbbs student etc to get relevant answers. maybe
- notion integration.

- put the schmea of differnt things in a seperate folders etc and use them everywhere instead of putting them in each route file and util file etc. 

- after everything we can send frontend code to claude to make it responsive
- why quiz.types.ts
- is the overall code like a senior or garbage 
- what is overall architecture of the project, explain project structure, why did you put certain things in hooks, some in utils and some as services.
-typescript types, is it strict, what is good in the code and where and what can we improve. 




### cookie delete on logout
- The server sends a Set-Cookie header with the same cookie name but with an expired date after successful logout.
- The browser sees the cookie has expired and automatically deletes it.
- Since the cookie is deleted, it won’t be sent in future requests.


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


- In FastAPI, response.delete_cookie() is used to remove a cookie from the client's browser.
How it Works:
It sets the cookie's expiration time to the past.
The browser will then delete the cookie.
The cookie must match the domain and path where it was set.

What happens?
The "session_id" cookie is removed from the client.
The user may need to log in again.

FastAPI endpoint standard convetion.
- when you send a POST request to /quiz (without a trailing slash), FastAPI is configured to automatically redirect that request to /quiz/ (with a trailing slash). 
- Trailing slashes are a common convention for directories or collections of resources on the web. FastAPI encourages this for API consistency.
- SEO (Potentially): In some cases, search engines treat URLs with and without trailing slashes as different URLs. Using trailing slashes consistently can help avoid potential SEO issues (though this is less relevant for APIs).

#### cors error
The CORS error you're encountering arises because using allow_origins=["*"] with allow_credentials=True is incompatible when credentials (like cookies or authorization headers) are involved
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Replace the wildcard * with explicit frontend origins in your FastAPI CORS configuration
The browser blocks requests when allow_origins is ["*"] and credentials are enabled.

Security Restriction: Browsers block wildcard (*) origins with credentials to prevent cross-origin attacks